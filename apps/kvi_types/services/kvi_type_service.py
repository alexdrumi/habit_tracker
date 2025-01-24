from apps.kvi_types.repositories.kvi_type_repository import KviTypeRepository
import logging


class KviTypeService:
	def __init__(self, repository: KviTypeRepository):
		self._repository = repository
	
	def create_a_kvi_type(self, kvi_type_name, kvi_description, kvi_multiplier):
		try:
			kvi_type_entity = self._repository.create_a_kvi_type(kvi_type_name, kvi_description, kvi_multiplier)
			return kvi_type_entity
		except ValueError as verror:
			logging.error(f"KviTypeService Error: {verror}")
			raise
		except Exception as error:
			logging.error(f"Unexpected error in create_a_kvi_type: {error}")
			raise