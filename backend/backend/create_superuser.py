
import os
import django
import environ

from django.conf import settings
from django.contrib.auth.models import get_user_model

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'settings') 
django.setup()

User = get_user_model()

def create_superuser(email, password):
	if User.objects.filter(email=email).exists():
		print('Superuser with that email already exists')
	else:
		User.objects.create_superuser(email=email, password=password)
		print('Superuser created successfully')


if __name__ == '__main__':
	env = environ.Env()
	environ.Env.read_env()
	# for example, from .env:
	# SUPERUSER_EMAIL=admin@example.com
	# SUPERUSER_PASSWORD=123456
	env = environ.Env()
	environ.Env.read_env()
	email = env('MARIADB_SUPERUSER_EMAIL')
	password = env('MARIADBDB_SUPERUSER_PASSWORD')
	create_superuser(email, password)



# MARIADB_SUPERUSER_EMAIL=mbencus89@gmail.com
# MARIADBDB_SUPERUSER_PASSWORD=e9538bfb
# import os
# import django
# import environ

# os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'settings') #if we import this from another folder we gotta do smth else as well.
# django.setup()

# from django.contrib.auth.models import User

# def create_superuser(username, email, password):
#     if User.objects.filter(username=username).exists():
#         print('Superuser already exists')
#     else:
#         User.objects.create_superuser(username=username, email=email, password=password)
#         print('Superuser created successfully')


# if __name__ == '__main__':
#     #env variables?
#     env = environ.Env()
#     environ.Env.read_env()
#     username = env('MARIADB_USER')
#     email = env('MARIADB_USER_EMAIL')
#     password = env('MARIADB_PASSWORD')

#     create_superuser(username, email, password)

