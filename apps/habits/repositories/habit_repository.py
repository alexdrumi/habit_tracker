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

def handle_habit_repository_errors(f):
	"""Decorator to clean up and handle errors in habit repository methods."""
	def exception_wrapper(self, *args, **kwargs):
		try:
			return f(self, *args, **kwargs)
		except IntegrityError as ierror:
			self._db._connection.rollback()
			#in create_a_habit the first argument is habit_name and last is habit_user_id?
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
		'''
		Validates a habit id.

		Args:
			user_id (int): ID of the habit.

		Returns:
			int: The validated habit ID.
		'''
		with self._db._connection.cursor() as cursor:
			query = "SELECT habit_id FROM habits WHERE habit_id = %s"  
			cursor.execute(query, (habit_id,))
			result = cursor.fetchone()
			 
			if not result:
				raise HabitNotFoundError(habit_id)
			return result[0]
			

	@handle_habit_repository_errors
	def create_a_habit(self, habit_name, habit_action, habit_streak, habit_periodicity_type, habit_periodicity_value, habit_user_id):
		'''
		Create a habit in the habits table.

		Args:
			(str, str, int, str, int, int): The name, action, streak, periodicity type, periodicity value, habit user id of the habit.
		
		Returns:
			Dict: Entire habit entity except the habit periodicity value.
		'''
		with self._db._connection.cursor() as cursor:
			query = "INSERT INTO habits(habit_name, habit_action, habit_streak, habit_periodicity_type, habit_periodicity_value, habit_user_id, created_at) VALUES (%s, %s, %s, %s, %s, %s, NOW());"
			cursor.execute(query, (habit_name, habit_action, habit_streak, habit_periodicity_type, habit_periodicity_value, habit_user_id))
			self._db._connection.commit()
			return {
				'habit_id': cursor.lastrowid,
				'habit_action': habit_action,
				'habit_streak': habit_streak,
				'habit_periodicity_type': habit_periodicity_type,
				'habit_user_id': habit_user_id,
			}


	@handle_habit_repository_errors
	def update_habit_field(self, habit_id, habit_field_name, habit_field_value):
		'''
		Updates one or more habit fields.

		Args:
			(int, str, int): The id, habit field name, habit field value of the habit.
		
		Returns:
			Int: Amount of rows updated.
		'''
		#against sql injection
		allowed_fields = {
			"habit_name", "habit_action", "habit_streak",
			"habit_periodicity_type", "habit_periodicity_value", "habit_user_id"
		}

		#this prevents nasty SQL injections. .format() is essentialy the same as f''
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
	def get_habit_id(self, user_id, habit_name):
		'''
		Gets the habit id based on user ID and habit name.

		Args:
			(int, str): The user id and related habit_name.
		
		Returns:
			Int: Habit ID.
		'''
		with self._db._connection.cursor() as cursor:
			user_id = self._user_repository.get_user_id(user_name=user_id)
			
			query = "SELECT habit_id from habits WHERE (habit_user_id = %s AND habit_name = %s)"
			cursor.execute(query, (user_id, habit_name,))
			habit_id = cursor.fetchone()
			
			if not habit_id:
				raise HabitNotFoundError(habit_id) #doesnt this throw none or so?
			return habit_id[0] #id

	@handle_habit_repository_errors		
	def delete_a_habit(self, habit_id):
		'''
		Deletes a habit based on habit_id.

		Args:
			int: The id of the habit wished to be deleted.
		
		Returns:
			Int: Amount of rows affected.
		'''
		self._db._connection.autocommit = False
		#ifautocommit is enabled, each delete statement in the function would be immediately committed to the database before  the next statement.
		try: #not sure how else to solve this because the decorator already has a try block but we need to reset autocommit
			with self._db._connection.cursor() as cursor:

				#delete the related analytics first, cascade only works with ORMS
				analytics_query = "DELETE FROM analytics WHERE habit_id_id = %s"
				cursor.execute(analytics_query, (habit_id,))

				#delete also goals
				goals_query = "DELETE FROM goals WHERE habit_id_id = %s"
				cursor.execute(goals_query, (habit_id,))


				query = "DELETE FROM habits WHERE habit_id = %s"
				cursor.execute(query, (habit_id,))

				if cursor.rowcount == 0:
					raise HabitNotFoundError(habit_id)

				self._db._connection.commit() #if all deletions passed, commit
				return cursor.rowcount #nr of rows effected in DELETE SQL, this could also be just a bool but x>0 will act anyway as bool

		finally:
			self._db._connection.autocommit = True #allow autocommit again



	@handle_habit_repository_errors
	def get_all_habits(self):
		'''
		Gets information about all habits in the database.

		Args:
			None (self)
		
		Returns:
			list(tuple): Habit entities with their associated columns.
		'''
		with self._db._connection.cursor() as cursor:
			query = "SELECT habit_id, habit_name, habit_action, habit_user_id FROM habits;"
			cursor.execute(query)
			habits = cursor.fetchall()
				
			if not habits:
				dummy_id_holder = -1
				raise HabitNotFoundError(dummy_id_holder) #dummy id holder
			
			return habits #no rows updated but also no error found
	
	@handle_habit_repository_errors
	def get_habit_by_id(self, habit_id):
		'''
		Gets all information about a specific habit in the database. Acts like an in memory object for facade.

		Args:
			int: habit_id
		
		Returns:
			dict: habit_id, habit_name, habit_streak, habit_periodicity_type
		'''
		with self._db._connection.cursor() as cursor:
			query = "SELECT habit_id, habit_name, habit_action, habit_user_id FROM habits;"
			cursor.execute(query)
			habits = cursor.fetchall()
				
			if not habits:
				dummy_id_holder = -1
				raise HabitNotFoundError(dummy_id_holder) #dummy id holder
			
			return habits #no rows updated but also no error found