# #!/bin/bash

# set -e
# echo "Applying database migration"
# python manage.py migrate

# echo "Creating superuser."
# chmod +x scripts/create_superuser.py
# python scripts/create_superuser.py


# # Start the server
# echo "Starting server..."
# exec python manage.py runserver 0.0.0.0:8000


#!/usr/bin/env bash
set -e

# Wait for MariaDB to be ready
echo "⏳ Waiting for MariaDB..."
while ! mariadb -h mariadb -u root -p"${MARIADB_ROOT_PASSWORD}" -e "select 1"; do
  sleep 2
done

# Run Django/FastAPI migrations if any (adjust for your setup)
# echo "📜 Applying migrations…"
# python manage.py migrate

echo "🚀 Starting FastAPI"
uvicorn app.main:app --host 0.0.0.0 --reload
