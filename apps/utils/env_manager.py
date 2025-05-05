from .singleton_meta import SingletonMeta
import os
import environ
from pathlib import Path
BASE_DIR = Path(__file__).resolve().parent.parent.parent


class EnvManager(metaclass=SingletonMeta):
	"""
	Loads the environment variables to be used both for settings.py and database connection.
	"""
	def __init__(self):
		self.config = self._load_config()



	def _load_config(self):		
		env = environ.Env()
		location = str(BASE_DIR / '.env')
		
		if not os.path.exists(location):
			raise RuntimeError('Error: The .env file was nof found at {location}.')
		else:
			pass
		environ.Env.read_env(env_file=location)
		
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
