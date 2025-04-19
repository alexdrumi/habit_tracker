from apps.core.facades.habit_tracker_facade_impl import HabitTrackerFacadeImpl
from apps.core.orchestrators.habit_orchestrator import HabitOrchestrator
from apps.users.utils.mappers import map_to_user_read_schema
from apps.users.schemas import UserRead, UserCreate
from typing import List


class HabitController:
	def __init__(self, habit_tracker_facade: HabitTrackerFacadeImpl, habit_tracker_orchestrator: HabitOrchestrator):
		self._facade = habit_tracker_facade
		self._orchestrator = habit_tracker_orchestrator



	def create_user(self, user_name, user_age, user_gender, user_role):
		"""
		Creates a new user.

		Args:
			user_name (str): The user's name.
			user_age (int): The user's age.
			user_gender (str): The user's gender.
			user_role (str): The user's role (e.g., "admin" or "participant").

		Returns:
			dict: Information about the newly created user.
		"""
		return self._facade.create_user(user_name, user_age, user_gender, user_role)



	def delete_user(self, user_id):
		"""
		Deletes an existing user by ID.

		Args:
			user_id (int): The ID of the user to delete.

		Returns:
			int: The number of rows affected by the delete operation.
		"""
		return self._facade.delete_user(int(user_id))



	def query_all_users(self) -> List[UserRead]:
		"""
		Retrieves all users stored in the system.

		Returns:
			dict: A list of UserRead pydantic schemas for API response.
		"""
		raw_users = self._facade.query_all_user_data()
		return [map_to_user_read_schema(user) for user in raw_users]



	def query_user_and_related_habits(self):
		"""
		Fetches users along with their associated habits.

		Returns:
			dict: A structured representation of users and their related habits.
		"""
		return self._facade.query_user_and_related_habits()



	def create_a_habit_with_validation(self, habit_name, habit_action, periodicity_type, user_id):
		"""
		Creates a new habit, ensuring the user is valid.

		Args:
			habit_name (str): The name of the habit (e.g., "Morning run").
			habit_action (str): The action or behavior the habit represents.
			periodicity_type (str): The periodicity (e.g., "daily", "weekly").
			user_id (int): The ID of the user who owns this habit.

		Returns:
			dict: Details about the newly created habit.
		"""

		''' this comes from the underlying repository
		return {
						'habit_id': cursor.lastrowid,
						'habit_action': habit_action,
						'habit_streak': habit_streak,
						'habit_periodicity_type': habit_periodicity_type,
						'habit_user_id': habit_user_id,
					}
		'''
		return self._facade.create_a_habit_with_validation(habit_name, habit_action, periodicity_type, user_id)



	def create_a_goal(self, goal_name, habit_id, target_kvi_value, current_kvi_value, goal_description):
		"""
		Creates a goal for a specific habit.

		Args:
			goal_name (str): The name or title of the goal.
			habit_id (int): The habit's ID this goal is tied to.
			target_kvi_value (float): The target key value indicator (e.g., total completions needed).
			current_kvi_value (float): The current progress toward the target.
			goal_description (str): A short description of the goal.

		Returns:
			dict: Details of the newly created goal.
		"""
		return self._facade.create_a_goal(goal_name, habit_id, target_kvi_value, current_kvi_value, goal_description)



	def get_all_habits(self):
		"""
		Retrieves all habits in the system.

		Returns:
			list: A list of habit entries.
		"""
		return self._facade.get_all_habits()



	def delete_a_habit(self, habit_id):
		"""
		Deletes a habit by ID, preserving any associated progress entries.

		Args:
			habit_id (int): The ID of the habit to delete.

		Returns:
			int: The number of rows affected by the delete operation.
		"""
		return self._facade.delete_a_habit(int(habit_id)) 



	def query_goals_and_related_habits(self):
		"""
		Retrieves goals along with their associated habit data.

		Returns:
			dict: A structured mapping of goals and their related habit information.
		"""
		return self._facade.query_goals_and_related_habits()



	def delete_a_goal(self, goal_id):
		"""
		Deletes an existing goal by ID.

		Args:
			goal_id (int): The ID of the goal to delete.

		Returns:
			int: The number of rows affected by the delete operation.
		"""
		return 	self._facade.delete_a_goal(int(goal_id))



	def fetch_ready_to_tick_goals_of_habits(self):
		"""
		Lists goals that are ready to be 'ticked' or updated according to their schedule.

		Returns:
			list: A list of goals that are eligible for completion updates.
		"""
		return self._facade.fetch_ready_to_tick_goals_of_habits()



	def complete_a_habit(self, habit_id, goal_id):
		"""
		Marks a habit as completed for the day or week, incrementing streaks and progress.

		Args:
			habit_id (int): The ID of the habit to complete.
			goal_id (int): The ID of the goal linked to this habit.

		Returns:
			None
		"""
		return self._facade.complete_a_habit(habit_id=int(habit_id), goal_id=int(goal_id))



	def get_pending_goals(self):
		"""
		Retrieves a list of goals that are pending completion or reminders.

		Returns:
			list: A list of goal entries pending progress.
		"""
		return self._facade.get_pending_goals()



	def calculate_longest_streak(self):
		"""
		Calculates the longest streak across all habits in the system.

		Returns:
			list of tuples: The habit_id, habit_name, habit_streak of the longest streak.
		"""
		return self._facade.calculate_longest_streak()



	def get_same_periodicity_type_habits(self):
		"""
		Retrieves habits that share the same periodicity type.

		Returns:
			list of tuples: A list of habit records grouped by the same periodicity.
		"""
		return self._facade.get_same_periodicity_type_habits()



	def get_currently_tracked_habits(self):
		"""
		Fetches habits that are actively tracked.

		Returns:
			list of tuples: A list of actively tracked habits.
		"""
		return self._facade.get_currently_tracked_habits()



	def longest_streak_for_habit(self, habit_id):
		"""
		Calculates the longest streak for a specific habit.

		Args:
			habit_id (int): The habit ID to evaluate.

		Returns:
			list of tuples: The longest streak value for the specified habit from progresses table.
		"""
		return self._facade.longest_streak_for_habit(habit_id)



	def update_habit_streak(self, habit_id, updated_streak_value):
		"""
		Updates the streak count of a habit.

		Args:
			habit_id (int): The ID of the habit to update.
			updated_streak_value (int): The new streak value.

		Returns:
			int: Amount of updated entries.
		"""
		return self._facade.update_habit_streak(habit_id, updated_streak_value)



	def get_current_streak(self, habit_id):
		"""
		Gets the current streak value of a habit.

		Args:
			habit_id (int): The ID of the habit to query.

		Returns:
			int or None: The current streak value of the specified habit.
		"""
		return self._facade.get_current_streak(habit_id=habit_id)



	def get_last_progress_entry(self, goal_id):
		"""
		Retrieves the most recent progress entry for a given goal.

		Args:
			goal_id (int): The ID of the goal to look up.

		Returns:
			dict or None: The last recorded progress data, if any.
		"""
		return self._facade.get_last_progress_entry(goal_id=goal_id)



	def query_goal_of_a_habit(self, habit_id):
		"""
		Retrieves a single goal for a habit, currently one is expected.

		Args:
			habit_id (int): The habit's ID.

		Returns:
			Any: The associated goal's data.
		"""
		return self._facade.query_goal_of_a_habit(habit_id=habit_id)



	def create_progress(self, goal_id, current_kvi_value, distance_from_target_kvi_value,  goal_name, habit_name, current_streak=None, progress_description=None, occurence_date=None):
		"""
		Creates a new progress record for a specific goal.

		Args:
			goal_id (int): ID of the goal.
			current_kvi_value (float): Current KVI progress being recorded.
			distance_from_target_kvi_value (float): Remaining distance to the target KVI.
			goal_name (str): Name of the goal.
			habit_name (str): Name of the associated habit.
			current_streak (int, optional): Current streak value. Defaults to None.
			progress_description (str, optional): Additional details about the progress. Defaults to None.
			occurence_date (datetime, optional): Timestamp of when progress occurred. Defaults to None.

		Returns:
			dict: Data of the newly created progress entry.
		"""
		return self._facade.create_progress(goal_id=goal_id, 
			current_kvi_value=current_kvi_value,
			distance_from_target_kvi_value=distance_from_target_kvi_value, 
			goal_name=goal_name,
			habit_name=habit_name,
			current_streak=current_streak,
			progress_description=progress_description,
			occurence_date=occurence_date)