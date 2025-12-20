# data/db_registry.py

DATABASES = {
    "Northwind": "database/northwind_small.sqlite",
    "Chinook":  "database/chinook.db",
    "Sakila":   "database/sakila.db"
}

USER_DB_ACCESS = {
    "admin": ["Northwind", "Chinook", "Sakila"],
    "analyst": ["Northwind", "Chinook"],
    "guest": []
}