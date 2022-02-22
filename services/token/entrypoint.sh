#!/bin/sh

echo "Esperando a Mysql..."

while ! nc -z token-db 3306; do
  sleep 0.1
done

echo "Mysql iniciado"

gunicorn -b 0.0.0.0:5000 manage:app