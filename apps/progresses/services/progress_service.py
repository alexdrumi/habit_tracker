from apps.progresses.repositories.progress_repository import ProgressesRepository, ProgressAlreadyExistError, ProgressesRepositoryError, ProgressNotFoundError
from apps.goals.services.goal_service import GoalService, GoalNotFoundError
import logging



def handle_log_service_exceptions(f):
	"""Decorator to clean up and handle errors in progress services methods."""
	def exception_wrapper(*args, **kwargs):
		try:
			return f(*args, **kwargs)
		except (ProgressAlreadyExistError, ProgressNotFoundError, GoalNotFoundError) as specific_error:
			logging.error(f"Service error in {f.__name__}: {specific_error}")
			raise specific_error
		except ProgressesRepositoryError as herror:
			logging.error(f"Service error in {f.__name__}: {herror}")
			raise herror
		except Exception as error:
			logging.error(f"Unexpected error in {f.__name__}: {error}")
			raise error
	return exception_wrapper




class ProgressesService:
	def __init__(self, repository: ProgressesRepository, goal_service: GoalService):
		self._repository = repository
		self._goal_service = goal_service


	@handle_log_service_exceptions
	def create_progress(self, goal_id, current_kvi_value, distance_from_target_kvi_value, progress_description=None):
		validated_goal_id = self._goal_service.validate_goal_id(goal_id) #we call this now from orchestrator, but maybe later we use it also as a single call, better to validate here as well
		progress_entity = self._repository.create_progress(validated_goal_id, current_kvi_value, distance_from_target_kvi_value, progress_description)
		return progress_entity


	def get_progress_id(self, goal_id):
		try:
			progress_id = self._repository.get_progress_id(goal_id)
			return progress_id

		except ProgressNotFoundError as perror:
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

		except ProgressNotFoundError as perror:
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

		except ProgressNotFoundError as perror:
			logging.error(f"Progress with goal ID '{goal_id}' not found in delete progress: {perror}")
			raise
		except Exception as error:
			logging.exception("Unexpected error in delete_progress") #apparently, this is better for tracing, https://docs.python.org/3/library/logging.html
			raise