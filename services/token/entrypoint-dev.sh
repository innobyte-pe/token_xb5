#!/bin/sh

echo "Esperando a Mysql..."

while ! nc -z token-db 3306; do
  sleep 0.1
done

echo "Mysql iniciado:w"

python manage.py run -h 0.0.0.0
