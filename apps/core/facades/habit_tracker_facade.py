from abc import ABC, abstractmethod

class HabitTrackerFacade(ABC):
	@abstractmethod
	def create_user(self, user_name: str, user_password: str, user_age: int, user_gender: str, user_role: str) ->dict:
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
		pass #this will be multistep from the orchestrator

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
	def complete_a_habit(self, habit_id, goal_id):
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
	

	