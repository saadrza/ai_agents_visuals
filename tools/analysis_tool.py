# tools/analysis_tool.py
from langchain.tools import BaseTool
from data.db_access import load_table

class DataAnalysisTool(BaseTool):
    name: str = "data_analysis"
    description: str = (
        "Analyze a database table. "
        "Inputs: user, db_name, table, analysis_type "
        "analysis_type ∈ {summary, correlation, missing}"
    )

    def _run(self, user: str, db_name: str, table: str, analysis_type: str) -> str:
        df = load_table(user, db_name, table)

        if analysis_type == "summary":
            return df.describe(include="all").to_string()

        if analysis_type == "correlation":
            return df.corr(numeric_only=True).to_string()

        if analysis_type == "missing":
            return df.isnull().sum().to_string()

        return "Unsupported analysis type"

    async def _arun(self, *args, **kwargs):
        raise NotImplementedError
