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
	def validate_a_kvi_type(self, kvi_type_id):
		try:
			with self._db._connection.cursor() as cursor:
				query = "SELECT kvi_type_id FROM kvi_types WHERE kvi_type_id = %s"
				cursor.execute(query, (kvi_type_id,))
				current_value = cursor.fetchone()
				
				if not current_value:
					raise KviTypesNotFoundError(f"Kvi type with id of: {kvi_type_id} is not found.")
				# if current_value[0] == kvi_type_id:
				return current_value[0] #no rows updated but also no error found
		except Exception as error:
			self._db._connection.rollback()  # Required if using manual transactions
			raise


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
				# if not (kvi_multiplier >= 0.0 and kvi_multiplier <= 10.0):
				# 	raise ValueError("kvi_multiplier must be between 0.0 and 10.0.")
				
				query = "INSERT INTO kvi_types(kvi_type_name, kvi_description, kvi_multiplier, kvi_type_user_id) VALUES (%s, %s, %s, %s);"
				cursor.execute(query, (kvi_type_name, kvi_description, kvi_multiplier, user_id))
				self._db._connection.commit()
				return {
					'kvi_type_id': cursor.lastrowid,
					'kvi_type_name': kvi_type_name,
					'kvi_description': kvi_description,
					'kvi_multiplier':kvi_multiplier,
					'user_id': user_id
				}
		except IntegrityError as ierror:
			if "Duplicate entry" in str(ierror):
				self._db._connection.rollback()
				raise IntegrityError(f"Duplicate kvi_type with {kvi_type_name}.")
			raise #for other integrity errors in mariadb (fk, not null etc)
		except Exception as error:
			self._db._connection.rollback()
			raise


	def get_kvi_type_id(self, kvi_type_name, kvi_type_user_id):
		try:
			with self._db._connection.cursor() as cursor:
				query = "SELECT kvi_type_id FROM kvi_types WHERE (kvi_type_user_id = %s AND kvi_type_name = %s)"
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


	def update_kvi_type(self, kvi_type_id, kvi_multiplier):
		try:
			with self._db._connection.cursor() as cursor:
				query = "UPDATE kvi_types SET kvi_multiplier = %s WHERE kvi_type_id = %s"
				cursor.execute(query, (kvi_multiplier, kvi_type_id))
				self._db._connection.commit() #modifies data thus have to commit
				
				if cursor.rowcount == 0:
					raise KviTypesNotFoundError(f"KVI type with ID {kvi_type_id} not found.")  # Raise if no rows were updated
				
				return cursor.rowcount
			
		except KviTypesNotFoundError as not_found_error:
			self._db._connection.rollback()
			raise 

		except Exception as error:
			self._db._connection.rollback()
			raise


	def delete_a_kvi_type(self, kvi_type_id):
		try:
			with self._db._connection.cursor() as cursor:
				query = "DELETE FROM kvi_types WHERE kvi_type_id = %s"
				cursor.execute(query, (kvi_type_id, ))
				self._db._connection.commit()

				if cursor.rowcount == 0:
					raise KviTypesNotFoundError(f"Kvi type with id {kvi_type_id} is not found.")
				return cursor.rowcount #nr of rows effected in DELETE SQL, this could also be just a bool but x>0 will act anyway as bool
		
		except Exception as error:
				self._db._connection.rollback()
				raise

