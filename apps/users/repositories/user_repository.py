from apps.users.models import AppUsers
from apps.database.database_manager import MariadbConnection

class UserNotFoundError(Exception):
	"""Custom exception raised when a user is not found."""
	pass

class RoleCreationError(Exception):
	"""Custom raised when a role cannot be created."""
	pass

class UserRepository:
	def __init__(self):
		self._db = MariadbConnection()

	def create_a_role(self, user_role):
		'''
		Create a user role in the app_users_roles table. ID will be used as a foreign key in app_user.

		Args:
			user_role (str): The name of the user role (admin, user, bot).
		
		Returns:
			int: The id of existing or newly created role. To be used as a foreign key in app_users.
		'''
		try:
			with  self._db._connection.cursor() as cursor:
				query = "SELECT user_role from app_users_role WHERE user_role = %s"
				cursor.execute(query, (user_role,))
				result = cursor.fetchone() #can be only one entry here, more efficient than fetchall()
				if result:
					return result[0]
					# raise RoleCreationError(f"Role '{user_role}' already exists in the database.")
				query = "INSERT INTO app_users_role(user_role) VALUES (%s);"
				cursor.execute(query, (user_role,))
				self._db._connection.commit()
				return cursor.lastrowid #id we need to creating users
		except Exception as error:
			#could log but print for now
			self._db._connection.rollback()
			raise



	def create_a_user(self, user_name, user_age, user_gender, user_role):
		'''
		Create a user in the app_users table.

		Args:
			(str, int, str, str): The name, age, gender and role of the user.
		
		Returns:
			int, str, str: The id, user_name, user_role of the created_user.
		'''
		try:
			with self._db._connection.cursor() as cursor:
				user_role_id = self.create_a_role(user_role)
				query = "INSERT INTO app_users(user_name, user_age, user_gender, user_role_id, created_at) VALUES (%s, %s, %s, %s, NOW());"
				cursor.execute(query, (user_name, user_age, user_gender, user_role_id))
				self._db._connection.commit()
				return {
					'user_id': cursor.lastrowid,
					'user_name': user_name,
					'user_role': user_role
				}
		except Exception as error:
			self._db._connection.rollback()
			raise



	def delete_a_user(self, user_id):
		'''
		Delete a user from the app_users table.

		Args:
			user_id (int): ID of the user.

		Returns:
			int: Number of rows effected by deletion.
		'''
		try:
			with self._db._connection.cursor() as cursor: #this closes cursor anyway, https://www.psycopg.org/docs/cursor.html
				query = "DELETE FROM app_users WHERE user_id = %s"
				cursor.execute(query, (user_id,))
				self._db._connection.commit()
				if cursor.rowcount == 0:
					raise UserNotFoundError(f"User with user_name {user_id} is not found.")
				return cursor.rowcount #nr of rows effected in DELETE SQL, this could also be just a bool but x>0 will act anyway as bool
		except Exception as error:
			self._db._connection.rollback()
			raise
		


	#TODO, make this less repetitive, there must be a pretty pythonic way for the if blocks
	def update_a_user(self, user_name, user_age=None, user_gender=None, user_role=None):
		'''
		Update a user from the app_users table.

		Args:
			(str, int, str, str): The new name, new age, new gender and new role of the user.
		
		Returns:
			int: Number of rows effected by update.
		'''
		try:
			updated_cols = []
			updated_vals = []
			if user_name is not None:
				updated_cols.append("user_name = %s")
				updated_vals.append(user_name)

			if user_age is not None:
				updated_cols.append("user_age = %s")
				updated_vals.append(user_age)

			if user_gender is not None:
				updated_cols.append("user_gender = %s")
				updated_vals.append(user_gender)

			if user_role is not None:
				#if you need a role_id, you can call self.create_a_role(user_role) to create it
				role_id = self.create_a_role(user_role)
				updated_cols.append("user_role_id = %s")
				updated_vals.append(role_id)
			
			if not updated_cols:
				return 0
			set_commands = ', '.join(updated_cols) 
			query = f"UPDATE app_users SET {set_commands} WHERE user_name = %s"
			updated_vals.append(user_name) #once more for the where clause
			
			with self._db._connection.cursor() as cursor:
				cursor.execute(query, updated_vals)
				self._db._connection.commit()
				
				if cursor.rowcount == 0:
					raise UserNotFoundError(f"User with user_name {user_name} is not found.")
				return cursor.rowcount #nr of rows effected in UPDATE SQL (ideally 1)
		except Exception as error:
			self._db._connection.rollback()
			raise



	def get_user_id(self, user_name):
		'''
		Get the user_id based on a user_name.

		Args:
			user_name (str): The name of the user.
		
		Returns:
			int: The ID of the user.
		'''
		try:
			with self._db._connection.cursor() as cursor:
				query =  f"SELECT user_id from app_users WHERE user_name = %s"
				cursor.execute(query, (user_name,))
				result = cursor.fetchone()
				if result:
					user_id_idx = 0
					return result[user_id_idx]
				else: #select only handles read only query, no need for rollback, no changes in the database
					raise UserNotFoundError(f"User with user_name: {user_name} is not found.")
		except Exception as error: #rolback for unexpected errors
			self._db._connection.rollback()
			raise




