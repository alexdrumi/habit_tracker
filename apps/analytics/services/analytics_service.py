from apps.analytics.repositories.analytics_repository import AnalyticsRepository, AnalyticsNotFoundError
from apps.habits.services.habit_service import HabitService
from apps.progresses.services.progress_service import ProgressesService
from mysql.connector.errors import IntegrityError
import logging

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
		

	def create_analytics(self, habit_id, times_completed, streak_length, last_completed_at=None):
		try:
			#check if habit id exist
			validated_habit_id = self._habit_service._repository.validate_a_habit(habit_id)
			analytics_entity = self._repository.create_analytics(times_completed, streak_length, habit_id, last_completed_at=last_completed_at)
			return analytics_entity
		except IntegrityError as ierror:
			logging.error(f"Duplicate analytics type error: {ierror}")
			raise
		except Exception as error:
			logging.error(f"AnalyticsService Exception in create analytics: {error}")
			raise


	def update_analytics(self, habit_id, times_completed=None, streak_length=None, last_completed_at=None):
		try:
			#get analytics id, if there is none this will raise an error
			analytics_id = self._repository.get_analytics_id(habit_id)

			#validate based on input
			self.validate_analytics("update", habit_id=habit_id, analytics_id=analytics_id, times_completed=times_completed, streak_length=streak_length, last_completed_at=last_completed_at)
			
			#update analytics
			updated_rows = self._repository.update_analytics(analytics_id, times_completed, streak_length, last_completed_at)
			return updated_rows
		except AnalyticsNotFoundError as aerror:
			logging.error(f"Analytics for habit with id {habit_id} is not found. error: {aerror}")
			raise
		except Exception as error:
			logging.error(f"Unexpected error in update analytics: {error}")
			raise


	def get_analytics_id(self, habit_id):
		try:
			#should we validate whether habit id exists first?
			analytics_id = self._repository.get_analytics_id(habit_id)
			return analytics_id
		except AnalyticsNotFoundError as aerror:
			logging.error(f"Analytics for habit with id {habit_id} is not found. error: {aerror}")
			raise
		except Exception as error:
			logging.error(f"Unexpected error in update analytics: {error}")
			raise


	def delete_analytics(self, habit_id=None, analytics_id=None):
		try:
			self.validate_analytics('delete', habit_id=habit_id, analytics_id=analytics_id)

			if habit_id and not analytics_id:
				analytics_id = self._repository.get_analytics_id(habit_id)
			
			deleted_rows = self._repository.delete_analytics(analytics_id)
			return deleted_rows
		except AnalyticsNotFoundError as aerror:
			logging.error(f"Analytics for habit with id {habit_id} is not found. error: {aerror}")
			raise
		except Exception as error:
			logging.error(f"Unexpected error in update analytics: {error}")
			raise


	def calculate_longest_streak(self):
		try:
			result = self._repository.calculate_longest_streak()
			# print(f"WE ARE BEING CALLED HERE")
			return result

		except AnalyticsNotFoundError as aerror:
			logging.error(f"Analytics is not found. error: {aerror}")
			raise
		except Exception as error:
			logging.error(f"Unexpected error in update analytics: {error}")
			raise


	def get_same_periodicity_type_habits(self):
		try:
			result = self._repository.get_same_periodicity_type_habits()
			return result
		except AnalyticsNotFoundError as aerror:
			logging.error(f"Analytics is not found. error: {aerror}")
			raise
		except Exception as error:
			logging.error(f"Unexpected error in update analytics: {error}")
			raise

	def get_currently_tracked_habits(self):
		try:
			result = self._repository.get_currently_tracked_habits()
			return result
		except AnalyticsNotFoundError as aerror:
			logging.error(f"Analytics is not found. error: {aerror}")
			raise
		except Exception as error:
			logging.error(f"Unexpected error in update analytics: {error}")
			raise
	
	def longest_streak_for_habit(self, habit_id):
		try:
			result = self._repository.longest_streak_for_habit(habit_id)
			return result
		except AnalyticsNotFoundError as aerror:
			logging.error(f"Analytics is not found. error: {aerror}")
			raise
		except Exception as error:
			logging.error(f"Unexpected error in update analytics: {error}")
			raise
		# - and return the longest run streak for a given habit.
		# try: 
		# 	result 