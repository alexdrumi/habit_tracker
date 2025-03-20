from apps.users.repositories.user_repository import UserRepository, UserRepositoryError, UserNotFoundError, RoleCreationError, AlreadyExistError
import logging

def handle_log_service_exceptions(f):
	'''A decorator to log exceptions of in the service layer.'''
	def exception_wrapper(self, *args, **kwargs):
		try: #all functions, create, delete etc wil be wrapped in this try block, not sure how to pass already exist error username or id
			return f(self, *args, **kwargs)
		except ValueError as verror:
			logging.error(f"Service error in user_service from function {f.__name__}: {verror}")
			raise verror
		except UserRepositoryError as rerror:
			logging.error(f"Service error in user_service from function {f.__name__}: {rerror}")
			raise rerror
		except Exception as error:
			logging.error(f"Service error in user_service from function {f.__name__}: {error}")
			raise error
	return exception_wrapper


class UserService:
	def __init__(self, repository: UserRepository): #inject user repo here
		self._repository = repository


	def _validate_user_input(self, user_name: str, user_password=None, user_age=None, user_gender=None, user_role=None, is_update=False):
		"""
		Validates user data before creating or updating a user record.

		Args:
			user_name (str): The username to validate. Must be a non-empty string.
			user_password (str, optional): The user's password (if needed).
			user_age (int, optional): The user's age. Must be between 1 and 120 if provided.
			user_gender (str, optional): The user's gender. Must be non-empty if provided.
			user_role (str, optional): The role. Must be one of ['admin', 'user', 'bot'] if provided.
			is_update (bool, optional): Whether this is an update operation. 
										If False (create operation), user_age, user_gender, and user_role must not be None.

		Raises:
			ValueError: If any field fails validation checks.
		"""
		if is_update == False: #if its create
			print(f"{user_age}, {user_gender}, {user_role}")
			if user_age is None or user_gender is None or user_role is None:
				raise ValueError("Fields needed for creating a user: user_age, user_gender, user_role.")

		if not isinstance(user_name, str) or not user_name.strip():
			raise ValueError("Invalid user name.")

		# if not isinstance(user_password, str) or not user_password.strip():
		# 	raise ValueError("Invalid user password.")

		if user_age is not None:
			if not isinstance(user_age, int) or not (0 < user_age < 120):
				raise ValueError("Invalid user age.")

		if user_gender is not None:
			if not isinstance(user_gender, str) or not user_gender.strip():
				raise ValueError("Invalid user gender.")

		if user_role is not None:
			if not isinstance(user_role, str) or not user_role.strip() or user_role not in ['user', 'admin', 'bot']:
				raise ValueError(f"Invalid user role: {user_role}, expected one of the followings: 'admin', 'user', 'bot'.")



	@handle_log_service_exceptions
	def create_a_user(self, user_name: str, user_age: int, user_gender: str, user_role: str) ->dict:
		"""
		Creates a new user after validating the input data.

		Args:
			user_name (str): The user's name.
			user_age (int): The user's age (1-119).
			user_gender (str): The user's gender.
			user_role (str): The user's role, must be one of ['admin', 'user', 'bot'].

		Returns:
			dict: A dictionary containing the created user's info including 'user_id'.

		Raises:
			ValueError: If input data fails validation (e.g., negative age).
			AlreadyExistError: If a user with the same name already exists.
		"""
		self._validate_user_input(user_name=user_name, user_age=int(user_age), user_gender=user_gender, user_role=user_role)
		
		user_entity = self._repository.create_a_user(user_name, int(user_age), user_gender, user_role)
		return user_entity



	@handle_log_service_exceptions
	def update_a_user(self, user_name:str, user_age=None, user_gender=None, user_role=None) -> int:
		"""
		Updates existing user information given a username as the key.

		Args:
			user_name (str): The name of the user to be updated (used in WHERE).
			user_age (int, optional): The new age (1-119).
			user_gender (str, optional): The new gender.
			user_role (str, optional): The new role ('admin', 'user', or 'bot').

		Returns:
			int: The number of rows updated (ideally 1 if successful).

		Raises:
			ValueError: If input validation fails.
			UserNotFoundError: If the user doesn't exist.
		"""
		self._validate_user_input(user_name, user_age, user_gender, user_role, True)
		
		updated_count = self._repository.update_a_user(user_name, user_age, user_gender, user_role)
		return updated_count



	@handle_log_service_exceptions
	def delete_user(self, user_id: int) -> int:
		"""
		Deletes a user by ID along with any associated habits.

		Args:
			user_id (int): The ID of the user to delete.

		Returns:
			int: Number of rows affected by deletion of the user record.

		Raises:
			ValueError: If user_id is invalid.
			UserNotFoundError: If the user doesn't exist.
		"""
		if not isinstance(user_id, int) or user_id <=0: #max users? do we need to check both with linters and isintance?
			raise ValueError("Invalid user id.")

		deleted_count = self._repository.delete_a_user(user_id)
		return deleted_count



	@handle_log_service_exceptions
	def get_user_id(self, user_name:str) -> int:
		"""
		Retrieves a user's ID by their username.

		Args:
			user_name (str): The user's name.

		Returns:
			int: The user's ID.

		Raises:
			ValueError: If the user_name is invalid.
			UserNotFoundError: If no user with that name exists.
		"""
		if not (isinstance(user_name, str)) or not user_name.strip():
			raise ValueError("Invalid user name.")

		user_id = self._repository.get_user_id(user_name)
		return user_id



	@handle_log_service_exceptions
	def validate_user_by_name(self, user_name:str) ->int:
		"""
		Validates if a user with the given name exists, returning their user_id.

		Args:
			user_name (str): The name of the user.

		Returns:
			int: The user's ID if found.

		Raises:
			ValueError: If the user_name is invalid.
			UserNotFoundError: If the user doesn't exist.
		"""
		if not (isinstance(user_name, str)) or not user_name.strip():
			raise ValueError("Invalid user name.")

		validated_user_id = self._repository.validate_user_by_name(user_name)
		return validated_user_id



	@handle_log_service_exceptions
	def validate_user_by_id(self, user_id:int) ->int:
		"""
		Validates if a user with the given ID exists, returning the same user_id.

		Args:
			user_id (int): The ID of the user.

		Returns:
			int: The user_id if found.

		Raises:
			ValueError: If the user_id is invalid (non-integer or <= 0).
			UserNotFoundError: If no user with that ID exists.
		"""
		if not (isinstance(user_id, int)):
			raise ValueError("Invalid user id.")

		validated_user_id = self._repository.validate_user_by_id(user_id)
		return validated_user_id



	@handle_log_service_exceptions
	def query_all_user_data(self) -> dict: #maybe list of dicts?
		"""
		Retrieves all users from the database (user_id, user_name).

		Returns:
			list: A list of user records (tuples). Empty list if no records exist.
		"""
		all_users = self._repository.query_all_user_data()
		return all_users



	@handle_log_service_exceptions
	def quary_user_and_related_habits(self) -> dict:
		"""
		Retrieves all users and their associated habits using an INNER JOIN.

		Returns:
			list: A list of tuples, each containing user data and habit data.
					e.g., (user_name, user_id, habit_id, habit_name, habit_action).
		"""
		inner_joined_user_and_related_habits = self._repository.query_user_and_related_habits()
		return inner_joined_user_and_related_habits