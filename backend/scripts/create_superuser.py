import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from django.contrib.auth.models import User

def create_superuser(username, email, password):
    if User.objects.filter(username=username).exists():
        print('Superuser already exists')
    else:
        User.objects.create_superuser(username=username, email=email, password=password)
        print('Superuser created successfully')


if __name__ == '__main__':
    #env variables?
    env = environ.Env()
    environ.Env.read_env()
    username = env('MARIADB_USER')
    email = env('MARIADB_USER_EMAIL')
    password = env('MARIADB_PASSWORD')

    create_superuser(username, email, password)

