from apps.users.models import AppUsers
from apps.database.database_manager import MariadbConnection
from apps.users.repositories.user_repository import UserRepository, UserNotFoundError
from apps.users.services.user_service import UserService
# from django.db import IntegrityError->we use mysql integrity error for duplicates
from mysql.connector.errors import IntegrityError

#baseclass
class HabitRepositoryError(Exception):
	def __init__(self, message="An unexpected error occurred in habit repository."):
		super().__init__(message)



class HabitNotFoundError(HabitRepositoryError):
	"""Raised when a habit is not found."""
	def __init__(self, habit_id):
		message = f"Habit not found with ID: {habit_id}"
		super().__init__(message)



class HabitAlreadyExistError(HabitRepositoryError):
	"""Raised when creating habit fails due to a already existing entry."""
	def __init__(self, habit_name, habit_user_id):
		message = f"Habit '{habit_name}' already exists for user with id: {habit_user_id}"
		super().__init__(message)



class HabitPeriodicityTypeError(HabitRepositoryError):
	"""Raised when a habit periodicity type is not found."""
	def __init__(self, habit_id):
		message = f"Habit periodicity type for habit with ID: {habit_id} is not found."
		super().__init__(message)



def handle_habit_repository_errors(f):
	"""Decorator to clean up and handle errors in habit repository methods."""
	def exception_wrapper(self, *args, **kwargs):
		try:
			return f(self, *args, **kwargs)
		except IntegrityError as ierror:
			self._db._connection.rollback()
			raise HabitAlreadyExistError(habit_name=args[0], habit_user_id=args[-1]) from ierror
		except HabitRepositoryError as herror:
			raise herror
		except Exception as error:
			self._db._connection.rollback()
			raise error
	return exception_wrapper



