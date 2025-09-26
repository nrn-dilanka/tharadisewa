#!/bin/bash

# Django Backend Setup and Migration Script
# This script will create migrations and setup the database for all apps

echo "🚀 Starting Django Backend Setup..."

# Navigate to backend directory
cd /home/robotics/Project/TharadiSewa/backend

echo "📦 Activating virtual environment..."
source /home/robotics/Project/TharadiSewa/.venv/bin/activate

echo "� Installing additional Python packages for product app..."
pip install qrcode[pil] Pillow django-filter

echo "�🔄 Creating migrations for all apps..."
python manage.py makemigrations

echo "🗄️ Applying migrations to database..."
python manage.py migrate

echo "👤 Creating Django superuser (optional)..."
echo "You can create a superuser by running:"
echo "python manage.py createsuperuser"
echo ""

echo "🎯 Available Django Commands:"
echo "1. Start development server:"
echo "   python manage.py runserver"
echo ""
echo "2. Create superuser:"
echo "   python manage.py createsuperuser"
echo ""
echo "3. Access Django Admin:"
echo "   http://localhost:8000/admin/"
echo ""
echo "4. API Endpoints:"
echo "   - Authentication: http://localhost:8000/api/auth/"
echo "   - Customers: http://localhost:8000/api/customers/"
echo "   - Customer Contacts: http://localhost:8000/api/contacts/"
echo "   - Shops: http://localhost:8000/api/shops/"
echo "   - Customer Locations: http://localhost:8000/api/locations/"
echo "   - Products: http://localhost:8000/api/products/"
echo "   - Purchases: http://localhost:8000/api/purchases/"
echo ""

echo "✅ Setup completed successfully!"
echo ""
echo "📚 Documentation:"
echo "   - API Documentation: backend/SHOP_LOCATION_API_DOCUMENTATION.md"
echo "   - Customer API: backend/customer/API_DOCUMENTATION.md"
echo "   - Customer Contact API: backend/customer_contact/API_DOCUMENTATION.md"
echo "   - Product API: backend/product/API_DOCUMENTATION.md"
echo "   - Purchase API: backend/purchase/API_DOCUMENTATION.md"
echo ""
echo "🔧 To start development server, run:"
echo "   python manage.py runserver"