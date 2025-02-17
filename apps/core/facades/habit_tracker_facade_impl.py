from apps.core.facades.habit_tracker_facade import HabitTrackerFacade
from apps.core.orchestrators.habit_orchestrator import HabitOrchestrator

from apps.users.services.user_service import UserService
from apps.habits.services.habit_service import HabitService
from apps.goals.services.goal_service import GoalService
from apps.analytics.services.analytics_service import AnalyticsService


class HabitTrackerFacadeImpl(HabitTrackerFacade):
	"""Concrete implementation of the HabitTrackerFacade abstract class"""

	def __init__(self, user_service: UserService, habit_service: HabitService):
		self._user_service = user_service
		self._habit_service = habit_service
		self._habit_orchestrator = HabitOrchestrator(self) #dependencty injection of facade

	def create_user(self, user_name: str, user_age: int, user_gender: str, user_role: str) ->dict:
		return self._user_service.create_a_user(user_name, user_age, user_gender, user_role)
	
	def delete_user(self, user_id: int) -> int:
		return self._user_service.delete_user(user_id)
	
	def query_all_user_data(self) -> dict:
		return self._user_service.query_all_user_data()
		
	def query_user_and_related_habits(self) -> dict:
		return self._user_service.quary_user_and_related_habits()

	def create_a_habit(self, habit_name, habit_action, habit_periodicity_type, habit_user_id, habit_streak=None, habit_periodicity_value=None):
		return self._habit_orchestrator.create_a_habit_with_validation(habit_name, habit_action, habit_periodicity_type, habit_user_id)

	def get_all_habits(self):
		return self._habit_service.get_all_habits()

	def delete_a_habit_by_id(self, habit_id):
		return self._habit_service.delete_a_habit_by_id(habit_id)