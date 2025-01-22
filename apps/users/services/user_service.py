from apps.users.repositories.user_repository import UserRepository
from apps.users.repositories.user_repository import UserNotFoundError
from apps.users.repositories.user_repository import RoleCreationError
import logging

class UserService:
	def __init__(self):
		self._repository = UserRepository()

	def create_a_user(self, user_name, user_age, user_gender, user_role):
		try:
			user_entity = self._repository.create_a_user(user_name, user_age, user_gender, user_role)
			return user_entity
		except RoleCreationError as error:
			logging.error(f"UserService RoleCreationError create_a_user: {error}")
			raise
		except Exception as error:
			logging.error(f"UserService Exception create_a_user: {error}")
			raise

	def delete_a_user(self, user_id):
		try:
			deleted_count = self._repository.delete_a_user(user_id)
			return deleted_count
		except UserNotFoundError as error:
			logging.error(f"UserService UserNotFoundError delete_a_user: {error}")
			raise
		except Exception as error:
			logging.error(f"UserService Exception delete_a_user: {error}")
			raise

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