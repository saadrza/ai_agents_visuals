# tools/schema_tool.py
from langchain.tools import BaseTool
from data.db_access import list_tables

class SchemaTool(BaseTool):
    name: str = "inspect_schema"
    description: str = "List available tables in a database."

    def _run(self, user: str, db_name: str) -> str:
        tables = list_tables(user, db_name)
        return f"Tables in {db_name}: {tables}"

    async def _arun(self, *args, **kwargs):
        raise NotImplementedError
