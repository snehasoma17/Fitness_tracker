import sqlite3

conn = sqlite3.connect("fitness.db")
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS workouts(
id INTEGER PRIMARY KEY AUTOINCREMENT,
date TEXT,
exercise TEXT,
duration INTEGER,
calories INTEGER
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS meals(
id INTEGER PRIMARY KEY AUTOINCREMENT,
date TEXT,
meal TEXT,
calories INTEGER
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS weight_log(
id INTEGER PRIMARY KEY AUTOINCREMENT,
date TEXT,
weight REAL
)
""")

conn.commit()
conn.close()

print("Database Created")
