from apps.database.database_manager import MariadbConnection
from mysql.connector.errors import IntegrityError


class UserRepositoryError(Exception):
	'''Baseclass for exceptions for repository errors.'''
	def __init__(self, message="An unexpected error occured in user repository."):
		super().__init__(message)

class UserNotFoundError(UserRepositoryError):
	'''Exception raised when user is not found.'''
	def __init__(self, user_name_or_id):
		message = f"User is not found with user name/id: {user_name_or_id}"
		super().__init__(message)

class RoleCreationError(UserRepositoryError):
	'''Exception raised when role creation failes.'''
	def __init__(self, message= "Failed to create a role."):
		super().__init__(message)

class AlreadyExistError(UserRepositoryError):
	'''Exception raised when user creation failes, e.g.: duplicate input.'''
	def __init__(self, user_name):
		message = f"User already found with user name:  {user_name}. Create user with another name."
		super().__init__(message)

def handle_user_repository_errors(f):
	'''A decorator to make exceptions of database errors cleaner.'''
	def exception_wrapper(self, *args, **kwargs):
		try: #all functions, create, delete etc wil be wrapped in this try block, not sure how to pass already exist error username or id
			return f(self, *args, **kwargs)
		except IntegrityError as ierror:
			self._db._connection.rollback()
			raise AlreadyExistError(user_name=args[0]) from ierror #id is args[0]
		except UserRepositoryError as urerror:
			raise urerror
		except Exception as error:
			self._db._connection.rollback()
			raise error #anything else here? should b just error

	return exception_wrapper		
		


