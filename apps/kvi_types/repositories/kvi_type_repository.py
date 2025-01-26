from apps.users.models import AppUsers
from apps.database.database_manager import MariadbConnection
from apps.users.repositories.user_repository import UserRepository, UserNotFoundError
from apps.users.services.user_service import UserService
# from django.db import IntegrityError
from mysql.connector.errors import IntegrityError

class KviTypesNotFoundError(Exception):
	"""Custom exception raised when a kvi type is not found."""
	pass

# class HabitCreationError(Exception):
# 	"""Custom raised when a role cannot be created."""
# 	pass
class KviTypeRepository:
	#dependency injection, loose coupling
	#can extend functionalities without modifying existing code
	#habitrepo only depends on abstract layers such as userservice
	def __init__(self, database: MariadbConnection, user_repository: UserRepository):
		self._db = database
		self._user_repository = user_repository

	''''
	kvi_type_name = models.CharField(max_length=20, blank=False, null=False)
		kvi_description = models.CharField(max_length=40, blank=True, null=True)
		kvi_multiplier = models.FloatField(
			validators=[MinValueValidator(0.0), MaxValueValidator(10.0)]
		)
	'''

	def create_a_kvi_type(self, kvi_type_name, kvi_description, kvi_multiplier, user_id):
		'''
		Create a kvi_type in the kvi_type table.

		Args:
			(str, str, double): The name, description and multiplier of the kvi_type.
		
		Returns:
			kvi_type: The id,kvi_type_name,kvi_description,kvi_multiplier of the newly created kvi type. The ID wil be used as a foreign key in the goals table.
		'''
		try:
			with self._db._connection.cursor() as cursor:
				query = "INSERT INTO kvi_types(kvi_type_name, kvi_description, kvi_multiplier) VALUES (%s, %s, %s, %s);"
				cursor.execute(query, (kvi_type_name, kvi_description, kvi_multiplier, user_id))
				self._db._connection.commit()
				return {
					'kvi_type_id': cursor.lastrowid,
					'kvi_type_name': kvi_type_name,
					'kvi_description': kvi_description,
					'kvi_multiplier':kvi_multiplier,
					'user_id': user_id
				}
		except ValueError as error:
			self._db._connection.rollback()
			raise
		except Exception as error:
			self._db._connection.rollback()
			raise

	def get_kvi_type_id(self, kvi_type_name, kvi_type_user_id):
		try:
			with self._db._connection.cursor() as cursor:
				query = f"SELECT user_id FROM kvi_types WHERE (user_id = %s AND kvi_type_name = %s)"
				cursor.execute(query, (kvi_type_user_id, kvi_type_name))
				result = cursor.fetchone()
				if result:
					kvi_type_id_idx = 0
					return result[kvi_type_id_idx]
				else:
					raise KviTypesNotFoundError(f"Kvi type with name: {kvi_type_name} and kvi type user id: {kvi_type_user_id} is not found.")
		except Exception as error: #rolback for unexpected errors
			self._db._connection.rollback()
			raise




	# def update_kvi_type(self, )

		# 		query = "INSERT INTO habits(habit_name, habit_action, habit_streak, habit_periodicity_type, habit_periodicity_value, habit_user_id, created_at) VALUES (%s, %s, %s, %s, %s, %s, NOW());"
		# 		cursor.execute(query, (habit_name, habit_action, habit_streak, habit_periodicity_type, habit_periodicity_value, validated_user_id))
		# 		self._db._connection.commit()
		# 		return {
		# 			'habit_id': cursor.lastrowid,
		# 			'habit_action': habit_action,
		# 			'habit_streak': habit_streak,
		# 			'habit_periodicity_type': habit_periodicity_type,
		# 			'habit_periodicity_value': habit_periodicity_value,
		# 			'habit_user_id': validated_user_id,
		# 		}
		# except IntegrityError as ierror:
		# 	if "Duplicate entry" in str(ierror):
		# 		raise IntegrityError(f"Duplicate habit '{habit_name}' for user '{habit_user}'.") from ierror
		# 	raise
		# except Exception as error:
		# 	self._db._connection.rollback()
		# 	raise



	# def update_habit_field(self, habit_id, habit_field_name, habit_field_value):
	# 	try:
	# 		with self._db._connection.cursor() as cursor:
	# 			check_query = f"SELECT {habit_field_name} FROM habits WHERE habit_id = %s"
	# 			cursor.execute(check_query, (habit_id,))
	# 			current_value = cursor.fetchone()

	# 			if not current_value:
	# 				raise HabitNotFoundError(f"Habit of with id of: {habit_id} is not found.")
	# 			if current_value[0] == habit_field_value:
	# 				return 0 #no rows updated but also no error found

	# 		with self._db._connection.cursor() as cursor:
	# 			query = f"UPDATE habits SET {habit_field_name} = %s WHERE habit_id = %s"
	# 			cursor.execute(query, (habit_field_value, habit_id,))
	# 			self._db._connection.commit() #modifies data thus have to commit
	# 			return cursor.rowcount

	# 	except Exception as error:
	# 		self._db._connection.rollback()
	# 		raise



	# def get_habit_id(self, user_name, habit_name):
	# 	try:
	# 		with self._db._connection.cursor() as cursor:
	# 			user_id = self._user_repository.get_user_id(user_name=user_name)
				
	# 			query = f"SELECT habit_id from habits WHERE (habit_user_id = %s AND habit_name = %s)"
	# 			cursor.execute(query, (user_id, habit_name,))
	# 			habit_id = cursor.fetchone()
				
	# 			if not habit_id:
	# 				raise HabitNotFoundError(f"Habit of {user_name} with name {habit_name} is not found.")
	# 			return habit_id[0] #id
	# 	except Exception as error:
	# 		raise



	# def delete_a_habit(self, habit_id):
	# 	try:
	# 		#habit id is found by this time since get_habit_id will be called in service. in case habit doesnt exist this will never be triggered.
	# 		with self._db._connection.cursor() as cursor:
	# 			query = f"DELETE FROM habits WHERE habit_id = %s"
	# 			cursor.execute(query, (habit_id,))
	# 			self._db._connection.commit()
				
	# 			if cursor.rowcount == 0:
	# 				raise HabitNotFoundError(f"Habit of with id {habit_id} is not found.")
	# 			return cursor.rowcount #nr of rows effected in DELETE SQL, this could also be just a bool but x>0 will act anyway as bool
	# 	except Exception as error:
	# 			self._db._connection.rollback()
	# 			raise
	


