#!/bin/bash

echo "=== TharadiSewa Backend Setup Script ==="
echo

# Navigate to backend directory
cd /home/robotics/Project/TharadiSewa/backend

# Activate virtual environment
echo "Activating virtual environment..."
source /home/robotics/Project/TharadiSewa/.venv/bin/activate

# Make migrations
echo "Creating migrations..."
python manage.py makemigrations

# Apply migrations
echo "Applying migrations..."
python manage.py migrate

# Create superuser
echo "Creating superuser..."
echo "Please enter superuser details:"
python manage.py createsuperuser

echo
echo "=== Setup Complete! ==="
echo
echo "To start the development server:"
echo "cd /home/robotics/Project/TharadiSewa/backend"
echo "source /home/robotics/Project/TharadiSewa/.venv/bin/activate"
echo "python manage.py runserver"
echo
echo "Then visit:"
echo "- API: http://localhost:8000/api/"
echo "- Admin: http://localhost:8000/admin/"
echo
echo "To test the API:"
echo "python test_api.py"