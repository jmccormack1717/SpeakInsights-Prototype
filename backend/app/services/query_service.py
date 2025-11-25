"""Query service: Natural language to SQL conversion"""
import logging
from typing import Dict, Any
from app.core.llm import LLMClient
from app.core.security import SQLValidator
from app.utils.schema_parser import build_schema_context, get_table_names


class QueryService:
    """Service for converting natural language to SQL"""
    
    def __init__(self):
        self.llm = LLMClient()
        self.logger = logging.getLogger(__name__)
    
    async def generate_sql(
        self,
        user_query: str,
        schema_info: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Convert natural language query to SQL
        
        Args:
            user_query: User's natural language query
            schema_info: Database schema information
            
        Returns:
            Dict with 'sql' and 'intent' keys
        """
        schema_context = build_schema_context(schema_info)
        table_names = get_table_names(schema_info)

        # Detect common "describe/overview" style questions
        lower_query = user_query.lower()
        overview_keywords = [
            "describe the dataset",
            "describe dataset",
            "dataset overview",
            "overview of the dataset",
            "what is in this dataset",
            "what does this dataset contain",
            "describe the data",
            "data overview",
        ]
        is_overview_query = any(k in lower_query for k in overview_keywords)

        # Detect correlation / collinearity style questions
        correlation_keywords = [
            "correlation",
            "correlated",
            "correlate",
            "collinearity",
            "colinear",
            "most related to",
            "related to outcome",
        ]
        is_correlation_query = any(k in lower_query for k in correlation_keywords)
        
        # For schema-related queries, provide better guidance
        schema_query_keywords = ['feature', 'column', 'field', 'attribute', 'schema', 'structure', 'what data', 'what information']
        is_schema_query = any(keyword in lower_query for keyword in schema_query_keywords)
        
        schema_guidance = ""
        if is_schema_query and table_names:
            # Provide example of how to query schema in SQLite
            table_name = table_names[0]  # Use first table
            schema_guidance = f"""
IMPORTANT: For queries about columns/features/schema, use SQLite's PRAGMA:
Example: SELECT name FROM pragma_table_info('{table_name}')
This is the SQLite-compatible way to list columns. DO NOT use FROM (VALUES ...).
"""
        
        prompt = f"""You are an expert SQL query generator for SQLite. Convert the following natural language query to SQL.

User Query: "{user_query}"

Database Schema:
{schema_context}
{schema_guidance}
Rules:
1. Only generate SELECT queries (read-only operations)
2. **CRITICAL: Use SQLite-compatible syntax only. SQLite does NOT support:**
   - `FROM (VALUES ...)` syntax (PostgreSQL/MySQL syntax)
   - Common Table Expressions (CTEs) in older SQLite versions
   - Some advanced window functions
3. **For listing columns/features:** Use `PRAGMA table_info(table_name)` or query actual table data, NOT `FROM (VALUES ...)`
4. **Always query from actual tables in the schema above.** Do not create temporary tables or use VALUES clauses.
5. Include appropriate WHERE, GROUP BY, ORDER BY clauses when needed
6. Use aggregate functions (SUM, COUNT, AVG, MAX, MIN) when appropriate
7. **CRITICAL: Generate ONLY ONE SELECT statement. Do not include multiple statements separated by semicolons.**
8. Return valid JSON with the following structure:
   {{
     "sql": "SELECT ...",
     "intent": {{
       "primary_intent": "trend|comparison|distribution|correlation|part_to_whole|table",
       "grouping": "column_name or null",
       "time_filter": "time dimension if present or null",
       "aggregation": "sum|avg|count|max|min or null",
       "explicit_chart_type": "chart type if user requested specific chart or null"
     }}
   }}

Examples of CORRECT SQLite syntax for common queries:
- List all columns: `SELECT name FROM pragma_table_info('diabetes')`
- Get all data: `SELECT * FROM diabetes LIMIT 100`
- Count rows: `SELECT COUNT(*) FROM diabetes`
- Average value: `SELECT AVG(Glucose) FROM diabetes`
- Group by: `SELECT Outcome, COUNT(*) FROM diabetes GROUP BY Outcome`
- Filter: `SELECT * FROM diabetes WHERE Glucose > 100`
- Multiple columns: `SELECT Pregnancies, Glucose, Outcome FROM diabetes LIMIT 10`
- Distinct values: `SELECT DISTINCT Outcome FROM diabetes`
- Aggregations: `SELECT Outcome, AVG(Glucose), MAX(Glucose), MIN(Glucose) FROM diabetes GROUP BY Outcome`

Examples of INCORRECT syntax (DO NOT USE):
- `SELECT feature FROM (VALUES ('col1'), ('col2')) AS t(feature)` ❌ SQLite doesn't support VALUES in FROM
- `WITH temp AS (SELECT ...)` ❌ Avoid CTEs unless necessary (SQLite 3.8.3+)
- Multiple statements with semicolons ❌ Only one SELECT per query

IMPORTANT: 
- Always use actual table and column names from the schema above
- For "what features/columns" queries, use: `SELECT name FROM pragma_table_info('table_name')`
- Keep queries simple and SQLite-compatible
- Test your SQL mentally: would it work in SQLite?

Generate the SQL query and intent analysis:"""

        messages = [
            {
                "role": "system",
                "content": "You are a SQL expert that converts natural language to SQL queries. Always return valid JSON."
            },
            {
                "role": "user",
                "content": prompt
            }
        ]
        
        # Retry mechanism with feedback
        max_retries = 2
        last_error = None
        
        for attempt in range(max_retries + 1):
            try:
                # Add feedback from previous attempt if retrying
                if attempt > 0 and last_error:
                    feedback_prompt = f"""
Previous attempt failed with error: {last_error}

Please fix the SQL query. Common issues:
- SQLite does NOT support: FROM (VALUES ...), CTEs in older versions
- Use actual table names from the schema
- For column listings: SELECT name FROM pragma_table_info('table_name')
- Only one SELECT statement, no semicolons

Generate a corrected SQL query:"""
                    messages.append({
                        "role": "user",
                        "content": feedback_prompt
                    })
                
                response = await self.llm.generate_json(messages, temperature=0.3)
                
                sql = response.get("sql", "").strip()
                intent = response.get("intent", {}) or {}

                primary_intent = intent.get("primary_intent", "").lower()

                # If user clearly asked about correlation but LLM didn't label it, fix the intent
                if is_correlation_query and primary_intent != "correlation":
                    primary_intent = "correlation"
                    intent["primary_intent"] = "correlation"

                # If this is a correlation-style question, override SQL to use the full dataset
                if primary_intent == "correlation" and table_names:
                    base_table = table_names[0]
                    sql = f"SELECT * FROM {base_table}"

                # If this is an overview/describe-dataset question, also use a simple full-table sample
                if is_overview_query and table_names:
                    base_table = table_names[0]
                    # Limit for performance, but enough rows for good stats
                    sql = f"SELECT * FROM {base_table} LIMIT 500"
                    intent["primary_intent"] = intent.get("primary_intent") or "overview"
                
                if not sql:
                    raise ValueError("No SQL generated in response")
                
                # Validate SQL
                is_valid, error_msg = SQLValidator.validate_sql(sql, table_names)
                
                if not is_valid:
                    last_error = error_msg
                    if attempt < max_retries:
                        self.logger.warning(f"SQL validation failed (attempt {attempt + 1}/{max_retries + 1}): {error_msg}. Retrying...")
                        continue
                    else:
                        raise ValueError(f"Generated SQL is invalid after {max_retries + 1} attempts: {error_msg}")
                
                # Sanitize SQL
                sql = SQLValidator.sanitize_sql(sql)
                
                return {
                    "sql": sql,
                    "intent": intent
                }
                
            except Exception as e:
                last_error = str(e)
                if attempt < max_retries:
                    self.logger.warning(f"SQL generation failed (attempt {attempt + 1}/{max_retries + 1}): {str(e)}. Retrying...")
                    continue
                else:
                    raise Exception(f"Failed to generate valid SQL after {max_retries + 1} attempts: {str(e)}")

