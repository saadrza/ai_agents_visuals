# data/db_registry.py
DATABASES = {
    "northwind": "database/northwind_small.sqlite",
    "chinook":  "database/chinook.db",
    "sakila":   "database/sakila.db"
}

USER_DB_ACCESS = {
    "admin": ["northwind", "chinook", "sakila"],
    "analyst": ["northwind", "chinook"],
    "guest": []
}
