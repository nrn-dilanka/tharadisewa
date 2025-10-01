import sqlite3

conn = sqlite3.connect('db.sqlite3')
cursor = conn.cursor()

# Remove the fake customer migration record
cursor.execute("DELETE FROM django_migrations WHERE app = 'customer' AND name = '0001_initial'")
conn.commit()

print("Removed fake customer.0001_initial migration record")
conn.close()