class UserRepository:
	def __init__(self, database: MariadbConnection):
		self._db = database


	@handle_user_repository_errors
	def validate_user_by_name(self, user_name):
		'''
		Validates whether a user with user_name exists in the database.

		Args:
			user_name (str): The username to be checked.

		Returns:
			int: THe user ID if the user exists.
		'''
		with self._db._connection.cursor() as cursor:
			query_user = "SELECT user_id from app_users WHERE user_name = %s;"
			cursor.execute(query_user, (user_name,))
			result_user = cursor.fetchone()

			if not result_user:
				raise UserNotFoundError(user_name)
			
			user_id_idx = 0
			return result_user[user_id_idx]

	@handle_user_repository_errors
	def validate_user_by_id(self, user_id):
		'''
		Validates whether a user with user_id exists in the database.

		Args:
			user_id (int): The user id to be checked.

		Returns:
			int: The user ID if the user exists.
		'''
		with self._db._connection.cursor() as cursor:
			query_user = "SELECT user_id from app_users WHERE user_id = %s;"
			cursor.execute(query_user, (user_id,))
			result_user = cursor.fetchone()

			if not result_user:
				raise UserNotFoundError(user_id)
			
			user_id_idx = 0
			return result_user[user_id_idx]


	@handle_user_repository_errors
	def create_a_role(self, user_role):
		'''
		Create a user role in the app_users_roles table. ID will be used as a foreign key in app_user.

		Args:
			user_role (str): The name of the user role (admin, user, bot).

		Returns:
			int: The id of existing or newly created role. To be used as a foreign key in app_users.
		'''
		with  self._db._connection.cursor() as cursor:
			query = "SELECT user_role from app_users_role WHERE user_role = %s"
			cursor.execute(query, (user_role,))
			role = cursor.fetchone() #can be only one entry here, more efficient than fetchall()
			
			if role:
				role_id_idx = 0
				return role[role_id_idx]
			
			# try:
				#if role doesnt exist
			query = "INSERT INTO app_users_role(user_role) VALUES (%s);"
			cursor.execute(query, (user_role,))

			if cursor.rowcount == 0:
				raise RoleCreationError()

			self._db._connection.commit()
			return cursor.lastrowid #id we need to creating users

			#double roles should be ok?
			# except IntegrityError as ierror:
			# 	raise
		

	@handle_user_repository_errors
	def create_a_user(self, user_name, user_password, user_age, user_gender, user_role):
		'''
		Create a user in the app_users table.

		Args:
			(str, int, str, str): The name, age, gender and role of the user.
		
		Returns:
			a dict (int, str, str): The id, user_name, user_role of the created_user.
		'''
		with self._db._connection.cursor() as cursor:
			user_role_id = self.create_a_role(user_role)
			try:
				query = "INSERT INTO app_users(user_name, user_password, user_age, user_gender, user_role_id, created_at) VALUES (%s, %s, %s, %s, NOW());"
				cursor.execute(query, (user_name, user_password, user_age, user_gender, user_role_id))
				self._db._connection.commit()
				return {
					'user_id': cursor.lastrowid,
					'user_name': user_name,
					'user_role': user_role
				}
	
			except IntegrityError as ierror:
				raise

	@handle_user_repository_errors
	def delete_a_user(self, user_id):
		'''
		Delete a user from the app_users table.

		Args:
			user_id (int): ID of the user.

		Returns:
			int: Number of rows effected by deletion.
		'''
		with self._db._connection.cursor() as cursor: #this closes cursor anyway, https://www.psycopg.org/docs/cursor.html
			query = "DELETE FROM app_users WHERE user_id = %s"
			cursor.execute(query, (user_id,))
			self._db._connection.commit()

			if cursor.rowcount == 0:
				raise UserNotFoundError(user_id)

			return cursor.rowcount #nr of rows effected in DELETE SQL, this could also be just a bool but x>0 will act anyway as bool


	@handle_user_repository_errors
	def update_a_user(self, user_name, user_age=None, user_gender=None, user_role=None):
		'''
		Update a user from the app_users table.

		Args:
			(str, int, str, str): The new name, new age, new gender and new role of the user.
		
		Returns:
			int: Number of rows effected by update.
		'''
		#will eventually correct this with dict and list comprehension prob
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
		
		#WE SHOULD FIND A WAY WITHOUT STRING FORMATTING (F'') BECAUSE SQL INJECTIONS CAN THROW THIS OFF.
		query = f"UPDATE app_users SET {set_commands} WHERE user_name = %s"
		updated_vals.append(user_name) #once more for the where clause
		
		with self._db._connection.cursor() as cursor:
			cursor.execute(query, updated_vals)
			self._db._connection.commit()
			
			if cursor.rowcount == 0:
				raise UserNotFoundError(user_name)
			return cursor.rowcount #nr of rows effected in UPDATE SQL (ideally 1)
		


	@handle_user_repository_errors
	def get_user_id(self, user_name):
		'''
		Get the user_id based on a user_name.

		Args:
			user_name (str): The name of the user.
		
		Returns:
			int: The ID of the user.
		'''
		with self._db._connection.cursor() as cursor:
			query =  "SELECT user_id from app_users WHERE user_name = %s"
			cursor.execute(query, (user_name,))
			result = cursor.fetchone()
			if result:
				user_id_idx = 0
				return result[user_id_idx]
			else:
				raise UserNotFoundError(user_name)



	@handle_user_repository_errors
	def query_all_user_data(self):
		'''
		Requests all user data. 

		Args:
			None
		
		Returns:
			dict(list): every user data with their user_id and related habit_id, goal_id
		'''
		with self._db._connection.cursor() as cursor:
			query = "SELECT user_id, user_name FROM app_users;"
			cursor.execute(query)
			result = cursor.fetchall()

			if result:
				return result
			else:
				return []
	

	#user id, user name, habit_id, habit_name, habit_action
	#oders->habits
	#customers->users
	#SELECT app_users.user_name, app_users.user_id, habits.habit_id, habits.habit_name, habits.habit_action FROM habits INNER JOIN app_users ON habits.habit_user_id=app_users.user_id;
	@handle_user_repository_errors
	def query_user_and_related_habits(self): #INNER JOIN
		'''
		Requests all users who have associated habits data. 

		Args:
			None
		
		Returns:
			dict(list): every user data with their user_name, user_id, habit_id, habit_name, habit_action
		'''
		with self._db._connection.cursor() as cursor:
			query = "SELECT app_users.user_name, app_users.user_id, habits.habit_id, habits.habit_name, habits.habit_action FROM habits INNER JOIN app_users ON habits.habit_user_id=app_users.user_id;"
			cursor.execute(query)
			result = cursor.fetchall()

			if result:
				return result
			else:
				return []
			

