#!/bin/bash
set -e

echo "Waiting for database..."
sleep 5

# Применяем миграции
echo "Applying migrations..."
python manage.py migrate --noinput

# Пропускаем collectstatic если не настроен STATIC_ROOT
echo "Skipping collectstatic to avoid configuration issues..."

# Создаем суперпользователя через Python скрипт
echo "Setting up superuser..."
python manage.py shell -c "
import os
from django.contrib.auth import get_user_model
User = get_user_model()

if not User.objects.filter(is_superuser=True).exists():
    username = os.getenv('DJANGO_SUPERUSER_USERNAME', 'admin')
    email = os.getenv('DJANGO_SUPERUSER_EMAIL', 'admin@example.com') 
    password = os.getenv('DJANGO_SUPERUSER_PASSWORD', 'admin123')
    
    print(f'Creating superuser: {username}')
    User.objects.create_superuser(username=username, email=email, password=password)
    print('Superuser created successfully')
else:
    print('Superuser already exists')
"

# Запускаем сервер
echo "Starting server..."
python manage.py runserver 0.0.0.0:8000