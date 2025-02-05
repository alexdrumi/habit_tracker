from apps.users.repositories.user_repository import UserRepository, UserRepositoryError, UserNotFoundError, RoleCreationError, AlreadyExistError
from apps.users.repositories.user_repository import UserNotFoundError
from apps.users.repositories.user_repository import RoleCreationError
import logging


def handle_log_service_exceptions(f):
	'''A decorator to log exceptions of in the service layer.'''
	def exception_wrapper(self, *args, **kwargs):
		try: #all functions, create, delete etc wil be wrapped in this try block, not sure how to pass already exist error username or id
			return f(self, *args, **kwargs)
		except AlreadyExistError as aerror:
			logging.error(f"Service error in user_service from function {f.__name__}: {aerror}")
			raise
		except UserRepositoryError as urerror:
			logging.error(f"Service error in user_service from function {f.__name__}: {urerror}")
			raise
		except Exception as error:
			logging.error(f"Service error in user_service from function {f.__name__}: {error}")
			raise
	return exception_wrapper		
		


class UserService:
	def __init__(self, repository: UserRepository): #inject user repo here
		self._repository = repository

	@handle_log_service_exceptions
	def create_a_user(self, user_name, user_age, user_gender, user_role):
		if not user_name or not isinstance(user_name, str):
			raise ValueError("Invalid user name.")
		
		if not isinstance(user_age, int) and not(user_age > 0 and user_age < 120):
			raise ValueError("Invalid user age.")

		user_entity = self._repository.create_a_user(user_name, user_age, user_gender, user_role)
		return user_entity

	@handle_log_service_exceptions
	def delete_a_user(self, user_id):
		deleted_count = self._repository.delete_a_user(user_id)
		return deleted_count


	def update_a_user(self, user_name, user_age=None, user_gender=None, user_role=None):
		try:
			update_count = self._repository.update_a_user(user_name, user_age, user_gender, user_role)
			return update_count
		except UserNotFoundError as error:
			logging.error(f"UserService UserNotFoundError update_a_user: {error}")
			raise
		except Exception as error:
			logging.error(f"UserService Exception update_a_user: {error}")
			raise

	def get_user_id(self, user_name):
		try:
			user_id = self._repository.get_user_id(user_name)
			return user_id
		except UserNotFoundError as error:
			logging.error(f"UserService UserNotFoundError get_user_id: {error}")
			raise
		except Exception as error:
			logging.error(f"UserService Exception get_user_id: {error}")
			raise
	
	def validate_user(self, user_name):
		try:
			validated_user_id = self._repository.validate_user(user_name)
			return validated_user_id
		except UserNotFoundError as error:
			logging.error(f"UserService UserNotFoundError validate_user: {error}")
			raise
		except Exception as error:
			logging.error(f"UserService Exception validate_user: {error}")
			raise