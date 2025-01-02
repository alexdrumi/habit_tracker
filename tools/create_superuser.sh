#!/bin/bash

#!/bin/bash

# Check if the superuser exists
./manage.py shell -c "
import os
from django.contrib.auth.models import User
username = os.environ.get('MARIADB_USER')
email = os.environ.get('MARIADB_USER_EMAIL')
password = os.environ.get('MARIADB_PASSWORD')
if not User.objects.filter(username=username).exists():
    User.objects.create_superuser(username=username, email=email, password=password)
    print(f'Superuser {username} created successfully.')
else:
    print(f'Superuser {username} already exists.')
"
