from apps.users.models import AppUsers
from apps.database.database_manager import MariadbConnection
from apps.users.repositories.user_repository import UserRepository, UserNotFoundError
from apps.users.services.user_service import UserService
# from django.db import IntegrityError
from mysql.connector.errors import IntegrityError

class HabitNotFoundError(Exception):
	"""Custom exception raised when a habit is not found."""
	pass

# class HabitCreationError(Exception):
# 	"""Custom raised when a role cannot be created."""
# 	pass
class HabitRepository:
	#dependency injection, loose coupling
	#can extend functionalities without modifying existing code
	#habitrepo only depends on abstract layers such as userservice
	def __init__(self, database: MariadbConnection, user_repository: UserRepository):
		self._db = database
		self._user_repository = user_repository


	def validate_a_habit(self, habit_id):
			try:
				with self._db._connection.cursor() as cursor:
					query = "SELECT habit_id FROM habits WHERE habit_id = %s"
					cursor.execute(query, (habit_id,))
					current_value = cursor.fetchone()
					
					if not current_value:
						raise HabitNotFoundError(f"Habit of with id of: {habit_id} is not found.")
					return current_value[0] #no rows updated but also no error found
			except Exception as error:
				self._db._connection.rollback()  # Required if using manual transactions
				raise

	def create_a_habit(self, habit_name, habit_action, habit_streak, habit_periodicity_type, habit_periodicity_value, habit_user):
		'''
		Create a habit in the habits table.

		Args:
			(str, str, int, str, int, int): The name, action, streak, periodicity type, periodicity value, habit user of the habit.
		
		Returns:
			int: The id of existing or newly created role. To be used as a foreign key in app_users.
		'''
		try:
			with self._db._connection.cursor() as cursor:
				validated_user_id = self._user_repository.validate_user(habit_user)
				query = "INSERT INTO habits(habit_name, habit_action, habit_streak, habit_periodicity_type, habit_periodicity_value, habit_user_id, created_at) VALUES (%s, %s, %s, %s, %s, %s, NOW());"
				cursor.execute(query, (habit_name, habit_action, habit_streak, habit_periodicity_type, habit_periodicity_value, validated_user_id))
				self._db._connection.commit()
				return {
					'habit_id': cursor.lastrowid,
					'habit_action': habit_action,
					'habit_streak': habit_streak,
					'habit_periodicity_type': habit_periodicity_type,
					'habit_periodicity_value': habit_periodicity_value,
					'habit_user_id': validated_user_id,
				}
		except IntegrityError as ierror:
			if "Duplicate entry" in str(ierror):
				raise IntegrityError(f"Duplicate habit '{habit_name}' for user '{habit_user}'.") from ierror
			raise
		except Exception as error:
			self._db._connection.rollback()
			raise



	def update_habit_field(self, habit_id, habit_field_name, habit_field_value):
		try:
			with self._db._connection.cursor() as cursor:
				check_query = f"SELECT {habit_field_name} FROM habits WHERE habit_id = %s"
				cursor.execute(check_query, (habit_id,))
				current_value = cursor.fetchone()

				if not current_value:
					raise HabitNotFoundError(f"Habit of with id of: {habit_id} is not found.")
				if current_value[0] == habit_field_value:
					return 0 #no rows updated but also no error found

			with self._db._connection.cursor() as cursor:
				query = f"UPDATE habits SET {habit_field_name} = %s WHERE habit_id = %s"
				cursor.execute(query, (habit_field_value, habit_id,))
				self._db._connection.commit() #modifies data thus have to commit
				return cursor.rowcount

		except Exception as error:
			self._db._connection.rollback()
			raise



	def get_habit_id(self, user_name, habit_name):
		try:
			with self._db._connection.cursor() as cursor:
				user_id = self._user_repository.get_user_id(user_name=user_name)
				
				query = f"SELECT habit_id from habits WHERE (habit_user_id = %s AND habit_name = %s)"
				cursor.execute(query, (user_id, habit_name,))
				habit_id = cursor.fetchone()
				
				if not habit_id:
					raise HabitNotFoundError(f"Habit of {user_name} with name {habit_name} is not found.")
				return habit_id[0] #id
		except Exception as error:
			raise



	def delete_a_habit(self, habit_id):
		try:
			#habit id is found by this time since get_habit_id will be called in service. in case habit doesnt exist this will never be triggered.
			with self._db._connection.cursor() as cursor:
				query = f"DELETE FROM habits WHERE habit_id = %s"
				cursor.execute(query, (habit_id,))
				self._db._connection.commit()
				
				if cursor.rowcount == 0:
					raise HabitNotFoundError(f"Habit of with id {habit_id} is not found.")
				return cursor.rowcount #nr of rows effected in DELETE SQL, this could also be just a bool but x>0 will act anyway as bool
		except Exception as error:
				self._db._connection.rollback()
				raise
	


