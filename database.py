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
    username TEXT,
    date TEXT,
    meal TEXT,
    food TEXT,
    calories INTEGER,
    protein INTEGER DEFAULT 0,
    carbs INTEGER DEFAULT 0
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
