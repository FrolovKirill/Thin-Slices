#!/bin/bash
set -e

# 1. Применяем миграции
python manage.py migrate --noinput

# 2. Проверяем, есть ли суперюзер
SUPERUSER_EXISTS=$(python manage.py shell -c "from django.contrib.auth import get_user_model; \
print(get_user_model().objects.filter(is_superuser=True).exists())")

# 3. Создаём суперюзера интерактивно только если его нет
if [ "$SUPERUSER_EXISTS" = "False" ]; then
    echo "No superuser found. Please create one:"
    python manage.py createsuperuser
else
    echo "Superuser already exists."
fi

# 4. Запускаем сервер
python manage.py runserver 0.0.0.0:8000