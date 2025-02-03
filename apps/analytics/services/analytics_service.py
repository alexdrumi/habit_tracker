from apps.analytics.repositories.analytics_repository import AnalyticsRepository
from apps.habits.services.habit_service import HabitService
from mysql.connector.errors import IntegrityError
import logging

class AnalyticsService:
	def __init__(self, repository: AnalyticsRepository, habit_service: HabitService):
		self._repository = repository
		self._habit_service = habit_service

	def create_analytics(self, times_completed, streak_length, habit_id, last_completed_at=None):
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