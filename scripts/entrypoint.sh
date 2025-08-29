#!/bin/bash

set -e
echo "Applying database migration"
python manage.py migrate

echo "Creating superuser."
chmod +x scripts/create_superuser.py
python scripts/create_superuser.py


echo "Starting server..."
exec python manage.py runserver 0.0.0.0:8000
