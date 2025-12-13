#!/bin/bash
set -e

echo "Esperando a que la base de datos esté lista..."
python manage.py makemigrations --noinput
python manage.py migrate --noinput

echo "Recolectando archivos estáticos..."
python manage.py collectstatic --noinput --clear || echo "Advertencia: collectstatic falló, continuando..."

echo "Iniciando servidor..."
exec "$@"
