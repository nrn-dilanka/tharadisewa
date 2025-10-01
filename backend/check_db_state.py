import sqlite3

conn = sqlite3.connect('db.sqlite3')
cursor = conn.cursor()

# Check what tables exist
cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name LIKE '%customer%'")
tables = cursor.fetchall()
print("Customer-related tables:")
for table in tables:
    print(f"  - {table[0]}")

# Check migration records
cursor.execute("SELECT app, name, applied FROM django_migrations WHERE app IN ('customer', 'customer_contact') ORDER BY app, name")
migrations = cursor.fetchall()
print("\nMigration records:")
for migration in migrations:
    print(f"  {migration[0]}.{migration[1]} - Applied: {migration[2]}")

conn.close()