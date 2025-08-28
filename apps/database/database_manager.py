import psycopg2
import MySQLdb
import mysql.connector as mysql

from apps.utils.singleton_meta import SingletonMeta
from apps.utils.env_manager import EnvManager

class MariadbConnection(metaclass=SingletonMeta):
	'''Singleton class for managing database connections.'''
	def __init__(self):

		config = EnvManager()

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




