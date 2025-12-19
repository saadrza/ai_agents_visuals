# data/db_access.py
import sqlite3
import pandas as pd
from data.db_registry import DATABASES, USER_DB_ACCESS

def list_tables(user, db_name):
    if db_name not in USER_DB_ACCESS.get(user, []):
        print("User:", user, "DB Access:", USER_DB_ACCESS.get(user, []))
        raise PermissionError("Access denied")

    conn = sqlite3.connect(DATABASES[db_name])
    tables = pd.read_sql(
        "SELECT name FROM sqlite_master WHERE type='table'", conn
    )
    conn.close()
    return tables["name"].tolist()


def load_table(user, db_name, table):
    if db_name not in USER_DB_ACCESS.get(user, []):
        raise PermissionError("Access denied")

    conn = sqlite3.connect(DATABASES[db_name])
    df = pd.read_sql(f"SELECT * FROM {table}", conn)
    conn.close()
    return df
