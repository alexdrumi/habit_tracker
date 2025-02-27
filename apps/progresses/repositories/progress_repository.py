from apps.habits.repositories.habit_repository import HabitRepository
from apps.goals.repositories.goal_repository import GoalRepository

from apps.database.database_manager import MariadbConnection
from mysql.connector.errors import IntegrityError

#baseclass
class ProgressesRepositoryError(Exception):
	def __init__(self, message="An unexpected error occurred in progress repository."):
		super().__init__(message)


class ProgressNotFoundError(ProgressesRepositoryError):
	"""Raised when a progress is not found."""
	def __init__(self, goal_id_or_progress_id):
		message = f"Progress not found with goal/progress ID: {goal_id_or_progress_id}" #for now..
		super().__init__(message)


class ProgressAlreadyExistError(ProgressesRepositoryError):
	"""Raised when creating progress fails due to a already existing entry."""
	def __init__(self, progress_name, progress_id):
		message = f"Goal '{progress_name}' already exists for user with id: {progress_id}"
		super().__init__(message)

def handle_goal_repository_errors(f):
	"""Decorator to clean up and handle errors in progress repository methods."""
	def exception_wrapper(self, *args, **kwargs):
		try:
			return f(self, *args, **kwargs)
		except IntegrityError as ierror:
			self._db._connection.rollback()
			#in create_a_habit the first argument is habit_name and last is habit_user_id?
			raise ProgressAlreadyExistError(progress_name=args[0], progress_id=args[-1]) from ierror
		except ProgressesRepositoryError as herror:
			raise herror
		except Exception as error:
			self._db._connection.rollback()
			raise error
	return exception_wrapper




class ProgressesRepository:
	def __init__(self, database: MariadbConnection, goal_repository: GoalRepository):
		self._db = database
		self._goal_repository = goal_repository



	@handle_goal_repository_errors
	def create_progress(self, goal_id, current_kvi_value, distance_from_target_kvi_value, progress_description=None):
		'''
		Create a progress in the progresses table.

		Args:
			int, (str): The goal_id of the goal which made the progress. Optionally a progress description."
		
		Returns:
			Dict: Progress id and goal id.
		'''
		with self._db._connection.cursor() as cursor:		 
			query = "INSERT INTO progresses(current_kvi_value, goal_id_id, distance_from_goal_kvi_value, occurence_date) VALUES (%s, %s, %s, NOW());"
			cursor.execute(query, (current_kvi_value, goal_id, distance_from_target_kvi_value,))
			self._db._connection.commit()
			return {
				'progress_id': cursor.lastrowid,
				'goal_id': goal_id,
				'current_kvi_value': current_kvi_value,
				'distance_from_target_kvi_value': distance_from_target_kvi_value,
			}
	

	@handle_goal_repository_errors
	def get_progress_id(self, goal_id):
		with self._db._connection.cursor() as cursor:
			query = "SELECT progress_id FROM progresses WHERE goal_id_id = %s" #how to sort this based on occurence date?
			cursor.execute(query, (goal_id,))
			result = cursor.fetchone()
			if result:
				progress_id_idx = 0
				return result[progress_id_idx]
			else:
					raise ProgressNotFoundError(goal_id)

	@handle_goal_repository_errors
	def get_last_progress_entry(self, goal_id):
		with self._db._connection.cursor() as cursor:
			query = "SELECT * FROM progresses WHERE goal_id_id = %s ORDER BY occurence_date;"
			cursor.execute(query, (goal_id,))
			result = cursor.fetchall()

			if result:
				# print(f'FROM PROGRESS REPO {result} IS THE LAST PROGRESS OR SO')
				# print(result[0])
				return result[-1] #last entry
			else:
				return None
		

	#https://dev.mysql.com/doc/connector-python/en/connector-python-api-mysqlcursordict.html
	@handle_goal_repository_errors
	def get_progress(self, progress_id):
		with self._db._connection.cursor(dictionary=True) as cursor:
			query = "SELECT * FROM progresses WHERE progress_id = %s;"
			cursor.execute(query, (progress_id,))
			progress_entry = cursor.fetchone()

			if not progress_entry:
				return None #instead of raising errors, here it is expected that sometimes there wil be no entry

			return progress_entry


	@handle_goal_repository_errors
	def delete_progress(self, progress_id):
		with self._db._connection.cursor() as cursor:
			query = "DELETE FROM progresses WHERE progress_id = %s;"
			cursor.execute(query, (progress_id,))
			self._db._connection.commit()

			if cursor.rowcount == 0:
				raise ProgressNotFoundError(progress_id)
			return cursor.rowcount
