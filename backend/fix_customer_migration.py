import sqlite3
import sys

conn = sqlite3.connect('db.sqlite3')
cursor = conn.cursor()

try:
    # Add the customer.0001_initial migration record
    cursor.execute("""
        INSERT INTO django_migrations (app, name, applied) 
        VALUES ('customer', '0001_initial', datetime('now'))
    """)
    conn.commit()
    print("Added customer.0001_initial migration record")
except sqlite3.IntegrityError as e:
    print(f"Migration record already exists: {e}")

conn.close()