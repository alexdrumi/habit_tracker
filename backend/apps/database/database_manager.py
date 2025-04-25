import psycopg2
import MySQLdb
import mysql.connector as mysql

from apps.utils.singleton_meta import SingletonMeta
from apps.utils.env_manager import EnvManager

# class SingletonMeta(type):
# 	'''
# 	A Singleton metaclass that ensures a class has only one instance.
# 	'''
# 	_instances = {}

# 	def __call__(cls, *args, **kwargs): #https://www.geeksforgeeks.org/__call__-in-python/ ->functions like init but for metaclasses
# 		#cls checks if this class (cls) already, exist in instances
# 		if cls not in cls._instances:
# 			instance = super().__call__(*args, **kwargs)
# 			cls._instances[cls] = instance
# 		return cls._instances[cls]



'''

#We could also use this later to load the env vars only once and store it somewhere so we can also use it here
import os

class ConfigManager(metaclass=SingletonMeta):
    def __init__(self):
        self.config = self._load_config()

    def _load_config(self):
        # Load configuration from environment variables or a file
        return {
            'DEBUG': os.getenv('DEBUG', 'False'),
            'DATABASE_URL': os.getenv('DATABASE_URL', 'sqlite:///db.sqlite3'),
            # Add other configurations here
        }

    def get_config(self, key):
        return self.config.get(key)
'''

# https://dev.mysql.com/doc/connector-python/en/connector-python-api-mysql-connector-connect.html
class MariadbConnection(metaclass=SingletonMeta):
	'''Singleton class for managing database connections.'''
	def __init__(self):

		config = EnvManager() #singleton to store env details

		self._connection = mysql.connect(
			host=config.get_config("HOST"),
			user=config.get_config("USER"),
			password=config.get_config("PASSWORD"),
			database=config.get_config("NAME"),
			port=config.get_config("PORT"),
			charset="utf8mb4",
			collation="utf8mb4_unicode_ci"
		)

		cursor = self._connection.cursor()
		# query = ("SELECT DATABASE();")
		# cursor.execute(query)
		# results = cursor.fetchall()
		# for db in results:
		# 	print(db)
	
	
		




