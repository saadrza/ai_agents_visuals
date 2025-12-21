# data/db_access.py
import sqlite3
import pandas as pd
from data.db_registry import DATABASES, USER_DB_ACCESS


def list_tables(user, db_name):
    """List all tables in the database if user has access.
    
    Args:
        user: User role (admin, analyst, guest)
        db_name: Database name (Northwind, Chinook, Sakila)
        Returns:
        List of table names
    """
    if db_name not in USER_DB_ACCESS.get(user, []):
        print("User:", user, "DB Access:", USER_DB_ACCESS.get(user, []))
        raise PermissionError("Access denied")

    conn = sqlite3.connect(DATABASES[db_name])
    tables = pd.read_sql(
        "SELECT name FROM sqlite_master WHERE type='table'", conn
    )
    conn.close()
    return tables["name"].tolist()

def get_database_schema(user, db_name):
    """
    Returns a string summary of the database schema for the LLM.
    Args:
        user: User role (admin, analyst, guest)
        db_name: Database name (Northwind, Chinook, Sakila)
    Format: TableName (Column1, Column2, ...)
    """
    if db_name not in USER_DB_ACCESS.get(user, []):
        raise PermissionError("Access denied")

    conn = sqlite3.connect(DATABASES[db_name])
    cursor = conn.cursor()
    
    # Get all tables
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = [row[0] for row in cursor.fetchall()]
    
    schema_summary = []
    
    for table in tables:
        # Get columns for each table
        # PRAGMA table_info returns: (cid, name, type, notnull, dflt_value, pk)
        cursor.execute(f"PRAGMA table_info([{table}])") 
        columns = [f"{col[1]} ({col[2]})" for col in cursor.fetchall()]
        schema_summary.append(f"Table: {table}\nColumns: {', '.join(columns)}")
        
    conn.close()
    return "\n\n".join(schema_summary)


def load_table(user, db_name, table):
    """
    Load a table from the database with proper handling of SQL reserved keywords.
    
    Args:
        user: User role (admin, analyst, guest)
        db_name: Database name (northwind, chinook, sakila)
        table: Table name to load
        
    Returns:
        pandas DataFrame with table data
    """
    if db_name not in USER_DB_ACCESS.get(user, []):
        raise PermissionError("Access denied")

    # List of SQL reserved keywords that need escaping
    RESERVED_KEYWORDS = [
        'Order', 'User', 'Group', 'Table', 'Index', 'Key', 
        'Select', 'From', 'Where', 'Join', 'Union', 'Database'
    ]
    
    # Escape table name if it's a reserved keyword
    table_name = table
    if table in RESERVED_KEYWORDS:
        table_name = f'[{table}]'
    
    conn = sqlite3.connect(DATABASES[db_name])
    
    try:
        # Use the escaped table name
        df = pd.read_sql(f"SELECT * FROM {table_name}", conn)
    except sqlite3.OperationalError as e:
        # If still fails, try with backticks (alternative escaping)
        if "syntax error" in str(e):
            try:
                df = pd.read_sql(f"SELECT * FROM `{table}`", conn)
            except:
                # If both fail, raise the original error
                raise e
        else:
            raise e
    finally:
        conn.close()
    
    return df


def execute_query(user, db_name, query):
    """
    Execute a custom SQL query with permission check and reserved keyword handling.
    
    Args:
        user: User role
        db_name: Database name
        query: SQL query to execute
        
    Returns:
        pandas DataFrame with query results
    """
    if db_name not in USER_DB_ACCESS.get(user, []):
        raise PermissionError("Access denied")
    
    # Only allow SELECT queries for security
    if not query.strip().upper().startswith('SELECT'):
        raise ValueError("Only SELECT queries are allowed")
    
    # Auto-escape common reserved keywords in the query
    RESERVED_KEYWORDS = ['Order', 'User', 'Group']
    for keyword in RESERVED_KEYWORDS:
        # Replace various patterns where reserved words appear
        query = query.replace(f' FROM {keyword} ', f' FROM [{keyword}] ')
        query = query.replace(f' FROM {keyword};', f' FROM [{keyword}];')
        query = query.replace(f' FROM {keyword}\n', f' FROM [{keyword}]\n')
        query = query.replace(f' JOIN {keyword} ', f' JOIN [{keyword}] ')
        query = query.replace(f' JOIN {keyword}\n', f' JOIN [{keyword}]\n')
    
    conn = sqlite3.connect(DATABASES[db_name])
    
    try:
        df = pd.read_sql_query(query, conn)
    finally:
        conn.close()
    
    return df