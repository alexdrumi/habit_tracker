from apps.core.facades.habit_tracker_facade import HabitTrackerFacadeInterface
from apps.core.orchestrators.habit_orchestrator import HabitOrchestrator

from apps.users.services.user_service import UserService
from apps.habits.services.habit_service import HabitService
from apps.goals.services.goal_service import GoalService
from apps.progresses.services.progress_service import ProgressesService
from apps.analytics.services.analytics_service import AnalyticsService
from apps.reminders.services.reminder_service import ReminderService

#WE WILL DEFINITELY HAVE TO HAVE SOME ERROR CHECKS HERE
#AND ALSO IN THE CLI LAYER
#FOR NOW THIS IS REALLY INCONSISTENT AS I'VE PLANNED LOGGING IN SERVICE.
#THERE IS A CHECK NEEDED IN CLI SO THAT THE LOOP KEEPS RUNNING SO MAYBE HERE WE JUST PASS THE EXCP TO THE LAYER ABOVE

class HabitTrackerFacadeImpl(HabitTrackerFacadeInterface):
	"""Concrete implementation of the HabitTrackerFacade abstract class"""

	def __init__(self, user_service: UserService, habit_service: HabitService, goal_service: GoalService, progress_service: ProgressesService, reminder_service: ReminderService, analytics_service: AnalyticsService):
		self._user_service = user_service
		self._habit_service = habit_service
		self._goal_service = goal_service
		self._progress_service = progress_service
		self._reminder_service = reminder_service
		self._analytics_service = analytics_service
		self._habit_orchestrator = HabitOrchestrator(self) #dependencty injection of facade

	"""USER RELATED METHODS"""
	def create_user(self, user_name: str, user_age: int, user_gender: str, user_role: str) ->dict:
		return self._user_service.create_a_user(user_name, user_age, user_gender, user_role)
	
	def delete_user(self, user_id: int) -> int:
		return self._user_service.delete_user(user_id)
	
	def query_all_user_data(self) -> dict:
		return self._user_service.query_all_user_data()
	
	def validate_user_by_id(self, user_id: int) ->int:
		return self._user_service.validate_user_by_id(int(user_id))


	"""HABIT RELATED METHODS"""
	def query_user_and_related_habits(self) -> dict:
		return self._user_service.quary_user_and_related_habits()

	def create_a_habit_with_validation(self, habit_name, habit_action, habit_periodicity_type, habit_user_id, habit_streak=None, habit_periodicity_value=None):
		return self._habit_orchestrator.create_a_habit_with_validation(habit_name, habit_action, habit_periodicity_type, int(habit_user_id))

	def create_a_habit(self, habit_name, habit_action, habit_periodicity_type, habit_user_id, habit_streak=None, habit_periodicity_value=None):
		return self._habit_service.create_a_habit(habit_name, habit_action, habit_periodicity_type, int(habit_user_id))

	def get_all_habits(self):
		return self._habit_service.get_all_habits()

	def delete_a_habit_by_id(self, habit_id, goal_id):
		return self._habit_service.delete_a_habit_by_id(habit_id, goal_id)
	
	def validate_a_habit(self, habit_id):
		return self._habit_service.validate_a_habit(habit_id)

	def complete_a_habit(self, habit_id, goal_id):
		return self._habit_orchestrator.complete_a_habit(habit_id=habit_id, goal_id=goal_id)

	def get_habit_strategy(self, habit_id):
		return self._habit_service.get_periodicity_type(habit_id)

	def update_habit_streak(self, habit_id, updated_streak_value):
		return self._habit_service.update_habit_streak(habit_id, updated_streak_value)

	def delete_a_habit(self, habit_id):
		return self._habit_orchestrator.delete_a_habit(habit_id)
	

	"""GOAL RELATED METHODS"""
	def create_a_goal(self, goal_name, habit_id, target_kvi_value, current_kvi_value, goal_description):
		print(f"INSIDE CREATE A GOAL; goalname {goal_name}, habit_id {habit_id}, target_kvi_value {target_kvi_value}, currentkvi {current_kvi_value}")
		return self._goal_service.create_a_goal( goal_name, int(habit_id), target_kvi_value, current_kvi_value, goal_description)
	
	def delete_a_goal(self, goal_id):
		return self._goal_service.delete_a_goal(goal_id)

	def get_current_kvi(self, goal_id):
		return self._goal_service.get_current_kvi(goal_id=goal_id)

	def query_goals_and_related_habits(self):
		return self._goal_service.query_goals_and_related_habits()

	def update_goal_current_kvi_value(self, goal_id, current_kvi_value):
		return self._goal_service.update_a_goal(goal_id=goal_id, current_kvi_value=current_kvi_value)
	
	def query_goals_of_a_habit(self, habit_id):
		return self._goal_service.query_goals_of_a_habit(habit_id=habit_id)
		# goal_name, goal_id, habit_id_id, habit_name, habit_periodicity_value
	
	def query_goal_of_a_habit(self, habit_id):
		return self._goal_service.query_goal_of_a_habit(habit_id=habit_id)


	#maybe have an orchestrator call which filters the goals after querying goals of a habit
	def fetch_ready_to_tick_goals_of_habits(self):
		return self._habit_orchestrator.fetch_ready_to_tick_goals_of_habits()
	
	def validate_a_goal(self, goal_id):
		return self._goal_service.validate_goal_id(goal_id=goal_id)
	
	def get_goal_entity_by_id(self, goal_id, habit_id):
		return self._goal_service.get_goal_entity_by_id(goal_id=goal_id, habit_id=habit_id)

	def query_all_goals(self):
		return self._goal_service.query_all_goals()

	def get_last_progress_entry_associated_with_goal_id(self, goal_id):
		return self._goal_service.get_last_progress_entry_associated_with_goal_id(goal_id)

	def get_goal_of_habit(self, habit_id):
		return self._goal_service.get_goal_of_habit(habit_id)

	#def complete a habit for the orchestrator
	"""PROGRESS RELATED METHODS"""
	def create_a_progress(self, goal_id, current_kvi_value, distance_from_kvi_value, current_streak, progress_description=None):
		return self._progress_service.create_progress(goal_id, current_kvi_value, distance_from_kvi_value, progress_description=progress_description, current_streak=current_streak)
	
	def get_last_progress_entry(self, goal_id):
		return self._progress_service.get_last_progress_entry(goal_id=goal_id)
	
	"""REMINDER RELATED METHODS"""
	def get_pending_goals(self):
		return self._reminder_service.get_pending_goals()
	

	"""ANALYTICS RELATED METHODS"""
	def calculate_longest_streak(self):
		return self._analytics_service.calculate_longest_streak()
	
	def get_same_periodicity_type_habits(self):
		return self._analytics_service.get_same_periodicity_type_habits()

	def get_currently_tracked_habits(self):
		return self._analytics_service.get_currently_tracked_habits()
	
	def longest_streak_for_habit(self, habit_id):
		return self._analytics_service.longest_streak_for_habit(habit_id)
