import sqlite3

conn = sqlite3.connect('db.sqlite3')
cursor = conn.cursor()

# Remove migrations that depend on customer
migrations_to_remove = [
    ('purchase', '0002_alter_purchase_customer'),
    ('shop', '0002_alter_shop_customer')
]

for app, migration_name in migrations_to_remove:
    cursor.execute("DELETE FROM django_migrations WHERE app = ? AND name = ?", (app, migration_name))
    print(f"Removed {app}.{migration_name}")

conn.commit()
conn.close()