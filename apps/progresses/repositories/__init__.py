from apps.habits.repositories.habit_repository import HabitRepository
from apps.goals.repositories.goal_repository import GoalRepository

from apps.database.database_manager import MariadbConnection
from mysql.connector.errors import IntegrityError

class ProgressesNotFoundError(Exception):
	"""Custom exception raised when analytics is not found."""
	pass


class AnalyticsRepository:
	def __init__(self, database: MariadbConnection, goal_repository: GoalRepository):
		self._db = database
		self._goal_repository = GoalRepository
	

	def create_progresses(self, goal_id, progress_description=None, last_completed_at=None):
		'''
		Create progress snapshot for a certain goals.
		'''
		try:
			#validation of habit will come from the service layer
			with self._db._connection.cursor() as cursor:
				#probably validation should happen in the service later
		
				query = "INSERT INTO progresses(goal_id_id, progress_description, occurence_date) VALUES (%s, %s, NOW());"
				cursor.execute(query, (goal_id, progress_description))
				self._db._connection.commit()
				return {
					'progress_id': cursor.lastrowid,
					'goal_id': goal_id,
				}
		except IntegrityError as ierror:
			if "Duplicate entry" in str(ierror):
				raise IntegrityError(f"Duplicate progress for goal with id '{goal_id}'.") from ierror
			raise
		except Exception as error:
			self._db._connection.rollback()
			raise