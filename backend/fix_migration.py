import sqlite3

conn = sqlite3.connect('db.sqlite3')
cursor = conn.cursor()

# Remove the problematic migration record
cursor.execute("DELETE FROM django_migrations WHERE app = 'customer_contact' AND name = '0002_alter_customercontact_customer'")
conn.commit()

print("Removed problematic migration record")
conn.close()