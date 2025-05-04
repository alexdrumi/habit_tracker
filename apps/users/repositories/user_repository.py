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
	'''A decorator to make exceptions in database errors cleaner.'''
	def exception_wrapper(self, *args, **kwargs):
		try: #all functions, create, delete etc wil be wrapped in this try block, not sure how to pass already exist error username or id
			return f(self, *args, **kwargs)
		except IntegrityError as ierror:
			self._db._connection.rollback()
			user_identifier = args[0] if args else "unknown"
			raise AlreadyExistError(user_identifier) from ierror #id is args[0]
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
		"""
		Checks if a user with the given name exists in the database.

		Args:
			user_name (str): The username to look up.

		Returns:
			int: The user's ID if found.

		Raises:
			UserNotFoundError: If no user with this name exists.
		"""
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
		"""
		Checks if a user with the given ID exists in the database.

		Args:
			user_id (int): The ID of the user.

		Returns:
			int: The user ID if found.

		Raises:
			UserNotFoundError: If no user with this ID exists.
		"""
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
		"""
		Creates a user role in the `app_users_role` table if it does not already exist.

		Args:
			user_role (str): The role name (e.g. 'admin', 'user', 'bot').

		Returns:
			int: The ID of the role, either existing or newly created.

		Raises:
			RoleCreationError: If the insertion fails for any reason.
		"""
		with self._db._connection.cursor() as cursor:
			query = "SELECT user_role FROM app_users_role WHERE user_role = %s;"
			cursor.execute(query, (user_role,))
			role = cursor.fetchone()
			if role:
				return role[0]
			#insert the new role.since user_role is the primary key thenreturn it directly
			query = "INSERT INTO app_users_role(user_role) VALUES (%s);"
			cursor.execute(query, (user_role,))
			self._db._connection.commit()
			return user_role 




	@handle_user_repository_errors
	def create_a_user(self, user_name, user_age, user_gender, user_role):
		"""
		Inserts a new user record into the `app_users` table.

		Args:
			user_name (str): The name of the user.
			user_age (int): The age of the user.
			user_gender (str): The gender of the user.
			user_role (str): The role string (e.g. 'admin', 'user', 'bot').

		Returns:
			dict: A dictionary containing the new user's 'user_id', 'user_name', and 'user_role'.

		Raises:
			AlreadyExistError: If a user with the same name already exists (handled by decorator).
		"""
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
	


	@handle_user_repository_errors
	def delete_a_user(self, user_id):
		"""
		Deletes a user from the database, as well as their related habits (if any).

		Args:
			user_id (int): The ID of the user to delete.

		Returns:
			int: The number of rows affected by the deletion from `app_users`.

		Raises:
			UserNotFoundError: If the user doesn't exist.
		"""
		try:
			self._db._connection.autocommit = False
			with self._db._connection.cursor() as cursor: #this closes cursor anyway, https://www.psycopg.org/docs/cursor.html
				#delete the related habit first
				query_habit = "DELETE FROM habits WHERE habit_user_id = %s";
				cursor.execute(query_habit, (user_id,))

				#then the user
				query = "DELETE FROM app_users WHERE user_id = %s"
				cursor.execute(query, (user_id,))

				if cursor.rowcount == 0:
					raise UserNotFoundError(user_id)
				self._db._connection.commit() #if all deletions passed, commit
				return cursor.rowcount #nr of rows effected in DELETE SQL, this could also be just a bool but x>0 will act anyway as bool
		finally:
			self._db._connection.autocommit = True #allow autocommit again



	@handle_user_repository_errors
	def update_a_user(self, user_name, user_age=None, user_gender=None, user_role=None):
		"""
		Updates a user's information in the `app_users` table.
		Fields that are None are not updated.

		Args:
			user_name (str): The existing username (used for the WHERE clause).
			user_age (int, optional): The new age.
			user_gender (str, optional): The new gender.
			user_role (str, optional): The new role.

		Returns:
			int: Number of rows affected by the update.

		Raises:
			UserNotFoundError: If no user is found with the given user_name.
		"""
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
		"""
		Retrieves a user's ID based on their username.

		Args:
			user_name (str): The user's name.

		Returns:
			int: The user's ID.

		Raises:
			UserNotFoundError: If no user is found with this name.
		"""
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
		"""
		Retrieves all users from the `app_users` table.

		Returns:
			list: A list of tuples, each containing user_id and user_name. 
					An empty list if no users are found.
		"""
		with self._db._connection.cursor() as cursor:
			query = "SELECT user_id, user_name FROM app_users;"
			cursor.execute(query)
			result = cursor.fetchall()

			if result:
				return result
			else:
				return []


	@handle_user_repository_errors
	def query_user_and_related_habits(self): #INNER JOIN
		"""
		Retrieves a joined list of users and their associated habits.

		Returns:
			list: A list of tuples containing
					(user_name, user_id, habit_id, habit_name, habit_action).
					An empty list if no users or habits are found.
		"""
		with self._db._connection.cursor() as cursor:
			query = "SELECT app_users.user_name, app_users.user_id, habits.habit_id, habits.habit_name, habits.habit_action FROM habits INNER JOIN app_users ON habits.habit_user_id=app_users.user_id;"
			cursor.execute(query)
			result = cursor.fetchall()

			if result:
				return result
			else:
				return []
			

