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
	"""
	A repository class for managing progress-related database operations, 
	such as creating, retrieving, and deleting progress entries.
	"""
	def __init__(self, database: MariadbConnection, goal_repository: GoalRepository):
		self._db = database
		self._goal_repository = goal_repository



	@handle_goal_repository_errors
	def create_progress(self, goal_id, current_kvi_value, distance_from_target_kvi_value, current_streak, goal_name, habit_name, progress_description=None, occurence_date=None):
		"""
		Inserts a new progress entry into the database.

		Args:
			goal_id (int): The unique identifier of the goal associated with this progress.
			current_kvi_value (float): Current Key Value Indicator for this progress iteration.
			distance_from_target_kvi_value (float): The difference between the target KVI and the current KVI.
			current_streak (int): The current streak value.
			goal_name (str): The name of the goal.
			habit_name (str): The name of the habit.
			progress_description (str, optional): Additional description of the progress. Defaults to None.
			occurence_date (datetime, optional): The timestamp for when the progress occurred. Defaults to current time.

		Returns:
			dict: A dictionary containing the newly created progress entry fields.

		Raises:
			ProgressAlreadyExistError: If there is a constraint violation indicating the progress already exists.
			ProgressesRepositoryError: If other repository-level errors occur.
			Exception: For any other unexpected errors.
		"""
		with self._db._connection.cursor() as cursor:
			if occurence_date == None: 
				query = "INSERT INTO progresses(current_kvi_value, goal_id_id, distance_from_goal_kvi_value, current_streak, goal_name, habit_name, occurence_date) VALUES (%s, %s, %s, %s, %s, %s, NOW());"
				cursor.execute(query, (current_kvi_value, goal_id, distance_from_target_kvi_value, current_streak, goal_name, habit_name))
				self._db._connection.commit()
				return {
					'progress_id': cursor.lastrowid,
					'goal_id': goal_id,
					'current_kvi_value': current_kvi_value,
					'distance_from_target_kvi_value': distance_from_target_kvi_value,
					'current_streak': current_streak,
					'goal_name': goal_name,
					'habit_name': habit_name
				}
			else:
				query = "INSERT INTO progresses(current_kvi_value, goal_id_id, distance_from_goal_kvi_value, current_streak, goal_name, habit_name, occurence_date) VALUES (%s, %s, %s, %s, %s, %s, %s);"
				cursor.execute(query, (current_kvi_value, goal_id, distance_from_target_kvi_value, current_streak, goal_name, habit_name, occurence_date))
				self._db._connection.commit()
				return {
					'progress_id': cursor.lastrowid,
					'goal_id': goal_id,
					'current_kvi_value': current_kvi_value,
					'distance_from_target_kvi_value': distance_from_target_kvi_value,
					'current_streak': current_streak,
					'goal_name': goal_name,
					'habit_name': habit_name
				}



	@handle_goal_repository_errors
	def get_progress_id(self, goal_id):
		"""
		Retrieves the ID of a progress entry that is associated with a specified goal.

		Args:
			goal_id (int): The unique identifier of the goal.

		Returns:
			int: The progress ID corresponding to the goal.

		Raises:
			ProgressNotFoundError: If no matching progress entry is found.
		"""
		with self._db._connection.cursor() as cursor:
			query = "SELECT progress_id FROM progresses WHERE goal_id_id = %s"
			cursor.execute(query, (goal_id,))
			result = cursor.fetchone()
			if result:
				progress_id_idx = 0
				return result[progress_id_idx]
			else:
					raise ProgressNotFoundError(goal_id)



	@handle_goal_repository_errors
	def get_last_progress_entry(self, goal_id):
		"""
		Retrieves the most recent progress entry for a given goal based on occurence_date.

		Args:
			goal_id (int): The unique identifier of the goal.

		Returns:
			tuple or None: The last progress record if found, otherwise None.

		Raises:
			ProgressesRepositoryError: For repository-level progress errors.
			Exception: For any other unexpected errors.
		"""
		with self._db._connection.cursor() as cursor:
			query = "SELECT * FROM progresses WHERE goal_id_id = %s ORDER BY occurence_date;"
			cursor.execute(query, (goal_id,))
			result = cursor.fetchall()

			if result:
				return result[-1] #last entry
			else:
				return None
		

	#https://dev.mysql.com/doc/connector-python/en/connector-python-api-mysqlcursordict.html
	@handle_goal_repository_errors
	def get_progress(self, progress_id):
		"""
		Retrieves a progress entry by its unique ID.

		Args:
			progress_id (int): The unique identifier of the progress entry.

		Returns:
			dict or None: A dictionary containing progress fields if found, otherwise None.

		Raises:
			ProgressesRepositoryError: For repository-level progress errors.
			Exception: For any other unexpected errors.
		"""
		with self._db._connection.cursor(dictionary=True) as cursor:
			query = "SELECT * FROM progresses WHERE progress_id = %s;"
			cursor.execute(query, (progress_id,))
			progress_entry = cursor.fetchone()

			if not progress_entry:
				return None #instead of raising errors, here it is expected that sometimes there wil be no entry

			return progress_entry


	@handle_goal_repository_errors
	def delete_progress(self, progress_id):
		"""
		Deletes a progress entry by its unique ID.

		Args:
			progress_id (int): The unique identifier of the progress entry to delete.

		Returns:
			int: The number of rows deleted (1 if successful).

		Raises:
			ProgressNotFoundError: If the specified progress entry is not found.
			ProgressesRepositoryError: For other repository-level errors.
			Exception: For any other unexpected errors.
		"""
		with self._db._connection.cursor() as cursor:
			query = "DELETE FROM progresses WHERE progress_id = %s;"
			cursor.execute(query, (progress_id,))
			self._db._connection.commit()

			if cursor.rowcount == 0:
				raise ProgressNotFoundError(progress_id)
			return cursor.rowcount
