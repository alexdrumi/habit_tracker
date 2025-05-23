from abc import ABC, abstractmethod

class HabitTrackerFacadeInterface(ABC):
	"""USER RELATED METHODS"""
	@abstractmethod
	def validate_user_by_id(self, user_id: int) ->int:
		pass



	@abstractmethod
	def create_user(self, user_name: str, user_password: str, user_age: int, user_gender: str, user_role: str) -> dict:
		pass



	@abstractmethod
	def delete_user(self, user_id: int) -> int:
		pass



	@abstractmethod
	def query_all_user_data(self) -> dict:
		pass



	"""HABIT RELATED METHODS"""
	@abstractmethod
	def query_user_and_related_habits(self) -> dict:
		pass



	@abstractmethod
	def create_a_habit(self, habit_name, habit_action, habit_periodicity_type, habit_user_id, habit_streak=None, habit_periodicity_value=None):
		pass



	@abstractmethod
	def get_all_habits(self):
		pass



	@abstractmethod
	def delete_a_habit_by_id(self, habit_id):
		pass



	@abstractmethod
	def validate_a_habit(self, habit_id):
		pass



	@abstractmethod
	def get_habit_strategy(self, habit_id):
		pass



	@abstractmethod
	def complete_a_habit(self, habit_id, goal_id):
		pass



	@abstractmethod
	def update_habit_streak(habit_id, updated_streak_value):
		pass



	@abstractmethod
	def delete_habit_physical_preserving_progress(self, habit_id, goal_id):
		pass



	@abstractmethod
	def get_current_streak(self, habit_id):
		pass




	"""GOAL RELATED METHODS"""
	@abstractmethod
	def create_a_goal(self, goal_name, habit_id, target_kvi_value, current_kvi_value, goal_description):
		pass



	@abstractmethod
	def delete_a_goal(self, goal_id):
		pass



	@abstractmethod
	def query_goals_and_related_habits(self):
		pass



	@abstractmethod
	def update_goal_current_kvi_value(self, goal_id, current_kvi_value):
		pass



	@abstractmethod
	def query_goals_of_a_habit(self, habit_id):
		pass


	@abstractmethod
	def query_goal_of_a_habit(self, habit_id):
		pass



	@abstractmethod
	def get_goal_entity_by_id(self, goal_id, habit_id):
		pass



	@abstractmethod
	def fetch_ready_to_tick_goals_of_habits(self):
		pass



	@abstractmethod
	def query_all_goals(self):
		pass



	@abstractmethod
	def get_last_progress_entry_associated_with_goal_id(self, goal_id):
		pass



	"""PROGRESS RELATED METHODS"""
	@abstractmethod
	def create_progress(self, goal_id, current_kvi_value, distance_from_target_kvi_value,  goal_name, habit_name, current_streak=None, progress_description=None, occurence_date=None):
		pass



	@abstractmethod
	def get_last_progress_entry(self, goal_id):
		pass



	"""REMINDER RELATED METHODS"""
	@abstractmethod
	def get_pending_goals(self):
		pass



	"""ANALYTICS RELATED METHODS"""
	@abstractmethod
	def calculate_longest_streak(self):
		pass



	@abstractmethod
	def get_same_periodicity_type_habits(self):
		pass



	@abstractmethod
	def get_currently_tracked_habits(self):
		pass



	@abstractmethod
	def longest_streak_for_habit(self, habit_id):
		pass

	@abstractmethod
	def average_streaks(self):
		pass