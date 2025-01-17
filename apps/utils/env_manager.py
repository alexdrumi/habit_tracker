from .singleton_meta import SingletonMeta
import os
import environ

from pathlib import Path
BASE_DIR = Path(__file__).resolve().parent.parent.parent

# MARIADB_ROOT_PASSWORD=gc51cFzuxfAWr9DkROHzFgkrQnZDWxIuNrNNOIIWadA
# MARIADB_DATABASE=habit
# MARIADB_USER=bmajor
# MARIADB_PASSWORD=drowssapsergtsop
# MARIADB_HOST=127.0.0.1
# MARIADB_PORT=5000

# MARIADB_SUPERUSER=bmajor
# MARIADB_USER_EMAIL=mbencus89@gmail.com
# MARIADB_SUPERUSER_EMAIL=mbencus89@gmail.com
# MARIADBDB_SUPERUSER_PASSWORD=e9538bfb


class EnvManager(metaclass=SingletonMeta):
	'''Loads the environment variables to be used both for settings.py and database connection.'''
	def __init__(self):
		self.config = self._load_config()

	def _load_config(self):
		
		env = environ.Env()
		location = str(BASE_DIR / '.env')
		
		if not os.path.exists(location):
			print(f"Error: The .env file was not found at {location}")
			raise RuntimeError('Error: The .env file was nof found at {location}.')
		else:
			print(f"{location} is where the .env file is located")
		
		environ.Env.read_env(env_file=location)
		
		print(f'{location} IS WHERE THE ENV FILE IS LOCATED\n\n\n')
		return {
			"ENGINE": "django.db.backends.mysql",
			"NAME": env("MARIADB_DATABASE"), 
			"USER": env("MARIADB_USER"), 
			"PASSWORD": env("MARIADB_PASSWORD"),
			"HOST": env("MARIADB_HOST", default="127.0.0.1"),
			"PORT": env("MARIADB_PORT", default="5000")
		}

	def get_config(self, key):
		return self.config.get(key)
