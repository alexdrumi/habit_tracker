from apps.progresses.repositories.progress_repository import ProgressesRepository, ProgressesNotFoundError
from apps.goals.services.goal_service import GoalService, GoalNotFoundError
import logging

class ProgressesService:
	def __init__(self, repository: ProgressesRepository, goal_service: GoalService):
		self._repository = repository
		self._goal_service = goal_service


	def create_progress(self, goal_id, progress_description=None):
		try:
			#validate goal id etc here
			validated_goal_id = self._goal_service.validate_goal_id(goal_id)
			#create the progress
			progress_entity = self._repository.create_progress(validated_goal_id, progress_description)
			return progress_entity

		except GoalNotFoundError as gerror:
			logging.error(f"Goal not found error originates in create progress service.: {gerror}")
			raise
		except Exception as error:
			logging.error(f"Unexpected exception originates in create progress service: {error}")
			raise


	def get_progress_id(self, goal_id):
		try:
			progress_id = self._repository.get_progress_id(goal_id)
			return progress_id

		except ProgressesNotFoundError as perror:
			logging.error(f"Progress with goal ID '{goal_id}' not found: {perror}")
			raise
		except Exception as error:
			logging.error(f"Unexpected error in get progress id: {error}")
			raise


	def get_progress(self, goal_id):
		try:
			progress_id = self._repository.get_progress_id(goal_id)
			progress_entity = self._repository.get_progress(progress_id)
			return progress_entity

		except ProgressesNotFoundError as perror:
			logging.error(f"Progress with goal ID '{goal_id}' not found in get progress: {perror}")
			raise
		except Exception as error:
			logging.exception("Unexpected error in get progress") #apparently, this is better for tracing, https://docs.python.org/3/library/logging.html
			raise


	def delete_progress(self, goal_id, progress_id=None):
		try:
			if progress_id is None:
				progress_id = self.get_progress_id(goal_id=goal_id)
			deleted_rows = self._repository.delete_progress(progress_id)
			return deleted_rows

		except ProgressesNotFoundError as perror:
			logging.error(f"Progress with goal ID '{goal_id}' not found in delete progress: {perror}")
			raise
		except Exception as error:
			logging.exception("Unexpected error in delete_progress") #apparently, this is better for tracing, https://docs.python.org/3/library/logging.html
			raise