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
		validated_habit_id = self._habit_service.validate_a_habit(habit_id)
		analytics_entity = self._repository.create_analytics(times_completed, streak_length, validated_habit_id, last_completed_at=last_completed_at)
		
		return analytics_entity
		
	@handle_analytics_service_exceptions
	def update_analytics(self, habit_id, times_completed=None, streak_length=None, last_completed_at=None):
		#get analytics id, if there is none this will raise an error
		analytics_id = self._repository.get_analytics_id(habit_id)

		#validate based on input
		self.validate_analytics("update", habit_id=habit_id, analytics_id=analytics_id, times_completed=times_completed, streak_length=streak_length, last_completed_at=last_completed_at)
		
		#update analytics
		updated_rows = self._repository.update_analytics(analytics_id, times_completed, streak_length, last_completed_at)
		return updated_rows
		

	@handle_analytics_service_exceptions
	def get_analytics_id(self, habit_id):
		#should we validate whether habit id exists first?
		analytics_id = self._repository.get_analytics_id(habit_id)
		return analytics_id

	@handle_analytics_service_exceptions
	def delete_analytics(self, habit_id=None, analytics_id=None):
		self.validate_analytics('delete', habit_id=habit_id, analytics_id=analytics_id)

		if habit_id and not analytics_id:
			analytics_id = self._repository.get_analytics_id(habit_id)
		
		deleted_rows = self._repository.delete_analytics(analytics_id)
		return deleted_rows

	@handle_analytics_service_exceptions
	def calculate_longest_streak(self):
		result = self._repository.calculate_longest_streak()
		return result

	@handle_analytics_service_exceptions
	def get_same_periodicity_type_habits(self):
		result = self._repository.get_same_periodicity_type_habits()
		return result

	@handle_analytics_service_exceptions
	def get_currently_tracked_habits(self):
		result = self._repository.get_currently_tracked_habits()
		return result

	@handle_analytics_service_exceptions
	def longest_streak_for_habit(self, habit_id):
		result = self._repository.longest_streak_for_habit(habit_id)
		return result
