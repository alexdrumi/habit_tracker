from apps.habits.repositories.habit_repository import HabitRepository
from apps.database.database_manager import MariadbConnection
from mysql.connector.errors import IntegrityError

class AnalyticsRepositoryError(Exception):
	"""BASE exception"""
	def __init__(self, message="An unexpected error occurred in analytics repository."):
		super().__init__(message)


class AnalyticsNotFoundError(AnalyticsRepositoryError):
	"""Custom exception"""
	def __init__(self, message):
		super().__init__(message)


def handle_analytics_repository_errors(f):
	"""Decorator, with an optional rollback in case of integrity error"""
	def exception_wrapper(self, *args, **kwargs):
		try:
			return f(self, *args, **kwargs)
		except IntegrityError as ierror:
			self._db._connection.rollback()
			raise ierror
		except AnalyticsRepositoryError as arerror:
			raise arerror #just re raise it
		except Exception as error:
			self._db._connection.rollback()
			raise error
	return exception_wrapper




class AnalyticsRepository:
	def __init__(self, database: MariadbConnection, habit_repository: HabitRepository):
		"""
		Creates an analytics repository. Uses dependency injection for related
		database and habit repository.
		"""
		self._db = database
		self._habit_repository = habit_repository

	@handle_analytics_repository_errors
	def create_analytics(self, times_completed, streak_length, habit_id, last_completed_at=None):
		"""
		Creates an analytics record for a specific habit.

		Args:
			times_completed (int): The number of times the habit has been completed.
			streak_length (int): The current streak length for the habit.
			habit_id (int): The unique identifier of the habit.
			last_completed_at (datetime, optional): The last completion time of the habit. Defaults to None.

		Returns:
			dict: A dictionary containing the newly created analytics record (including 'analytics_id').

		Raises:
			IntegrityError: If there's a database integrity issue during creation.
			AnalyticsRepositoryError: For repository-level errors related to analytics.
			Exception: For any other unexpected errors.
		"""
		with self._db._connection.cursor() as cursor:	
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



	@handle_analytics_repository_errors
	def get_analytics_id(self, habit_id):
		"""
		Retrieves the analytics ID associated with a given habit.

		Args:
			habit_id (int): The unique identifier of the habit.

		Returns:
			int: The analytics ID corresponding to the provided habit_id.

		Raises:
			AnalyticsNotFoundError: If no analytics record is found for the habit.
			IntegrityError: For database integrity-related errors.
			AnalyticsRepositoryError: For repository-level analytics errors.
			Exception: For any other unexpected errors.
		"""
		with self._db._connection.cursor() as cursor:
			query = "SELECT analytics_id FROM analytics WHERE habit_id_id = %s;"
			cursor.execute(query, (habit_id,))
			result = cursor.fetchone()
			if result:
				analytics_id_idx = 0
				return result[analytics_id_idx]
			else:
				raise AnalyticsNotFoundError(f"Analytics for habit with habit id: {habit_id} is not found.")



	@handle_analytics_repository_errors
	def update_analytics(self, analytics_id, times_completed=None, streak_length=None, last_completed_at=None):
		"""
		Updates an existing analytics record.

		Args:
			analytics_id (int): The unique identifier of the analytics record to be updated.
			times_completed (int, optional): Updated number of completions. Defaults to None.
			streak_length (int, optional): Updated streak length. Defaults to None.
			last_completed_at (datetime, optional): Updated datetime for the last completion. Defaults to None.

		Returns:
			int: The number of rows affected by the update (typically 1 if successful).

		Raises:
			AnalyticsNotFoundError: If the analytics record is not found.
			IntegrityError: For database integrity-related errors.
			AnalyticsRepositoryError: For repository-level analytics errors.
			Exception: For any other unexpected errors.
		"""
		updated_fields = []
		updated_values = []

		if times_completed is not None:
			updated_fields.append("times_completed = %s")
			updated_values.append(times_completed)
		
		if streak_length is not None:
			updated_fields.append("streak_length = %s")
			updated_values.append(streak_length)

		if last_completed_at is not None:
			updated_fields.append("last_completed_at = %s")
			updated_values.append(last_completed_at)
		
		if not updated_fields:
			return 0
		
		set_commands = ', '.join(updated_fields)
		updated_values.append(analytics_id)

		query = "UPDATE analytics SET " + set_commands + " WHERE analytics_id = %s;"
		with self._db._connection.cursor() as cursor:
			cursor.execute(query, updated_values)
			self._db._connection.commit()

			if cursor.rowcount == 0: #shouldnt be the case by now
				raise AnalyticsNotFoundError(f"Analytics for habit with analyticsid: {analytics_id} is not found.")

			return cursor.rowcount #nr of rows effected in UPDATE SQL (ideally 1)



	@handle_analytics_repository_errors  
	def delete_analytics(self, analytics_id):
		"""
		Deletes an analytics record.

		Args:
			analytics_id (int): The unique id of the analytics record to delete.

		Returns:
			int: The number of rows deleted (1 if successful).

		Raises:
			AnalyticsNotFoundError: If the analytics record is not found.
			IntegrityError: For database integrity-related errors.
			AnalyticsRepositoryError: For other repository-level analytics errors.
			Exception: For any other unexpected errors.
		"""
		with self._db._connection.cursor() as cursor:
			query = "DELETE FROM analytics WHERE analytics_id = %s"
			cursor.execute(query, (analytics_id,))
			self._db._connection.commit()
			if cursor.rowcount == 0:
				raise AnalyticsNotFoundError(f"Analytics for habit with id analyticsid: {analytics_id} is not found.")
			return cursor.rowcount #nr of rows effected in UPDATE SQL (ideally 1)


  
	@handle_analytics_repository_errors
	def calculate_longest_streak(self):
		"""
		Retrieves the habit that has the maximum current streak in the database.

		Returns:
			tuple: A tuple containing (habit_id, habit_name, habit_streak) for the habit with the longest streak.

		Raises:
			AnalyticsNotFoundError: If no habit streaks are found.
			IntegrityError: For database integrity-related errors.
			AnalyticsRepositoryError: For other repository-level analytics errors.
			Exception: For any other unexpected errors.
		"""
		with self._db._connection.cursor() as cursor:
			query = "SELECT habit_id, habit_name, habit_streak FROM habits WHERE habit_streak = (SELECT MAX(habit_streak) FROM habits) ORDER BY habit_streak DESC;"
			
			cursor.execute(query)
			result = cursor.fetchone()
			#no commit needed, nothing changed
			if result:
				return result
			else:
				raise AnalyticsNotFoundError(f"Longest streak has not been found.")



	@handle_analytics_repository_errors
	def get_same_periodicity_type_habits(self):
		"""
		Groups habits by periodicity type and returns the count and a concatenated list of habit details for each group.

		Returns:
			list of tuples: Each tuple contains (periodicity_type, habit_count, habit_list).
							- periodicity_type (str):  "daily" or "weekly".
							- habit_count (int): Number of habits with that periodicity.
							- habit_list (str): A comma-separated string of "habit_id: habit_name" pairs.

		Raises:
			AnalyticsNotFoundError: If no habits are found.
			IntegrityError: For database integrity-related errors.
			AnalyticsRepositoryError: For other repository-level analytics errors.
			Exception: For any other unexpected errors.
		"""
		with self._db._connection.cursor() as cursor:
			query = "SELECT habit_periodicity_type, COUNT(*) AS habit_count, GROUP_CONCAT(CONCAT(habit_id, ': ', habit_name) SEPARATOR ', ') AS habit_list FROM habits GROUP BY habit_periodicity_type ORDER BY habit_count DESC;"

			cursor.execute(query)
			result = cursor.fetchall()

			if result:
				return result
			else:
				raise AnalyticsNotFoundError(f"Same periodicity types have not been found.")



	@handle_analytics_repository_errors
	def get_currently_tracked_habits(self):
		"""
		Retrieves a list of habits that currently have an active streak (i.e., streak > 0).

		Returns:
			list of tuples: Each tuple contains (habit_id, habit_name, habit_streak, habit_periodicity_type).

		Raises:
			AnalyticsNotFoundError: If no tracked habits are found.
			IntegrityError: For database integrity-related errors.
			AnalyticsRepositoryError: For other repository-level analytics errors.
			Exception: For any other unexpected errors.
		"""
		with self._db._connection.cursor() as cursor:
			query = "SELECT habit_id, habit_name, habit_streak, habit_periodicity_type FROM habits WHERE habit_streak > 0;"

			cursor.execute(query)
			result = cursor.fetchall()

			if result:
				return result
			else:
				raise AnalyticsNotFoundError(f"Currently tracked habits are not found.")



	@handle_analytics_repository_errors
	def longest_streak_for_habit(self, habit_id):
		"""
		Retrieves the progress entry with the highest streak for the specified habit.

		Args:
			habit_id (int): The unique identifier of the habit.

		Returns:
			list of tuples: Each tuple represents a progress record sorted by the highest streak first.

		Raises:
			AnalyticsNotFoundError: If no progress entries are found for the given habit.
			IntegrityError: For database integrity-related errors.
			AnalyticsRepositoryError: For other repository-level analytics errors.
			Exception: For any other unexpected errors.
		"""
		with self._db._connection.cursor() as cursor:
			query = "SELECT p.* FROM progresses p JOIN goals g ON p.goal_id_id = g.goal_id WHERE g.habit_id_id = %s ORDER BY p.current_streak DESC LIMIT 1;"
			cursor.execute(query, (habit_id, ))

			result = cursor.fetchall()
		if result:
			return result
		else:
			raise AnalyticsNotFoundError(f"Longest streak for habit with id: {habit_id} is not found.")


	# #https://mariadb.com/kb/en/json_arrayagg/ , otherwise I would have split calls in the layers above. This is gonna be a simple loop
