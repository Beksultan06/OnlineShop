#!/bin/bash

# ------------------------------------------
# deploy.sh - автоматизация деплоя Django проекта
# ------------------------------------------

# Путь к проекту и виртуальному окружению
PROJECT_DIR="/opt/OnlineShop"
VENV_DIR="$PROJECT_DIR/venv"

# Останавливаем сервисы перед деплоем
echo "Stopping services..."
systemctl stop gunicorn
systemctl stop celery
systemctl stop celery-beat
systemctl stop nginx

# Переходим в директорию проекта
cd $PROJECT_DIR || { echo "Project directory not found! Exiting."; exit 1; }

# Активируем виртуальное окружение
source "$VENV_DIR/bin/activate" || { echo "Virtualenv not found! Exiting."; exit 1; }

# Применяем миграции
echo "Applying migrations..."
python manage.py migrate --noinput

# Перезапуск сервисов
echo "Starting services..."
systemctl start gunicorn
systemctl start celery
systemctl start celery-beat
systemctl start nginx

echo "Deployment finished successfully!"

