from apps.core.facades.habit_tracker_facade import HabitTrackerFacadeInterface
from apps.core.orchestrators.habit_orchestrator import HabitOrchestrator
from apps.users.services.user_service import UserService
from apps.habits.services.habit_service import HabitService
from apps.goals.services.goal_service import GoalService
from apps.progresses.services.progress_service import ProgressesService
from apps.analytics.services.analytics_service import AnalyticsService
from apps.reminders.services.reminder_service import ReminderService


class HabitTrackerFacadeImpl(HabitTrackerFacadeInterface):
	"""Concrete implementation of the HabitTrackerFacade abstract class"""
	def __init__(self, user_service: UserService, habit_service: HabitService, goal_service: GoalService, progress_service: ProgressesService, reminder_service: ReminderService, analytics_service: AnalyticsService):
		self._user_service = user_service
		self._habit_service = habit_service
		self._goal_service = goal_service
		self._progress_service = progress_service
		self._reminder_service = reminder_service
		self._analytics_service = analytics_service
		self._habit_orchestrator = HabitOrchestrator(self) #dependencty injection of facade interface (abstract class)



	"""USER RELATED METHODS"""
	def create_user(self, user_name: str, user_age: int, user_gender: str, user_role: str) ->dict:
		"""
		Creates a new user.

		Args:
			user_name (str): The user's name.
			user_age (int): The user's age.
			user_gender (str): The user's gender.
			user_role (str): The user's role.

		Returns:
			dict: Information about the newly created user.
		"""
		return self._user_service.create_a_user(user_name, user_age, user_gender, user_role)



	def delete_user(self, user_id: int) -> int:
		"""
		Deletes a user by ID.

		Args:
			user_id (int): The ID of the user to delete.

		Returns:
			int: Number of rows affected.
		"""
		return self._user_service.delete_user(user_id)



	def query_all_user_data(self) -> dict:
		"""
		Retrieves all user data.

		Returns:
			dict: A dictionary containing user information.
		"""
		return self._user_service.query_all_user_data()



	def validate_user_by_id(self, user_id: int) ->int:
		"""
		Validates that a user with the given ID exists.

		Args:
			user_id (int): The ID of the user to validate.

		Returns:
			int: The validated user ID if it exists.

		Raises:
			Exception: If no user with the given ID is found.
		"""
		return self._user_service.validate_user_by_id(int(user_id))



	"""HABIT RELATED METHODS"""
	def query_user_and_related_habits(self) -> dict:
		"""
		Fetches users along with any habits associated to them.

		Returns:
			dict: A structured mapping of users to their habits.
		"""
		return self._user_service.query_user_and_related_habits()



	def create_a_habit_with_validation(self, habit_name, habit_action, habit_periodicity_type, habit_user_id, habit_streak=None, habit_periodicity_value=None):
		"""
		Creates a habit after validating the user ID.

		Args:
			habit_name (str): Name of the habit.
			habit_action (str): Action or behavior the habit represents.
			habit_periodicity_type (str): Habit's periodicity type (e.g., 'daily', 'weekly').
			habit_user_id (int): The user ID to whom this habit belongs.
			habit_streak (int, optional): Initial streak value. Defaults to None.
			habit_periodicity_value (int, optional): A numeric frequency value. Defaults to None.

		Returns:
			dict: Newly created habit details.
		"""
		return self._habit_orchestrator.create_a_habit_with_validation(habit_name, habit_action, habit_periodicity_type, int(habit_user_id))



	def create_a_habit(self, habit_name, habit_action, habit_periodicity_type, habit_user_id, habit_streak=None, habit_periodicity_value=None):
		"""
		Creates a habit without validation checks.

		Args:
			habit_name (str): Name of the habit.
			habit_action (str): Action or behavior the habit represents.
			habit_periodicity_type (str): Habit's periodicity type (e.g., 'daily', 'weekly').
			habit_user_id (int): The user ID to whom this habit belongs.
			habit_streak (int, optional): Initial streak value. Defaults to None.
			habit_periodicity_value (int, optional): A numeric frequency value. Defaults to None.

		Returns:
			dict: Newly created habit details.
		"""
		return self._habit_service.create_a_habit(habit_name, habit_action, habit_periodicity_type, int(habit_user_id))



	def get_all_habits(self):
		"""
		Retrieves all habits in the system.

		Returns:
			list: A list of all habit records.
		"""
		return self._habit_service.get_all_habits()



	def delete_a_habit_by_id(self, habit_id, goal_id): #we ll see if we actually need this
		"""
		Deletes a habit by ID, potentially requiring goal reference.

		Args:
			habit_id (int): The ID of the habit.
			goal_id (int): The related goal's ID, if applicable.

		Returns:
			Any: Result of the deletion process.
		"""
		return self._habit_service.delete_a_habit_by_id(habit_id, goal_id)



	def validate_a_habit(self, habit_id):
		"""
		Validates the existence of a habit.

		Args:
			habit_id (int): The ID of the habit to check.

		Returns:
			int: The validated habit ID if it exists.

		Raises:
			Exception: If no matching habit is found.
		"""
		return self._habit_service.validate_a_habit(habit_id)



	def complete_a_habit(self, habit_id, goal_id):
		"""
		Marks a habit as complete, incrementing streaks and progress as needed.

		Args:
			habit_id (int): The ID of the habit to complete.
			goal_id (int): The ID of the goal linked to this habit.

		Returns:
			Any: Result of the completion process.
		"""
		return self._habit_orchestrator.complete_a_habit(habit_id=habit_id, goal_id=goal_id)



	def get_habit_strategy(self, habit_id):
		"""
		Retrieves the periodicity strategy (type) of a habit.

		Args:
			habit_id (int): The ID of the habit.

		Returns:
			tuple: A tuple containing the periodicity type (e.g., ('daily',)).
		"""
		return self._habit_service.get_periodicity_type(habit_id)



	def update_habit_streak(self, habit_id, updated_streak_value):
		"""
		Updates the streak count of a habit.

		Args:
			habit_id (int): The ID of the habit to update.
			updated_streak_value (int): The new streak value.

		Returns:
			Any: Result of the update operation.
		"""
		return self._habit_service.update_habit_streak(habit_id, updated_streak_value)



	def delete_a_habit(self, habit_id):
		"""
		Deletes a habit, preserving any related progress entries.

		Args:
			habit_id (int): The habit's ID.

		Returns:
			Any: Outcome of the delete operation.
		"""
		return self._habit_orchestrator.delete_a_habit(habit_id)



	def delete_habit_physical_preserving_progress(self, habit_id, goal_id):
		"""
		Physically removes the habit record but keeps progress data intact.

		Args:
			habit_id (int): The ID of the habit.
			goal_id (int): The goal ID associated with the habit.

		Returns:
			Any: Result of the physical deletion.
		"""
		return self._habit_service.delete_habit_physical_preserving_progress(habit_id, goal_id)



	def get_current_streak(self, habit_id):
		"""
		Fetches the current streak of a given habit.

		Args:
			habit_id (int): The habit's ID.

		Returns:
			int or None: The current streak value.
		"""
		return self._habit_service.get_current_streak(habit_id=habit_id)



	"""GOAL RELATED METHODS"""
	def create_a_goal(self, goal_name, habit_id, target_kvi_value, current_kvi_value, goal_description):
		"""
		Creates a new goal for a specified habit.

		Args:
			goal_name (str): The name of the goal.
			habit_id (int): The habit's ID associated with this goal.
			target_kvi_value (float): Target metric for completion (e.g., 7 ticks).
			current_kvi_value (float): Current progress toward the target.
			goal_description (str): Short description of the goal.

		Returns:
			dict: Data about the newly created goal.
		"""
		return self._goal_service.create_a_goal( goal_name, int(habit_id), target_kvi_value, current_kvi_value, goal_description)



	def delete_a_goal(self, goal_id):
		"""
		Removes an existing goal by ID.

		Args:
			goal_id (int): The ID of the goal to delete.

		Returns:
			int: The number of rows affected.
		"""
		return self._goal_service.delete_a_goal(goal_id)



	def get_current_kvi(self, goal_id):
		"""
		Retrieves the current KVI (Key value indicator) for a goal.

		Args:
			goal_id (int): The goal's ID.

		Returns:
			float: The current KVI value.
		"""
		return self._goal_service.get_current_kvi(goal_id=goal_id)



	def query_goals_and_related_habits(self):
		"""
		Fetches goals along with their associated habit data.

		Returns:
			dict: A structured mapping of goals and their related habits.
		"""
		return self._goal_service.query_goals_and_related_habits()



	def update_goal_current_kvi_value(self, goal_id, current_kvi_value):
		"""
		Updates the current KVI value of a goal.

		Args:
			goal_id (int): The ID of the goal to update.
			current_kvi_value (float): The new KVI value.

		Returns:
			Any: Outcome of the update.
		"""
		return self._goal_service.update_a_goal(goal_id=goal_id, current_kvi_value=current_kvi_value)



	def query_goals_of_a_habit(self, habit_id):
		"""
		Retrieves all goals belonging to a particular habit.

		Args:
			habit_id (int): The habit's ID.

		Returns:
			list: A list of goal entries for the specified habit.
		"""
		return self._goal_service.query_goals_of_a_habit(habit_id=habit_id)



	def query_goal_of_a_habit(self, habit_id):
		"""
		Retrieves a single goal for a habit, currently one is expected.

		Args:
			habit_id (int): The habit's ID.

		Returns:
			Any: The associated goal's data.
		"""
		return self._goal_service.query_goal_of_a_habit(habit_id=habit_id)



	def fetch_ready_to_tick_goals_of_habits(self):
		"""
		Identifies which goals are eligible for a 'tick' (completion increment) based on time or schedule.

		Returns:
			list: A list of goals ready to be incremented.
		"""
		return self._habit_orchestrator.fetch_ready_to_tick_goals_of_habits()



	def validate_a_goal(self, goal_id):
		"""
		Ensures that a goal with the given ID exists.

		Args:
			goal_id (int): The goal's ID.

		Returns:
			int: The validated goal ID if found.

		Raises:
			Exception: If no such goal is found.
		"""
		return self._goal_service.validate_goal_id(goal_id=goal_id)



	def get_goal_entity_by_id(self, goal_id, habit_id):
		"""
		Retrieves goal entity data by both goal and habit IDs.

		Args:
			goal_id (int): The goal ID.
			habit_id (int): The habit ID.

		Returns:
			dict: The goal entity data.
		"""
		return self._goal_service.get_goal_entity_by_id(goal_id=goal_id, habit_id=habit_id)



	def query_all_goals(self):
		"""
		Retrieves all goals.

		Returns:
			list: A list of all goal records in the system.
		"""
		return self._goal_service.query_all_goals()
	


	def get_last_progress_entry_associated_with_goal_id(self, goal_id):
		"""
		Gets the most recent progress entry for a specific goal.

		Args:
			goal_id (int): The ID of the goal.

		Returns:
			dict or None: The latest progress entry if it exists.
		"""
		return self._goal_service.get_last_progress_entry_associated_with_goal_id(goal_id)



	def get_goal_of_habit(self, habit_id):
		"""
		Retrieves the goal(s) for a habit, if any.

		Args:
			habit_id (int): The habit's ID.

		Returns:
			dict or None: The goal data associated with the habit.
		"""
		return self._goal_service.get_goal_of_habit(habit_id)



	"""PROGRESS RELATED METHODS"""
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
		return self._progress_service.create_progress(
			goal_id=goal_id, 
			current_kvi_value=current_kvi_value,
			distance_from_target_kvi_value=distance_from_target_kvi_value, 
			goal_name=goal_name,
			habit_name=habit_name,
			current_streak=current_streak,
			progress_description=progress_description,
			occurence_date=occurence_date)



	def get_last_progress_entry(self, goal_id):
		"""
		Retrieves the last recorded progress for a given goal.

		Args:
			goal_id (int): The goal ID.

		Returns:
			dict or None: The most recent progress data, if found.
		"""
		return self._progress_service.get_last_progress_entry(goal_id=goal_id)



	"""REMINDER RELATED METHODS"""
	def get_pending_goals(self):
		"""
		Retrieves a list of goals that are pending completion or reminders.

		Returns:
			list: A list of goal entries pending progress.
		"""
		return self._reminder_service.get_pending_goals()



	"""ANALYTICS RELATED METHODS"""
	def calculate_longest_streak(self):
		"""
		Calculates the longest streak across all habits in the system.

		Returns:
			list of tuples: The habit_id, habit_name, habit_streak of the longest streak.
		"""
		return self._analytics_service.calculate_longest_streak()



	def get_same_periodicity_type_habits(self):
		"""
		Retrieves habits that share the same periodicity type.

		Returns:
			list of tuples: A list of habit records grouped by the same periodicity.
		"""
		return self._analytics_service.get_same_periodicity_type_habits()



	def get_currently_tracked_habits(self):
		"""
		Fetches habits that are actively tracked.

		Returns:
			list of tuples: A list of actively tracked habits.
		"""
		return self._analytics_service.get_currently_tracked_habits()



	def longest_streak_for_habit(self, habit_id):
		"""
		Calculates the longest streak for a specific habit.

		Args:
			habit_id (int): The habit ID to evaluate.

		Returns:
			list of tuples: The longest streak value for the specified habit from progresses table.
		"""
		return self._analytics_service.longest_streak_for_habit(habit_id)


	def average_streaks(self):
		"""
		Calculates the average streak for all habits. Habits with no streaks are also included.

		Returns:
			float: The average amount of streaks across all habits.
		"""
		return self._analytics_service.average_streaks()
