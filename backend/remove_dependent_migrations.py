import sqlite3

conn = sqlite3.connect('db.sqlite3')
cursor = conn.cursor()

# Remove customer_contact migrations that depend on customer.0001_initial
cursor.execute("DELETE FROM django_migrations WHERE app = 'customer_contact' AND name = '0002_alter_customercontact_customer'")
conn.commit()

print("Removed customer_contact.0002_alter_customercontact_customer migration record")
conn.close()