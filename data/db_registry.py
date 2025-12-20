# data/db_registry.py

DATABASES = {
    "Northwind": "input_files/database/northwind_small.sqlite",
    "Chinook":  "input_files/database/chinook.db",
    "Sakila":   "input_files/database/sakila.db"
}

USER_DB_ACCESS = {
    "admin": ["Northwind", "Chinook", "Sakila"],
    "analyst": ["Northwind", "Chinook"],
    "guest": []
}