"""Simple CSV import script that doesn't require SQLAlchemy"""
import sqlite3
import csv
import sys
from pathlib import Path


def import_csv_to_sqlite(csv_path: str, db_path: str, table_name: str = None):
    """
    Import CSV file into SQLite database
    
    Args:
        csv_path: Path to CSV file
        db_path: Path to SQLite database file
        table_name: Optional table name (defaults to filename)
    """
    csv_file = Path(csv_path)
    if not csv_file.exists():
        print(f"Error: CSV file not found: {csv_path}")
        return
    
    # Determine table name
    if not table_name:
        table_name = csv_file.stem
    
    # Sanitize table name
    table_name = "".join(c if c.isalnum() or c == '_' else '_' for c in table_name)
    table_name = table_name.strip('_') or 'imported_data'
    
    # Ensure database directory exists
    db_file = Path(db_path)
    db_file.parent.mkdir(parents=True, exist_ok=True)
    
    # Connect to database
    conn = sqlite3.connect(str(db_file))
    cursor = conn.cursor()
    
    try:
        # Read CSV
        with open(csv_file, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            rows = list(reader)
            
            if not rows:
                print("Error: CSV file is empty")
                return
            
            # Get column names and sanitize them
            columns = []
            escaped_columns = []
            for col in reader.fieldnames:
                # Sanitize column name
                sanitized = col.strip().replace(' ', '_').replace('-', '_')
                sanitized = "".join(c if c.isalnum() or c == '_' else '_' for c in sanitized)
                sanitized = sanitized.strip('_')
                if sanitized and not (sanitized[0].isalpha() or sanitized[0] == '_'):
                    sanitized = '_' + sanitized
                columns.append(sanitized)
                # Escape for SQL (handle reserved keywords)
                escaped_columns.append(f'"{sanitized}"')
            
            # Infer types from first few rows
            column_types = {}
            for col in columns:
                sample_values = [row[col] for row in rows[:10] if row.get(col) and row[col].strip()]
                if not sample_values:
                    column_types[col] = 'TEXT'
                    continue
                
                # Try to infer type
                is_numeric = True
                is_integer = True
                is_date = True
                
                for val in sample_values:
                    val = val.strip()
                    if not val:
                        continue
                    
                    # Check if date
                    if '/' in val or '-' in val:
                        try:
                            from datetime import datetime
                            datetime.strptime(val, '%Y-%m-%d')
                        except:
                            is_date = False
                    else:
                        is_date = False
                    
                    # Check if numeric
                    try:
                        float_val = float(val)
                        if float_val != int(float_val):
                            is_integer = False
                    except:
                        is_numeric = False
                        is_integer = False
                
                if is_date:
                    column_types[col] = 'DATE'
                elif is_integer:
                    column_types[col] = 'INTEGER'
                elif is_numeric:
                    column_types[col] = 'REAL'
                else:
                    column_types[col] = 'TEXT'
            
            # Drop existing table
            cursor.execute(f'DROP TABLE IF EXISTS "{table_name}"')
            
            # Create table
            column_defs = [f'"{col}" {column_types[col]}' for col in columns]
            create_sql = f'CREATE TABLE "{table_name}" ({", ".join(column_defs)})'
            cursor.execute(create_sql)
            
            # Insert data
            placeholders = ','.join(['?' for _ in columns])
            insert_sql = f'INSERT INTO "{table_name}" ({", ".join(escaped_columns)}) VALUES ({placeholders})'
            
            rows_inserted = 0
            for row in rows:
                values = []
                for col in columns:
                    val = row.get(col, '').strip() if row.get(col) else None
                    if not val or val == '':
                        values.append(None)
                    else:
                        # Convert based on type
                        col_type = column_types[col]
                        if col_type == 'INTEGER':
                            try:
                                values.append(int(float(val)))
                            except:
                                values.append(None)
                        elif col_type == 'REAL':
                            try:
                                values.append(float(val))
                            except:
                                values.append(None)
                        elif col_type == 'DATE':
                            values.append(val)  # Keep as string
                        else:
                            values.append(val)
                
                cursor.execute(insert_sql, values)
                rows_inserted += 1
            
            conn.commit()
            
            print(f"Successfully imported dataset!")
            print(f"   Table: {table_name}")
            print(f"   Rows: {rows_inserted}")
            print(f"   Columns: {len(columns)}")
            print(f"   Location: {db_path}")
            
    except Exception as e:
        conn.rollback()
        print(f"Error importing CSV: {e}")
        raise
    finally:
        conn.close()


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python import_mvp_dataset_simple.py <path_to_csv> [table_name]")
        print("\nExample:")
        print("  python import_mvp_dataset_simple.py ../cleaned_diabetes_dataset.csv")
        print("  python import_mvp_dataset_simple.py ../cleaned_diabetes_dataset.csv diabetes_data")
        sys.exit(1)
    
    csv_path = sys.argv[1]
    table_name = sys.argv[2] if len(sys.argv) > 2 else None
    
    # Hardcoded paths for MVP
    db_path = Path(__file__).parent.parent / "data" / "default_user" / "mvp_dataset.db"
    
    import_csv_to_sqlite(csv_path, str(db_path), table_name)

