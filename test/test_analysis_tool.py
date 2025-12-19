def test_table_listing():
    from data.db_access import list_tables
    tables = list_tables("admin", "northwind")
    assert "Orders" in tables


def test_permission_enforced():
    from data.db_access import list_tables
    try:
        list_tables("guest", "chinook")
        assert False
    except PermissionError:
        assert True


def test_summary_analysis():
    from tools.analysis_tool import DataAnalysisTool
    tool = DataAnalysisTool()
    result = tool.run(
        user="admin",
        db_name="chinook",
        table="Customers",
        analysis_type="summary"
    )
    assert "count" in result
