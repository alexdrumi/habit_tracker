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


	def _validate_user_input(self, user_name: str, user_password: str, user_age=None, user_gender=None, user_role=None, is_update=False):
		if is_update == False: #if its create
			if user_age is None or user_gender is None or user_role is None:
				raise ValueError("Fields needed for creating a user: user_age, user_gender, user_role.")

		if not isinstance(user_name, str) or not user_name.strip():
			raise ValueError("Invalid user name.")

		if not isinstance(user_password, str) or not user_password.strip():
			raise ValueError("Invalid user password.")

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
	def create_a_user(self, user_name: str, user_password: str, user_age: int, user_gender: str, user_role: str) ->dict:
		self._validate_user_input(user_name, int(user_age), user_gender, user_role)
		
		user_entity = self._repository.create_a_user(user_name, user_password, user_age, user_gender, user_role)
		return user_entity


	@handle_log_service_exceptions
	def update_a_user(self, user_name:str, user_age=None, user_gender=None, user_role=None) -> int:
		self._validate_user_input(user_name, user_age, user_gender, user_role, True)
		
		updated_count = self._repository.update_a_user(user_name, user_age, user_gender, user_role)
		return updated_count


	@handle_log_service_exceptions
	def delete_user(self, user_id: int) -> int:
		if not isinstance(user_id, int) or user_id <=0: #max users? do we need to check both with linters and isintance?
			raise ValueError("Invalid user id.")

		deleted_count = self._repository.delete_a_user(user_id)
		return deleted_count


	@handle_log_service_exceptions
	def get_user_id(self, user_name:str) -> int:
		if not (isinstance(user_name, str)) or not user_name.strip():
			raise ValueError("Invalid user name.")

		user_id = self._repository.get_user_id(user_name)
		return user_id

	@handle_log_service_exceptions
	def validate_user(self, user_name:str) ->int:
		if not (isinstance(user_name, str)) or not user_name.strip():
			raise ValueError("Invalid user name.")

		validated_user_id = self._repository.validate_user(user_name)
		return validated_user_id
