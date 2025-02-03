from apps.habits.repositories.habit_repository import HabitRepository
from apps.database.database_manager import MariadbConnection
from mysql.connector.errors import IntegrityError

class AnalyticsNotFoundError(Exception):
	"""Custom exception raised when analytics is not found."""
	pass


class AnalyticsRepository:
	def __init__(self, database: MariadbConnection, habit_repository: HabitRepository):
		self._db = database
		self._habit_repository = habit_repository


	def create_analytics(self, times_completed, streak_length, habit_id, last_completed_at=None):
		'''
		Create analytics for a certain habit.
		'''
		try:
			#validation of habit will come from the service layer
			with self._db._connection.cursor() as cursor:
				#probably validation should happen in the service later
		
				query = "INSERT INTO analytics(times_completed, streak_length, last_completed_at, created_at, habit_id_id) VALUES (%s, %s, %s, NOW(), %s);"
				cursor.execute(query, (times_completed, streak_length, last_completed_at, habit_id))
				self._db._connection.commit()
				return {
					'analytics_id': cursor.lastrowid,
					'times_completed': times_completed,
					'streak_length': streak_length,
					'last_completed_at': last_completed_at,
					'habit_id_id': habit_id,
				}
		except IntegrityError as ierror:
			if "Duplicate entry" in str(ierror):
				raise IntegrityError(f"Duplicate analytics for habit with id '{habit_id}'.") from ierror
			raise
		except Exception as error:
			self._db._connection.rollback()
			raise
	def get_analytics_id()
		
	def update_analytics(self, streak_length,)