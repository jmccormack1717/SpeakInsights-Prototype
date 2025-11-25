"""SQL query validation and security"""
import re
from typing import Tuple, List
from sqlalchemy import text


class SQLValidator:
    """Validates and sanitizes SQL queries"""
    
    # Dangerous SQL keywords that should be blocked
    DANGEROUS_KEYWORDS = [
        'DROP', 'DELETE', 'TRUNCATE', 'ALTER', 'CREATE', 'INSERT',
        'UPDATE', 'EXEC', 'EXECUTE', 'GRANT', 'REVOKE', 'MERGE'
    ]
    
    # Allowed SQL keywords (read-only operations)
    ALLOWED_KEYWORDS = [
        'SELECT', 'FROM', 'WHERE', 'GROUP BY', 'ORDER BY', 'HAVING',
        'JOIN', 'INNER JOIN', 'LEFT JOIN', 'RIGHT JOIN', 'FULL JOIN',
        'UNION', 'UNION ALL', 'LIMIT', 'OFFSET', 'AS', 'DISTINCT',
        'COUNT', 'SUM', 'AVG', 'MAX', 'MIN', 'CASE', 'WHEN', 'THEN',
        'AND', 'OR', 'NOT', 'IN', 'LIKE', 'BETWEEN', 'IS NULL', 'IS NOT NULL'
    ]
    
    @classmethod
    def validate_sql(cls, sql: str, allowed_tables: List[str] = None) -> Tuple[bool, str]:
        """
        Validate SQL query for safety
        
        Args:
            sql: SQL query to validate
            allowed_tables: List of allowed table names (optional)
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        sql_upper = sql.upper().strip()
        
        # Check for dangerous keywords
        for keyword in cls.DANGEROUS_KEYWORDS:
            # Use word boundaries to avoid false positives
            pattern = r'\b' + re.escape(keyword) + r'\b'
            if re.search(pattern, sql_upper):
                return False, f"Dangerous keyword '{keyword}' is not allowed. Only SELECT queries are permitted."
        
        # Must start with SELECT
        if not sql_upper.startswith('SELECT'):
            return False, "Only SELECT queries are allowed. Query must start with SELECT."
        
        # Check for table names if provided
        if allowed_tables:
            # Extract table names from FROM and JOIN clauses
            table_pattern = r'\bFROM\s+(\w+)|JOIN\s+(\w+)'
            matches = re.findall(table_pattern, sql_upper)
            found_tables = [m[0] or m[1] for m in matches if m[0] or m[1]]
            
            for table in found_tables:
                if table.upper() not in [t.upper() for t in allowed_tables]:
                    return False, f"Table '{table}' is not allowed or does not exist."
        
        # Basic syntax check - ensure balanced parentheses
        if sql.count('(') != sql.count(')'):
            return False, "Unbalanced parentheses in SQL query."
        
        return True, ""
    
    @classmethod
    def sanitize_sql(cls, sql: str) -> str:
        """
        Basic SQL sanitization (remove comments, normalize whitespace)
        
        Args:
            sql: SQL query to sanitize
            
        Returns:
            Sanitized SQL query
        """
        # Remove SQL comments
        sql = re.sub(r'--.*$', '', sql, flags=re.MULTILINE)
        sql = re.sub(r'/\*.*?\*/', '', sql, flags=re.DOTALL)
        
        # Normalize whitespace
        sql = ' '.join(sql.split())
        
        # Remove trailing semicolons
        sql = sql.rstrip(';')
        
        return sql.strip()

