from apps.analytics.repositories.analytics_repository import AnalyticsRepository, AnalyticsNotFoundError
from apps.habits.services.habit_service import HabitService
from apps.progresses.services.progress_service import ProgressesService
from mysql.connector.errors import IntegrityError
import logging

def handle_analytics_service_exceptions(f):

	def wrapper(*args, **kwargs):
		try:
			return f(*args, **kwargs) 
		except AnalyticsNotFoundError as aerror:
			logging.error(f"Service error in {f.__name__}: {aerror}")
			raise aerror 
		except IntegrityError as ierror:
			logging.error(f"Service error in {f.__name__}: {ierror}")
			raise ierror 
		except Exception as error:
			logging.error(f"Unexpected error in {f.__name__}: {error}")
			raise error 

	return wrapper  


class AnalyticsService:
	def __init__(self, repository: AnalyticsRepository, habit_service: HabitService, progress_service: ProgressesService):
		self._repository = repository
		self._habit_service = habit_service
		self._progress_service = progress_service


	def validate_analytics(self, action, habit_id=None, analytics_id=None, times_completed=None, streak_length=None, last_completed_at=None):
		"""
		Validates input parameters for analytics-related actions such as creating, updating, or deleting analytics records.

		Args:
			action (str): 
				The action to perform. Must be one of ["create", "update", "delete"].
			habit_id (int, optional): 
				The unique identifier of the habit associated with the analytics record.
			analytics_id (int, optional): 
				The unique identifier of the analytics record.
			times_completed (int, optional): 
				The total number of times the habit has been completed.
			streak_length (int, optional): 
				The current streak length of consecutive habit completions.
			last_completed_at (datetime, optional): 
				Timestamp of the last habit completion. Optional, defaults to None.

		Raises:
			ValueError: 
				- If the action provided is not one of the allowed values ("create", "update", "delete").
				- If required fields (analytics_id, habit_id, times_completed, streak_length) are missing or invalid based on the action.
				- If times_completed or streak_length values are outside the allowed range (0 to 365).
		"""
		if action not in ["create", "update", "delete"]:
			raise ValueError(f"Invalid action '{action}'. Allowed: create, update, delete.")

		if action in ["update", "delete"] and not (analytics_id or habit_id):
			raise ValueError("analytics_id is required for updating or deleting a analytics_id.")

		if action == "update" and not (times_completed or streak_length):
			raise ValueError("to update analytics, you need at least one of the following: times_completed, streak_length.")

		if action == "create" and not (times_completed and streak_length and habit_id):
			raise ValueError("times_completed and streak_length and habit_id are required for creating an analytics.")

		if streak_length and (streak_length < 0 or streak_length > 365):
			raise ValueError("Streak_length must be between 0 and 365.")
		
		if times_completed and (times_completed < 0 or times_completed > 365):
			raise ValueError("times_completed must be between 0 and 365.")



	@handle_analytics_service_exceptions
	def create_analytics(self, habit_id, times_completed, streak_length, last_completed_at=None):
		"""
		Creates an analytics entry for a given habit.

		Args:
			habit_id (int): The unique identifier of the habit.
			times_completed (int): The total number of completions for the habit.
			streak_length (int): The current streak length of the habit.
			last_completed_at (datetime, optional): The last time the habit was completed. Defaults to None.

		Returns:
			dict: The newly created analytics record including its 'analytics_id'.

		Logs and Raises:
			AnalyticsNotFoundError: If the habit cannot be found or is invalid.
			IntegrityError: For database integrity-related errors.
			Exception: For other unexpected errors in the analytics service.
		"""
		validated_habit_id = self._habit_service.validate_a_habit(habit_id)
		analytics_entity = self._repository.create_analytics(times_completed, streak_length, validated_habit_id, last_completed_at=last_completed_at)
		
		return analytics_entity



	@handle_analytics_service_exceptions
	def update_analytics(self, habit_id, times_completed=None, streak_length=None, last_completed_at=None):
		"""
		Updates an existing analytics record tied to a given habit.

		Args:
			habit_id (int): The unique identifier of the habit.
			times_completed (int, optional): Updated number of habit completions. Defaults to None.
			streak_length (int, optional): Updated streak length of the habit. Defaults to None.
			last_completed_at (datetime, optional): Updated datetime for the last completion. Defaults to None.

		Returns:
			int: The number of rows updated (typically 1 on success).

		Logs and Raises:
			AnalyticsNotFoundError: If there's no analytics entry for the given habit.
			IntegrityError: For database integrity-related issues.
			Exception: For any other unexpected errors in analytics service.
		"""
		
		#get analytics id, if there is none this will raise an error
		analytics_id = self._repository.get_analytics_id(habit_id)

		#validate based on input
		self.validate_analytics("update", habit_id=habit_id, analytics_id=analytics_id, times_completed=times_completed, streak_length=streak_length, last_completed_at=last_completed_at)
		
		#update analytics
		updated_rows = self._repository.update_analytics(analytics_id, times_completed, streak_length, last_completed_at)
		return updated_rows
		


	@handle_analytics_service_exceptions
	def get_analytics_id(self, habit_id):
		"""
		Retrieves the analytics ID for the specified habit.

		Args:
			habit_id (int): The unique identifier of the habit.

		Returns:
			int: The ID of the analytics record tied to the provided habit_id.

		Logs and Raises:
			AnalyticsNotFoundError: If no analytics record is found for the habit.
			IntegrityError: For database integrity-related issues.
			Exception: For any other unexpected errors in analytics service.
		"""
		#should we validate whether habit id exists first?
		analytics_id = self._repository.get_analytics_id(habit_id)
		return analytics_id



	@handle_analytics_service_exceptions
	def delete_analytics(self, habit_id=None, analytics_id=None):
		"""
		Deletes an analytics record either by direct analytics ID or by habit ID.

		Args:
			habit_id (int, optional): The habit's unique identifier. Defaults to None.
			analytics_id (int, optional): The analytics record's unique identifier. Defaults to None.

		Returns:
			int: The number of rows deleted (usually 1 on success).

		Logs and Raises:
			ValueError: If neither habit_id nor analytics_id is provided when needed.
			AnalyticsNotFoundError: If the record to be deleted is not found.
			IntegrityError: For database integrity-related issues.
		"""
		self.validate_analytics('delete', habit_id=habit_id, analytics_id=analytics_id)

		if habit_id and not analytics_id:
			analytics_id = self._repository.get_analytics_id(habit_id)
		
		deleted_rows = self._repository.delete_analytics(analytics_id)
		return deleted_rows



	@handle_analytics_service_exceptions
	def calculate_longest_streak(self):
		"""
		Returns the habit with the current longest streak from the database.

		Returns:
			tuple: (habit_id, habit_name, habit_streak) representing the habit with the maximum streak.

		Logs and Raises:
			AnalyticsNotFoundError: If no longest streak is found.
			IntegrityError: For database integrity-related issues.
			Exception: For any other unexpected errors in analytics service.
		"""
		result = self._repository.calculate_longest_streak()
		return result



	@handle_analytics_service_exceptions
	def get_same_periodicity_type_habits(self):
		"""
		Groups and retrieves habits by periodicity type.

		Returns:
			list of tuples: Each tuple contains:
							(periodicity_type, habit_count, habit_list).
							- periodicity_type (str): 'daily' or 'weekly', etc.
							- habit_count (int): Number of habits in that group.
							- habit_list (str): Concatenated details of habits.

		Raises:
			AnalyticsNotFoundError: If no habits are found in any group.
			IntegrityError: For database integrity-related issues.
			Exception: For other unexpected errors in analytics service.
		"""
		result = self._repository.get_same_periodicity_type_habits()
		return result



	@handle_analytics_service_exceptions
	def get_currently_tracked_habits(self):
		"""
		Retrieves habits that currently have a streak above zero.

		Returns:
			list of tuples: E.g., [(habit_id, habit_name, streak, periodicity_type), ...]

		Raises:
			AnalyticsNotFoundError: If there are no habits currently being tracked.
			IntegrityError: For database integrity-related issues.
			Exception: For any other unexpected errors in analytics service.
		"""
		result = self._repository.get_currently_tracked_habits()
		return result



	@handle_analytics_service_exceptions
	def longest_streak_for_habit(self, habit_id):
		"""
		Retrieves the single highest streak entry from 'progresses' for a given habit.

		Args:
			habit_id (int): The unique identifier of the habit.

		Returns:
			list of tuples: The fetched progress records ordered by largest streak first.

		Raises:
			AnalyticsNotFoundError: If no progress data is found for the habit.
			IntegrityError: For database integrity-related issues.
			Exception: For other unexpected errors in analytics service.
		"""
		result = self._repository.longest_streak_for_habit(habit_id)
		return result
