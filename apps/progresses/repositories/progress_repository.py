from apps.habits.repositories.habit_repository import HabitRepository
from apps.goals.repositories.goal_repository import GoalRepository

from apps.database.database_manager import MariadbConnection
from mysql.connector.errors import IntegrityError

class ProgressesNotFoundError(Exception):
	"""Custom exception raised when analytics is not found."""
	pass


class ProgressesRepository:
	def __init__(self, database: MariadbConnection, goal_repository: GoalRepository):
		self._db = database
		self._goal_repository = goal_repository
	

	def create_progress(self, goal_id, progress_description=None):
		'''
		Create progress snapshot for a certain goals.
		'''
		try:
			#validation of habit will come from the service layer
			with self._db._connection.cursor() as cursor:		 
				query = "INSERT INTO progresses(goal_id_id, progress_description) VALUES (%s, %s);"
				cursor.execute(query, (goal_id, progress_description,))
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


	def get_progress_id(self, goal_id):
		try:
			with self._db._connection.cursor() as cursor:
				query = "SELECT progress_id FROM progresses WHERE goal_id_id = %s"
				cursor.execute(query, (goal_id,))
				result = cursor.fetchone()
				if result:
					progress_id_idx = 0
					return result[progress_id_idx]
				else:
					raise ProgressesNotFoundError(f"Progress with of with goal_id {goal_id} is not found.")
		except Exception as error:
			raise

	#https://dev.mysql.com/doc/connector-python/en/connector-python-api-mysqlcursordict.html
	def get_progress(self, progress_id):
		try:
			with self._db._connection.cursor(dictionary=True) as cursor:
				query = "SELECT * FROM progresses WHERE progress_id = %s;"
				cursor.execute(query, (progress_id,))
				progress_entry = cursor.fetchone()

				if not progress_entry:
					raise ProgressesNotFoundError(f"Progress with id {progress_id} not found.")

				return progress_entry
	
		except Exception as error:
			raise



	def delete_progress(self, progress_id):
		try:
			with self._db._connection.cursor() as cursor:
				query = "DELETE FROM progresses WHERE progress_id = %s;"
				cursor.execute(query, (progress_id,))
				self._db._connection.commit()

				if cursor.rowcount == 0:
					raise ProgressesNotFoundError(f"Progress with id {progress_id} is not found.")
				return cursor.rowcount
		except Exception as error:
			self._db._connection.rollback()
			raise