class HabitRepository:
	#dependency injection, loose coupling
	#can extend functionalities without modifying existing code
	#habitrepo only depends on abstract layers such as userservice
	def __init__(self, database: MariadbConnection, user_repository: UserRepository):
		self._db = database
		self._user_repository = user_repository



	@handle_habit_repository_errors
	def validate_a_habit(self, habit_id):
		"""
		Checks if a habit with the given ID exists.

		Args:
			habit_id (int): The habit’s ID.

		Returns:
			int: The validated habit ID.

		Raises:
			HabitNotFoundError: If the habit is not found.
		"""
		with self._db._connection.cursor() as cursor:
			query = "SELECT habit_id FROM habits WHERE habit_id = %s"  
			cursor.execute(query, (habit_id,))
			result = cursor.fetchone()
			 
			if not result:
				raise HabitNotFoundError(habit_id)
			return result[0]



	@handle_habit_repository_errors
	def create_a_habit(self, habit_name, habit_action, habit_streak, habit_periodicity_type, habit_periodicity_value, habit_user_id):
		"""
		Inserts a new habit record into the database.

		Args:
			habit_name (str): Name of the habit.
			habit_action (str): Description or action the habit represents.
			habit_streak (int): Initial streak value (often 0).
			habit_periodicity_type (str): Type (e.g., 'daily', 'weekly').
			habit_periodicity_value (int): Numeric frequency (e.g., 1 for daily).
			habit_user_id (int): ID of the user who owns this habit.

		Returns:
			dict: The newly created habit’s data.

		Raises:
			HabitAlreadyExistError: If a duplicate record is found.
		"""
		with self._db._connection.cursor() as cursor:
			#duplicate check?
			duplicate_check_query = "SELECT habit_id FROM habits WHERE habit_name = %s AND habit_user_id = %s"
			cursor.execute(duplicate_check_query, (habit_name, habit_user_id,))
			existing_habit = cursor.fetchone()

			if existing_habit:
				raise HabitAlreadyExistError(habit_name=habit_name, habit_user_id=habit_user_id)


			query = "INSERT INTO habits(habit_name, habit_action, habit_streak, habit_periodicity_type, habit_periodicity_value, habit_user_id, created_at) VALUES (%s, %s, %s, %s, %s, %s, NOW());"
			cursor.execute(query, (habit_name, habit_action, habit_streak, habit_periodicity_type, habit_periodicity_value, habit_user_id))
			self._db._connection.commit()
			return {
				'habit_name': habit_name,
				'habit_id': cursor.lastrowid,
				'habit_action': habit_action,
				'habit_streak': habit_streak,
				'habit_periodicity_type': habit_periodicity_type,
				'habit_user_id': habit_user_id,
			}



	@handle_habit_repository_errors
	def update_habit_field(self, habit_id, habit_field_name, habit_field_value):
		"""
		Updates a specific field for the given habit.

		Args:
			habit_id (int): ID of the habit to update.
			habit_field_name (str): The column name to update.
			habit_field_value (Any): The new value for that column.

		Returns:
			int: Number of rows affected by the update.

		Raises:
			HabitNotFoundError: If the habit does not exist.
			ValueError: If attempting to update a disallowed field.
		"""
		#against sql injection? In the future I have to guard also in other repos.
		allowed_fields = {
			"habit_name", "habit_action", "habit_streak",
			"habit_periodicity_type", "habit_periodicity_value", "habit_user_id"
		}

		if habit_field_name not in allowed_fields:
			raise ValueError(f"Invalid habit field to update.")
		
	
		with self._db._connection.cursor() as cursor:
			check_query = "SELECT {} FROM habits WHERE habit_id = %s".format(habit_field_name)
			cursor.execute(check_query, (habit_id,))
			current_value = cursor.fetchone()

			if not current_value:
				raise HabitNotFoundError(f"Habit of with id of: {habit_id} is not found.")
			if current_value[0] == habit_field_value:
				return 0 #no rows updated but also no error found
		
		#This could be SQL injected
		#UPDATE habits SET habit_streak; DROP TABLE habits; = %s WHERE habit_id = %s
		#if we insert SET habit_streak; + DROP TABLE habits; = %s
		with self._db._connection.cursor() as cursor:
			query = "UPDATE habits SET {} = %s WHERE habit_id = %s".format(habit_field_name)
			cursor.execute(query, (habit_field_value, habit_id,))
			self._db._connection.commit() #modifies data thus have to commit
			return cursor.rowcount




	@handle_habit_repository_errors
	def get_periodicity_type(self, habit_id):
		"""
		Retrieves the periodicity type (e.g., 'daily') for a given habit.

		Args:
			habit_id (int): The habit’s ID.

		Returns:
			tuple: The periodicity type, for example ('daily',).

		Raises:
			HabitPeriodicityTypeError: If the periodicity type is not found.
		"""
		with self._db._connection.cursor() as cursor:
			query =  "SELECT habit_periodicity_type FROM habits WHERE habit_id = %s"
			cursor.execute(query, (habit_id,))

			habit_periodicity_type = cursor.fetchone()
			if habit_periodicity_type:
				return habit_periodicity_type
			else:
				raise HabitPeriodicityTypeError(habit_id=habit_id)



	@handle_habit_repository_errors
	def get_habit_id(self, user_name, habit_name):
		"""
		Retrieves a habit ID based on user name and habit name.

		Args:
			user_name (str): The user’s name.
			habit_name (str): The habit’s name.

		Returns:
			int: The habit ID.

		Raises:
			HabitNotFoundError: If no matching habit is found.
		"""
		with self._db._connection.cursor() as cursor:
			user_id = self._user_repository.get_user_id(user_name=user_name)
			query = "SELECT habit_id from habits WHERE (habit_user_id = %s AND habit_name = %s)"
			cursor.execute(query, (user_id, habit_name,))
			
			habit_id = cursor.fetchone()
			if not habit_id:
				raise HabitNotFoundError(habit_id)
			return habit_id[0]



	@handle_habit_repository_errors		
	def delete_a_habit(self, habit_id, goal_id):
		"""
		Deletes a habit and its dependent goals/progress records.

		Args:
			habit_id (int): The ID of the habit to delete.
			goal_id (int): The ID of the goal tied to that habit (for removing progress).

		Returns:
			int: Number of rows affected (ideally 1 if success).

		Raises:
			HabitNotFoundError: If the habit does not exist.
		"""
		self._db._connection.autocommit = False
		#ifautocommit is enabled, each delete statement in the function would be immediately committed to the database before  the next statement.
		try: #not sure how else to solve this because the decorator already has a try block but we need to reset autocommit
			with self._db._connection.cursor() as cursor:
				#delete progresses first
				prorgresses_query = "DELETE FROM progresses WHERE goal_id_id = %s"
				cursor.execute(prorgresses_query, (goal_id,))

				#delete the related analytics first, cascade only works with ORMS
				# analytics_query = "DELETE FROM analytics WHERE habit_id_id = %s"
				# cursor.execute(analytics_query, (habit_id,))

				#delete also goals
				goals_query = "DELETE FROM goals WHERE habit_id_id = %s"
				cursor.execute(goals_query, (habit_id,))


				query = "DELETE FROM habits WHERE habit_id = %s"
				cursor.execute(query, (habit_id,))

				if cursor.rowcount == 0:
					raise HabitNotFoundError(habit_id)

				self._db._connection.commit() #if all deletions passed, commit
				return cursor.rowcount

		finally:
			self._db._connection.autocommit = True #allow autocommit again



	def delete_habit_physical_preserving_progress(self, habit_id, goal_id):
		"""
		Deletes a habit record but preserves existing progress (sets goal_id_id to NULL).

		Args:
			habit_id (int): The habit’s ID.
			goal_id (int): The goal’s ID used to set progress records to NULL.

		Returns:
			int: Number of rows affected by the deletion.

		Raises:
			HabitNotFoundError: If the habit does not exist.
		"""
		with self._db._connection.cursor() as cursor:
			self._db._connection.autocommit = False
			try:
				#find all goals referencing this habit
				#find_goals_query = "SELECT goal_id FROM goals WHERE habit_id_id = %s
				#cursor.execute(find_goals_query, (habit_id,))
				#goals = cursor.fetchall()  #[(24,), (25,)..]
				
				# if goals:
				# 	goal_ids = [str(g[0]) for g in goals]  # e.g., ['24','25']

				#goal_id_id=NULL in progresses for these goals
				set_null_query = f"UPDATE progresses SET goal_id_id = NULL WHERE goal_id_id = %s;"
				cursor.execute(set_null_query, (goal_id, ))

				#delete the goals for this habit
				delete_goals_query = "DELETE FROM goals WHERE habit_id_id = %s;"
				cursor.execute(delete_goals_query, (habit_id,))

				#delete the habit
				delete_habit_query = "DELETE FROM habits WHERE habit_id = %s;"
				cursor.execute(delete_habit_query, (habit_id,))

				if cursor.rowcount == 0:
					raise HabitNotFoundError(habit_id)

				self._db._connection.commit()
				return cursor.rowcount

			except Exception as err:
				self._db._connection.rollback()
				raise err
			finally:
				self._db._connection.autocommit = True #not sure how else can i escape this one



	@handle_habit_repository_errors
	def get_all_habits(self):
		"""
		Retrieves all habit records.

		Returns:
			list: A list of tuples, each containing habit fields
			(e.g., habit_id, habit_name, habit_action, habit_user_id), or an empty list.
		"""
		with self._db._connection.cursor(dictionary=True) as cursor:
			query = "SELECT habit_name, habit_id, habit_action, habit_streak, habit_periodicity_type, habit_user_id FROM habits;"
			cursor.execute(query)
			habits = cursor.fetchall()
			
			if not habits:
				return []
			
			return habits


	@handle_habit_repository_errors
	def get_current_streak(self, habit_id):
		"""
		Retrieves the current streak for a specific habit.

		Args:
			habit_id (int): The habit ID.

		Returns:
			tuple: Contains the streak value (e.g., (5,) for a streak of 5).

		Raises:
			HabitNotFoundError: If the habit is not found.
		"""
		with self._db._connection.cursor() as cursor:
			query = "SELECT habit_streak FROM habits WHERE habit_id = %s;"
			cursor.execute(query, (habit_id,))
			streak = cursor.fetchall()

			if not streak:
				dummy_id_holder = -1 #gotta come up with a better version here eventually
				raise HabitNotFoundError(dummy_id_holder)

			return streak[0]




	@handle_habit_repository_errors
	def get_habit_by_id(self, habit_id):
		"""
		Fetches all details of a single habit by its ID.

		Args:
			habit_id (int): The habit ID.

		Returns:
			list: A list of rows (tuples) with full habit data.

		Raises:
			HabitNotFoundError: If no matching habit is found.
		"""
		with self._db._connection.cursor() as cursor:
			query = "SELECT habit_id, habit_name, habit_action, habit_user_id FROM habits;"
			cursor.execute(query)
			habits = cursor.fetchall()
				
			if not habits:
				dummy_id_holder = -1
				raise HabitNotFoundError(dummy_id_holder) #dummy id holder
			
			return habits


	@handle_habit_repository_errors
	def get_goal_of_habit(self, habit_id):
		"""
		Retrieves the goal(s) associated with a specific habit.

		Args:
			habit_id (int): The habit ID.

		Returns:
			list: A list of goals tied to the habit.

		Raises:
			HabitNotFoundError: If no goals or habit are found.
		"""
		with self._db._connection.cursor() as cursor:
			query = "SELECT goal_id FROM goals WHERE habit_id_id = %s;"
			cursor.execute(query, habit_id)
			goal = cursor.fetchall()
				
			if not goal:
				dummy_id_holder = -1
				raise HabitNotFoundError(dummy_id_holder) #dummy id holder
			
			return goal