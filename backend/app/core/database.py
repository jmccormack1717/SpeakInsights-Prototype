"""Database connection and management"""
import os
from pathlib import Path
from typing import Optional, Dict, Any, List
from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import sessionmaker
from app.config import settings


class DatabaseManager:
    """Manages database connections for users"""
    
    def __init__(self):
        self.connections: Dict[str, Any] = {}
        self.data_path = Path(settings.database_path)
        self.data_path.mkdir(parents=True, exist_ok=True)
    
    def get_database_path(self, user_id: str, dataset_id: str) -> Path:
        """Get path to user's database file"""
        user_dir = self.data_path / user_id
        user_dir.mkdir(parents=True, exist_ok=True)
        return user_dir / f"{dataset_id}.db"
    
    def get_connection_string(self, user_id: str, dataset_id: str) -> str:
        """Get SQLite connection string for user's database"""
        db_path = self.get_database_path(user_id, dataset_id)
        return f"sqlite+aiosqlite:///{db_path}"
    
    async def get_engine(self, user_id: str, dataset_id: str):
        """Get or create async engine for user's database"""
        cache_key = f"{user_id}:{dataset_id}"
        
        if cache_key not in self.connections:
            conn_str = self.get_connection_string(user_id, dataset_id)
            engine = create_async_engine(
                conn_str,
                echo=False,
                pool_pre_ping=True
            )
            self.connections[cache_key] = engine
        
        return self.connections[cache_key]
    
    async def execute_query(
        self,
        user_id: str,
        dataset_id: str,
        sql: str,
        timeout: int = 30
    ) -> List[Dict[str, Any]]:
        """
        Execute SQL query and return results
        
        Args:
            user_id: User identifier
            dataset_id: Dataset identifier
            sql: SQL query to execute
            timeout: Query timeout in seconds
            
        Returns:
            List of result rows as dictionaries
            
        Raises:
            FileNotFoundError: If database file doesn't exist
            Exception: For other database errors
        """
        db_path = self.get_database_path(user_id, dataset_id)
        
        # Check if database file exists
        if not db_path.exists():
            raise FileNotFoundError(
                f"Database file not found: {db_path}. "
                f"Please ensure the dataset '{dataset_id}' has been imported."
            )
        
        # Extract only the first statement if multiple are present
        # Split by semicolon and take the first non-empty statement
        statements = [s.strip() for s in sql.split(';') if s.strip()]
        if not statements:
            raise ValueError("No valid SQL statement found")
        
        # Use only the first statement
        sql = statements[0]
        
        engine = await self.get_engine(user_id, dataset_id)
        
        async with engine.begin() as conn:
            # Set timeout
            await conn.execute(text(f"PRAGMA busy_timeout = {timeout * 1000}"))
            
            # Execute query
            result = await conn.execute(text(sql))
            
            # Fetch results
            rows = result.fetchall()
            
            # Convert to list of dicts
            columns = result.keys()
            return [dict(zip(columns, row)) for row in rows]
    
    async def get_schema(self, user_id: str, dataset_id: str) -> Dict[str, Any]:
        """
        Get database schema information
        
        Args:
            user_id: User identifier
            dataset_id: Dataset identifier
            
        Returns:
            Schema information as dict
            
        Raises:
            FileNotFoundError: If database file doesn't exist
            Exception: For other database errors
        """
        db_path = self.get_database_path(user_id, dataset_id)
        
        # Check if database file exists
        if not db_path.exists():
            raise FileNotFoundError(
                f"Database file not found: {db_path}. "
                f"Please ensure the dataset '{dataset_id}' has been imported."
            )
        
        engine = await self.get_engine(user_id, dataset_id)
        
        schema_info = {
            "tables": []
        }
        
        # Get all table names using SQLite system tables
        async with engine.begin() as conn:
            # Query SQLite master table for table names
            result = await conn.execute(text("""
                SELECT name FROM sqlite_master 
                WHERE type='table' AND name NOT LIKE 'sqlite_%'
                ORDER BY name
            """))
            table_rows = result.fetchall()
            table_names = [row[0] for row in table_rows]
        
        for table_name in table_names:
            # Get column information using PRAGMA
            async with engine.begin() as conn:
                result = await conn.execute(text(f"PRAGMA table_info({table_name})"))
                column_rows = result.fetchall()
                
                table_info = {
                    "name": table_name,
                    "columns": []
                }
                
                for col_row in column_rows:
                    # PRAGMA table_info returns: cid, name, type, notnull, dflt_value, pk
                    col_name = col_row[1]
                    col_type = col_row[2]
                    not_null = col_row[3] == 1
                    
                    table_info["columns"].append({
                        "name": col_name,
                        "type": col_type,
                        "nullable": not not_null
                    })
                
                # Get sample data (first 3 rows)
                try:
                    sample_result = await conn.execute(
                        text(f"SELECT * FROM {table_name} LIMIT 3")
                    )
                    sample_rows = sample_result.fetchall()
                    if sample_rows:
                        columns = sample_result.keys()
                        table_info["sample_rows"] = [
                            dict(zip(columns, row)) for row in sample_rows
                        ]
                    else:
                        table_info["sample_rows"] = []
                except Exception:
                    table_info["sample_rows"] = []
            
            schema_info["tables"].append(table_info)
        
        return schema_info
    
    async def create_database(self, user_id: str, dataset_id: str):
        """Create a new database file"""
        db_path = self.get_database_path(user_id, dataset_id)
        if not db_path.exists():
            # Create empty database by executing a simple query
            # This ensures the SQLite file is actually created on disk
            engine = await self.get_engine(user_id, dataset_id)
            try:
                async with engine.begin() as conn:
                    await conn.execute(text("SELECT 1"))
            finally:
                await engine.dispose()
    
    async def close_all(self):
        """Close all database connections"""
        for engine in self.connections.values():
            await engine.dispose()
        self.connections.clear()


# Global database manager instance
db_manager = DatabaseManager()

