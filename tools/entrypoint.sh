#!/bin/bash

set -e
echo "Applying database migration"
python manage.py migrate

echo "Creating superuser."
chmod +x backend/create_superuser.py
python backend/create_superuser.py


# Start the server
echo "Starting server..."
exec python manage.py runserver 0.0.0.0:8000
