# Django Migration Dependency Fix Guide

## Problem Identified
Migration dependency conflict between `customer` and `customer_contact` apps:
- `customer.0001_initial` is not applied ([ ])
- `customer_contact.0002_alter_customercontact_customer` is already applied ([X])
- This creates an inconsistent migration history

## Root Cause
The `customer_contact` app was initially created with a reference to `AUTH_USER_MODEL` instead of `customer.Customer`, then a migration was created to fix this, but it created a dependency conflict.

## Solution Steps

### Step 1: Reset the problematic migration
```bash
cd backend
python manage.py migrate customer_contact 0001 --fake
```

### Step 2: Apply the customer initial migration
```bash
python manage.py migrate customer 0001
```

### Step 3: Now apply the customer_contact migration properly
```bash
python manage.py migrate customer_contact 0002
```

### Step 4: Apply all remaining migrations
```bash
python manage.py migrate
```

## Alternative Solution (if above doesn't work)

If the above steps don't work, we need to recreate the customer_contact migrations:

### Step 1: Delete the problematic migration
```bash
# Delete the migration file (backup first)
rm backend/customer_contact/migrations/0002_alter_customercontact_customer.py
```

### Step 2: Reset customer_contact migrations
```bash
python manage.py migrate customer_contact zero --fake
```

### Step 3: Apply customer migration first
```bash
python manage.py migrate customer 0001
```

### Step 4: Recreate customer_contact migrations
```bash
python manage.py makemigrations customer_contact
```

### Step 5: Apply all migrations
```bash
python manage.py migrate
```

## Expected Output After Fix
```
customer
 [X] 0001_initial
customer_contact
 [X] 0001_initial
 [X] 0002_alter_customercontact_customer (or newly generated migration)
```

## Verification Commands
After fixing, verify with:
```bash
python manage.py showmigrations
python manage.py migrate --dry-run
python manage.py runserver
```

## Prevention for Future
To avoid this issue in the future:
1. Always create models with proper foreign key relationships from the start
2. Be careful with migration dependencies when models reference each other
3. Run `makemigrations` for all related apps together when creating cross-app relationships

## Files to Check After Fix
- Ensure `customer_contact/models.py` has correct foreign key to `customer.Customer`
- Verify database schema is correct
- Test API endpoints to ensure they work properly

## Database Schema Verification
After fixing migrations, verify the database schema:
```sql
-- Check if tables exist
.tables  -- SQLite
SHOW TABLES;  -- MySQL
\dt  -- PostgreSQL

-- Check customer table structure
.schema customers  -- SQLite
DESCRIBE customers;  -- MySQL
\d customers;  -- PostgreSQL
```

This should resolve the migration dependency conflict and allow your Django backend to start properly.