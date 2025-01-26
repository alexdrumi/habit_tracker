from apps.kvi_types.repositories.kvi_type_repository import KviTypeRepository, KviTypesNotFoundError
from apps.users.repositories.user_repository import UserRepository, UserNotFoundError

import logging


class KviTypeService:
	def __init__(self,  repository: KviTypeRepository):
		self._repository = repository
		# self._user_repository = user_repository

	def create_a_kvi_type(self, kvi_type_name, kvi_description, kvi_multiplier, user_name):
		try:
			user_id = self._repository._user_repository.get_user_id(user_name=user_name)
			kvi_type_entity = self._repository.create_a_kvi_type(kvi_type_name, kvi_description, kvi_multiplier, user_id)
			return kvi_type_entity
		except ValueError as verror:
			logging.error(f"KviTypeService Error: {verror}")
			raise
		except UserNotFoundError as uerror:
			logging.error(f"KviTypeService Error: {verror}")
			raise	
		except Exception as error:
			logging.error(f"Unexpected error in create_a_kvi_type: {error}")
			raise
	
	def get_kvi_type_id(self, kvi_type_name, kvi_type_user_id):
		try:
			kvi_type_id = self._repository.get_kvi_type_id(kvi_type_name, kvi_type_user_id)
			return kvi_type_id
		except KviTypesNotFoundError as kerror:
			logging.error(f"Kvi type not found for user with id'{kvi_type_user_id}' and habit '{kvi_type_name}': {herror}")
			raise
		except Exception as error:
			logging.error(f"Unexpected error in get_kvi_type_id: {error}")
			raise
