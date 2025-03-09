from apps.core.facades.habit_tracker_facade_impl import HabitTrackerFacadeImpl
from apps.core.orchestrators.habit_orchestrator import HabitOrchestrator


class HabitController:
	def __init__(self, habit_tracker_facade: HabitTrackerFacadeImpl, habit_tracker_orchestrator: HabitOrchestrator):
		self._facade = habit_tracker_facade
		self._orchestrator = habit_tracker_orchestrator

	def create_user(self, user_name, user_age, user_gender, user_role):
		#we could do input validation here as well
		return self._facade.create_user(user_name, user_age, user_gender, user_role)

	def delete_user(self, user_id):
		#we could do input validation here as well
		return self._facade.delete_user(int(user_id)) #we could check for row count but it will throw an error anyway

	def query_all_users(self):
		return self._facade.query_all_user_data()
	
	def query_user_and_related_habits(self):
		return self._facade.query_user_and_related_habits()
	
	def create_a_habit_with_validation(self, habit_name, habit_action, periodicity_type, user_id):
		return self._facade.create_a_habit_with_validation(habit_name, habit_action, periodicity_type, user_id)
	
	def create_a_goal(self, goal_name, habit_id, target_kvi_value, current_kvi_value, goal_description):
		return self._facade.create_a_goal(goal_name, habit_id, target_kvi_value, current_kvi_value, goal_description)
	
	def get_all_habits(self):
		return self._facade.get_all_habits()
	
	def delete_a_habit_by_id(self, habit_id):
		return self._facade.delete_a_habit_by_id(int(habit_id)) 

	def query_goals_and_related_habits(self):
		return self._facade.query_goals_and_related_habits()

	def delete_a_goal(self, goal_id):
		return 	self._facade.delete_a_goal(int(goal_id))
	
	def fetch_ready_to_tick_goals_of_habits(self):
		return self._facade.fetch_ready_to_tick_goals_of_habits()
	
	def complete_a_habit(self, habit_id, goal_id):
		return self._facade.complete_a_habit(habit_id=int(habit_id), goal_id=int(goal_id))

	def get_pending_goals(self):
		return self._facade.get_pending_goals()

	def calculate_longest_streak(self):
		return self._facade.calculate_longest_streak()

	def get_same_periodicity_type_habits(self):
		return self._facade.get_same_periodicity_type_habits()

	def get_currently_tracked_habits(self):
		return self._facade.get_currently_tracked_habits()

	def longest_streak_for_habit(self, habit_id):
		return self._facade.longest_streak_for_habit(habit_id)