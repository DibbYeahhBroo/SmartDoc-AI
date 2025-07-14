import sqlite3

# Connect to (or create) the database
conn = sqlite3.connect('database.db')
cursor = conn.cursor()

# Create the users table
cursor.execute('''
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        email TEXT NOT NULL,
        password TEXT NOT NULL
    )
''')

# Save and close
conn.commit()
conn.close()

print(" Database created successfully.")
