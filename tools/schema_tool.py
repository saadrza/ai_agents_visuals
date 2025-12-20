# tools/schema_tool.py
from langchain.tools import BaseTool
from pydantic import BaseModel, Field
import sqlite3
from typing import Type

class SchemaInput(BaseModel):
    db_path: str = Field(description="Full path to the SQLite database file")

class SchemaTool(BaseTool):
    name: str = "inspect_schema"
    description: str = """
    Useful for seeing table names and their column definitions.
    ALWAYS use this tool before writing a SQL query to ensure column names are correct.
    """
    args_schema: Type[BaseModel] = SchemaInput

    def _run(self, db_path: str) -> str:
        try:
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            
            # Get list of tables
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
            tables = [row[0] for row in cursor.fetchall()]
            
            schema_info = []
            for table in tables:
                # Get column info for each table
                cursor.execute(f"PRAGMA table_info([{table}])")
                columns = cursor.fetchall()
                # Format: (id, name, type, notnull, default, pk)
                col_str = ", ".join([f"{col[1]} ({col[2]})" for col in columns])
                schema_info.append(f"Table: {table}\n  Columns: {col_str}")
                
            conn.close()
            return "\n\n".join(schema_info)
        except Exception as e:
            return f"Error inspecting schema: {str(e)}"