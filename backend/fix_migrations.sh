#!/bin/bash
# Migration Fix Script for TharadiSewa Backend
# Run this script to fix the migration dependency conflict

echo "🔧 Starting migration dependency fix..."

# Step 1: Fake revert the problematic customer_contact migration
echo "📤 Step 1: Fake reverting customer_contact to 0001..."
python manage.py migrate customer_contact 0001 --fake

# Step 2: Apply the customer initial migration
echo "📥 Step 2: Applying customer initial migration..."
python manage.py migrate customer 0001

# Step 3: Apply the customer_contact fix migration
echo "🔄 Step 3: Applying customer_contact fix migration..."
python manage.py migrate customer_contact 0002

# Step 4: Apply all remaining migrations
echo "✅ Step 4: Applying all remaining migrations..."
python manage.py migrate

# Step 5: Show migration status
echo "📊 Final migration status:"
python manage.py showmigrations

echo "🎉 Migration fix completed!"
echo "📝 You can now run: python manage.py runserver"