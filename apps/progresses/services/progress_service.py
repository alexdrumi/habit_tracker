from apps.progresses.repositories.progress_repository import ProgressesRepository, ProgressAlreadyExistError, ProgressesRepositoryError, ProgressNotFoundError
from apps.goals.services.goal_service import GoalService, GoalNotFoundError
import logging
import datetime


def handle_progresses_service_exceptions(f):
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


	@handle_progresses_service_exceptions
	def create_progress(self, goal_id, current_kvi_value, distance_from_target_kvi_value,  goal_name, habit_name, current_streak=None, progress_description=None, occurence_date=None):
		validated_goal_id = self._goal_service.validate_goal_id(goal_id) #we call this now from orchestrator, but maybe later we use it also as a single call, better to validate here as well
		
		last_progress_entry = self._repository.get_last_progress_entry(goal_id)
		if not last_progress_entry and current_streak == None: #not sure if this will return None
			new_streak = 1
		elif current_streak:
			new_streak = current_streak
		else:
			last_date = last_progress_entry[3]  #or last_progress_entry["occurence_date"] if dict
			last_streak = last_progress_entry[6]  #or whichever index is current_streak
			
			#check if within date
			threshold = datetime.timedelta(hours=48)
			# print(f"occurence_date is {occurence_date}, last progrtess entry: {last_progress_entry}")
			if (occurence_date - last_date) < threshold:
				new_streak = last_streak + 1
			else:
				new_streak = 1
		progress_entity = self._repository.create_progress(goal_id=validated_goal_id, current_kvi_value=current_kvi_value, distance_from_target_kvi_value=distance_from_target_kvi_value, current_streak=new_streak, goal_name=goal_name, habit_name=habit_name, progress_description=progress_description, occurence_date=occurence_date)
		return progress_entity


	@handle_progresses_service_exceptions
	def get_progress_id(self, goal_id):
		progress_id = self._repository.get_progress_id(goal_id)
		return progress_id


	@handle_progresses_service_exceptions
	def get_progress(self, goal_id):
		progress_id = self._repository.get_progress_id(goal_id)
		progress_entity = self._repository.get_progress(progress_id)
		return progress_entity

	@handle_progresses_service_exceptions	
	def get_last_progress_entry(self, goal_id):
		last_progress_entry = self._repository.get_last_progress_entry(goal_id)
		return last_progress_entry

	@handle_progresses_service_exceptions
	def delete_progress(self, goal_id, progress_id=None):
		if progress_id is None:
			progress_id = self.get_progress_id(goal_id=goal_id)
		deleted_rows = self._repository.delete_progress(progress_id)
		return deleted_rows
