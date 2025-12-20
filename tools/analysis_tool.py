# tools/analysis_tool.py
from langchain.tools import BaseTool
from typing import Type
from pydantic import BaseModel, Field
import sqlite3
import pandas as pd


class AnalysisInput(BaseModel):
    """Input schema for DataAnalysisTool."""
    query: str = Field(description="SQL SELECT query to execute for data analysis")


class DataAnalysisTool(BaseTool):
    """Tool for analyzing data from the database."""
    
    name: str = "analyze_data"
    description: str = """
    Execute SQL queries and analyze the results.
    Use this to get data summaries, statistics, and insights.
    Input: A valid SQL SELECT query.
    Returns: Query results with basic statistics.
    
    IMPORTANT: For tables with reserved SQL keywords (Order, User, Group, etc.), 
    use square brackets like [Order] or backticks like `Order`.
    Example: SELECT * FROM [Order] instead of SELECT * FROM Order
    """
    args_schema: Type[BaseModel] = AnalysisInput
    db_path: str = None
    
    def __init__(self, db_path: str = None):
        super().__init__()
        self.db_path = db_path
        if not self.db_path:
            raise ValueError("db_path is required")
    
    def _run(self, query: str) -> str:
        """Execute query and analyze results."""
        try:
            # Validate it's a SELECT query
            if not query.strip().upper().startswith('SELECT'):
                return "Error: Only SELECT queries are allowed for security reasons"
            
            # Escape common reserved keywords in table names
            # This helps when the LLM generates queries with reserved words
            reserved_words = ['Order', 'User', 'Group', 'Table', 'Index', 'Key']
            for word in reserved_words:
                # Replace unescaped table names
                query = query.replace(f' FROM {word} ', f' FROM [{word}] ')
                query = query.replace(f' FROM {word};', f' FROM [{word}];')
                query = query.replace(f' JOIN {word} ', f' JOIN [{word}] ')
                query = query.replace(f' FROM {word}\n', f' FROM [{word}]\n')
            
            conn = sqlite3.connect(self.db_path)
            
            # Execute query
            df = pd.read_sql_query(query, conn)
            conn.close()
            
            if df.empty:
                return "Query returned no results"
            
            # Generate analysis
            analysis = f"Query Results:\n"
            analysis += f"- Total rows: {len(df)}\n"
            analysis += f"- Columns: {', '.join(df.columns)}\n\n"
            
            # Show first few rows
            max_rows = min(10, len(df))
            analysis += f"Sample data (first {max_rows} rows):\n"
            analysis += df.head(max_rows).to_string(index=False, max_colwidth=50) + "\n\n"
            
            # Basic statistics for numeric columns
            numeric_cols = df.select_dtypes(include=['number']).columns
            if len(numeric_cols) > 0:
                analysis += "Numeric column statistics:\n"
                analysis += df[numeric_cols].describe().to_string() + "\n"
            
            return analysis
            
        except Exception as e:
            error_msg = str(e)
            if "syntax error" in error_msg.lower() and "order" in error_msg.lower():
                return (
                    f"SQL Syntax Error: {error_msg}\n\n"
                    "TIP: The 'Order' table name is a reserved SQL keyword. "
                    "Please use square brackets: SELECT * FROM [Order] "
                    "or backticks: SELECT * FROM `Order`"
                )
            return f"Error analyzing data: {error_msg}\nMake sure your SQL query is valid for SQLite."