import sqlite3

db = sqlite3.connect("cuentas.db")
c = db.cursor()

c.execute("""
CREATE TABLE accounts (
 id INTEGER PRIMARY KEY AUTOINCREMENT,
 platform TEXT,
 username TEXT,
 password TEXT,
 used INTEGER DEFAULT 0
)
""")

c.execute("""
CREATE TABLE logs (
 id INTEGER PRIMARY KEY AUTOINCREMENT,
 user_id INTEGER,
 platform TEXT,
 date TEXT
)
""")

db.commit()
db.close()
print("DB creada")
