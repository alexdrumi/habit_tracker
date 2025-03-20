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
	"""
	A service class that provides higher-level business logic for handling
	progress-related operations, such as creation, retrieval, and deletion. 
	It coordinates with the repository and the goal service.
	"""
	def __init__(self, repository: ProgressesRepository, goal_service: GoalService):
		self._repository = repository
		self._goal_service = goal_service


	#this might go to the orchestrator, does too many things at the moment
	@handle_progresses_service_exceptions
	def create_progress(self, goal_id, current_kvi_value, distance_from_target_kvi_value,  goal_name, habit_name, current_streak=None, progress_description=None, occurence_date=None):
		"""
		Creates a new progress entry for a given goal, updating or resetting 
		the streak based on the last progress date.

		Args:
			goal_id (int): The unique identifier of the goal associated with the progress.
			current_kvi_value (float): Current KVI value for this new progress.
			distance_from_target_kvi_value (float): The difference between the target KVI and current KVI.
			goal_name (str): The name of the goal.
			habit_name (str): The name of the habit associated with the goal.
			current_streak (int, optional): An explicitly set current streak. Defaults to None.
			progress_description (str, optional): Additional description for the progress entry. Defaults to None.
			occurence_date (datetime, optional): The timestamp for the progress entry. Defaults to current time.

		Returns:
			dict: A dictionary containing the newly created progress entry data.

		Raises:
			ProgressAlreadyExistError: If a duplicate or invalid progress entry creation is attempted.
			ProgressNotFoundError: If the goal validation fails (no associated goal).
			GoalNotFoundError: If the specified goal_id is invalid.
			ProgressesRepositoryError: For repository-level progress errors.
			Exception: For any other unexpected errors.
		"""
		validated_goal_id = self._goal_service.validate_goal_id(goal_id) #we could call this from somewhere else, or validate befgore passing it onto the service.
		goal_entity = self._goal_service.get_goal_entity_by_goal_id(validated_goal_id)
		target_kvi = goal_entity['target_kvi']
		last_progress_entry = self._repository.get_last_progress_entry(goal_id=validated_goal_id)
		
		if not last_progress_entry and current_streak == None: #not sure if this will return None
			new_streak = 1
		elif current_streak is not None:
			new_streak = current_streak
		else:
			last_date = last_progress_entry[3]  #or last_progress_entry["occurence_date"] if dict
			last_streak = last_progress_entry[6]  #or whichever index is current_streak
			
			threshold = datetime.timedelta(hours=48) if target_kvi == 1.0 else datetime.timedelta(weeks=2)
			if (occurence_date - last_date) < threshold:
				new_streak = last_streak + 1
			else:
				new_streak = 1
		progress_entity = self._repository.create_progress(goal_id=validated_goal_id, current_kvi_value=current_kvi_value, distance_from_target_kvi_value=distance_from_target_kvi_value, current_streak=new_streak, goal_name=goal_name, habit_name=habit_name, progress_description=progress_description, occurence_date=occurence_date)
		return progress_entity



	@handle_progresses_service_exceptions
	def get_progress_id(self, goal_id):
		"""
		Retrieves the progress ID for a given goal.

		Args:
			goal_id (int): The unique identifier of the goal.

		Returns:
			int: The progress ID associated with the goal.

		Raises:
			ProgressNotFoundError: If no progress entry is found for the given goal.
			Exception: For any other unexpected errors.
		"""
		progress_id = self._repository.get_progress_id(goal_id)
		return progress_id



	@handle_progresses_service_exceptions
	def get_progress(self, goal_id):
		"""
		Retrieves the most recent progress entry as a dictionary for a given goal.

		Args:
			goal_id (int): The unique identifier of the goal.

		Returns:
			dict or None: The progress entry if found, otherwise None.

		Raises:
			ProgressNotFoundError: If no progress is found for the given goal.
		"""
		progress_id = self._repository.get_progress_id(goal_id)
		progress_entity = self._repository.get_progress(progress_id)
		return progress_entity



	@handle_progresses_service_exceptions	
	def get_last_progress_entry(self, goal_id):
		"""
		Retrieves the last chronological progress entry for a specified goal.

		Args:
			goal_id (int): The unique identifier of the goal.

		Returns:
			tuple or None: The last progress record if found, otherwise None.

		Raises:
			ProgressNotFoundError: If no progress is found for the given goal.
		"""
		last_progress_entry = self._repository.get_last_progress_entry(goal_id)
		return last_progress_entry



	@handle_progresses_service_exceptions
	def delete_progress(self, goal_id, progress_id=None):
		"""
		Deletes a specific progress entry. If progress_id is not provided, 
		it fetches the most recent entry for the goal and deletes it.

		Args:
			goal_id (int): The unique identifier of the goal.
			progress_id (int, optional): The unique identifier of the progress entry. 
				If None, the last entry for the goal is deleted.

		Returns:
			int: The number of rows deleted (1 if successful).

		Raises:
			ProgressNotFoundError: If the progress entry does not exist.
			Exception: For any other unexpected errors.
		"""
		if progress_id is None:
			progress_id = self.get_progress_id(goal_id=goal_id)
		deleted_rows = self._repository.delete_progress(progress_id)
		return deleted_rows
