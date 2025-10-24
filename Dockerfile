# Используем конкретную версию Python
FROM python:3.13.7-slim

# Устанавливаем системные библиотеки
RUN apt-get update && apt-get install -y \
    libgl1 \
    libglib2.0-0 \
    make \
 && rm -rf /var/lib/apt/lists/*

# Устанавливаем рабочую директорию
WORKDIR /app

# Копируем файл зависимостей
COPY requirements.txt .

# Обновляем pip и устанавливаем зависимости
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

# Копируем весь проект
COPY . .

# Копируем и делаем исполняемым entrypoint
COPY entrypoint.sh /app/entrypoint.sh
RUN chmod +x /app/entrypoint.sh

# Экспонируем порт Django
EXPOSE 8000

# Используем entrypoint
ENTRYPOINT ["sh", "/app/entrypoint.sh"]