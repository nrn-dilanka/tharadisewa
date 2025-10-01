import sqlite3

conn = sqlite3.connect('db.sqlite3')
cursor = conn.cursor()

# Find all migrations that might depend on customer
cursor.execute("""
    SELECT app, name, applied 
    FROM django_migrations 
    WHERE app != 'customer' 
    ORDER BY app, name
""")
migrations = cursor.fetchall()
print("All non-customer migrations:")
for migration in migrations:
    print(f"  {migration[0]}.{migration[1]} - Applied: {migration[2][:19] if migration[2] else 'None'}")

conn.close()