#!/bin/bash
set -e

#wait for mariadb
until mysqladmin ping -h "$MARIADB_HOST" -P "$MARIADB_PORT" --silent; do
  echo 'waiting for mariadb…'
  sleep 2
done

#run migrations
python manage.py migrate --noinput

#launch uvicorn server
exec uvicorn main:app \
  --host 0.0.0.0 \
  --port 8000 \
  --reload       # remove this --reload in real prod
