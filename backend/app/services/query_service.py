"""Query service: Natural language to SQL conversion"""
from typing import Dict, Any
from app.core.llm import LLMClient
from app.core.security import SQLValidator
from app.utils.schema_parser import build_schema_context, get_table_names


class QueryService:
    """Service for converting natural language to SQL"""
    
    def __init__(self):
        self.llm = LLMClient()
    
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
        
        prompt = f"""You are an expert SQL query generator. Convert the following natural language query to SQL.

User Query: "{user_query}"

Database Schema:
{schema_context}

Rules:
1. Only generate SELECT queries (read-only operations)
2. Use proper SQL syntax for SQLite
3. Include appropriate WHERE, GROUP BY, ORDER BY clauses when needed
4. Use aggregate functions (SUM, COUNT, AVG, MAX, MIN) when appropriate
5. **CRITICAL: Generate ONLY ONE SELECT statement. Do not include multiple statements separated by semicolons.**
6. Return valid JSON with the following structure:
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
        
        try:
            response = await self.llm.generate_json(messages, temperature=0.3)
            
            sql = response.get("sql", "").strip()
            intent = response.get("intent", {})
            
            # Validate SQL
            is_valid, error_msg = SQLValidator.validate_sql(sql, table_names)
            
            if not is_valid:
                raise ValueError(f"Generated SQL is invalid: {error_msg}")
            
            # Sanitize SQL
            sql = SQLValidator.sanitize_sql(sql)
            
            return {
                "sql": sql,
                "intent": intent
            }
        except Exception as e:
            raise Exception(f"Failed to generate SQL: {str(e)}")

