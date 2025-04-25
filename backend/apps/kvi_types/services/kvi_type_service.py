from apps.kvi_types.repositories.kvi_type_repository import KviTypeRepository, KviTypesNotFoundError
from apps.users.repositories.user_repository import UserRepository, UserNotFoundError
from apps.users.services.user_service import UserService, UserNotFoundError

from mysql.connector.errors import IntegrityError
import logging


class KviTypeService:
	def __init__(self, repository: KviTypeRepository, user_service: UserService):
		self._repository = repository
		self._user_service = user_service



	def _validate_kvi(self, action, kvi_type_id=None, kvi_type_name=None, kvi_multiplier=None, user_name=None):
			if action not in ["create", "update", "delete"]:
				raise ValueError(f"Invalid action '{action}'. Allowed: create, update, delete.")

			if action in ["update", "delete"] and not kvi_type_id:
				raise ValueError("kvi_type_id is required for updating or deleting a KVI type.")

			if action == "create" and not kvi_type_name:
				raise ValueError("kvi_type_name is required for creating a KVI type.")

			if action == "create" and not user_name:
				raise ValueError("user_name is required for creating a KVI type.")

			if action in ["create", "update"] and kvi_multiplier is not None:
				if not (0.0 <= kvi_multiplier <= 10.0):
					raise ValueError("kvi_multiplier must be between 0.0 and 10.0.")


	def create_a_kvi_type(self, kvi_type_name, kvi_description, kvi_multiplier, user_name):
		try:
			#validate
			self._validate_kvi("create", kvi_type_name, kvi_multiplier, user_name)

			#get user id
			user_id = self._user_service.get_user_id(user_name)
			
			#create kvi typer
			kvi_type_entity = self._repository.create_a_kvi_type(kvi_type_name, kvi_description, kvi_multiplier, user_id)
			return kvi_type_entity

		except IntegrityError as ierror:
			logging.error(f"Duplicate KVI type error: {ierror}")
			raise
		except UserNotFoundError as uerror:
			logging.error(f"User not found: {uerror}")
			raise
		except Exception as error:
			logging.error(f"Unexpected error in create_a_kvi_type: {error}")
			raise



	def update_a_kvi_type(self, kvi_multiplier, kvi_type_name=None, kvi_type_user_id=None, kvi_type_id=None):
			try:
				#validate
				self._validate_kvi("update", kvi_type_id=kvi_type_id, kvi_multiplier=kvi_multiplier)
				
				#update
				updated_rows = self._repository.update_kvi_type(kvi_type_id, kvi_multiplier)
				return updated_rows
	
			except KviTypesNotFoundError as kerror:
				logging.error(f"KVI type with ID '{kvi_type_id}' not found: {kerror}")
				raise
			except Exception as error:
				logging.error(f"Unexpected error in update_kvi_multiplier: {error}")
				raise



	def get_kvi_type_id(self, kvi_type_name, kvi_type_user_id):
		try:
			kvi_type_id = self._repository.get_kvi_type_id(kvi_type_name, kvi_type_user_id)
			return kvi_type_id

		except KviTypesNotFoundError as kerror:
			logging.error(f"Kvi type not found for user with id'{kvi_type_user_id}' and habit '{kvi_type_name}': {kerror}")
			raise
		except Exception as error:
			logging.error(f"Unexpected error in get_kvi_type_id: {error}")
			raise
	

	def delete_a_kvi_type(self, kvi_type_id):
		try:
			#validate
			self._validate_kvi("delete", kvi_type_id=kvi_type_id)

			#delete
			self._repository.delete_a_kvi_type(kvi_type_id)

		except KviTypesNotFoundError as kerror:
			logging.error(f"KVI type with ID '{kvi_type_id}' not found: {kerror}")
			raise
		except Exception as error:
			logging.error(f"Unexpected error in delete_a_kvi_type: {error}")
			raise