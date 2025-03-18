from apps.goals.repositories.goal_repository import GoalNotFoundError, GoalRepository, GoalAlreadyExistError, GoalRepositoryError
# from apps.habits.repositories.habit_repository import HabitNotFoundError, HabitRepository
# from apps.kvi_types.repositories.kvi_type_repository import KviTypesNotFoundError, KviTypeRepository
from apps.habits.services.habit_service import HabitNotFoundError, HabitService
from apps.kvi_types.services.kvi_type_service import KviTypesNotFoundError, KviTypeService
from mysql.connector.errors import IntegrityError
import logging


def handle_log_service_exceptions(f):
	"""Decorator to clean up and handle errors in goal services methods."""
	def exception_wrapper(*args, **kwargs):
		try:
			return f(*args, **kwargs)
		except (GoalAlreadyExistError, GoalRepositoryError, GoalNotFoundError) as specific_error:
			logging.error(f"Service error in {f.__name__}: {specific_error}")
			raise specific_error
		except HabitNotFoundError as herror:
			logging.error(f"Service error in {f.__name__}: {herror}")
			raise herror
		except IntegrityError as ierror:
				logging.error(f"Service error in {f.__name__}: {ierror}")
				raise ierror
		except Exception as error:
			logging.error(f"Unexpected error in {f.__name__}: {error}")
			raise error
	return exception_wrapper



class GoalService:
	def __init__(self, repository: GoalRepository, habit_service: HabitService): #, kvi_service: KviTypeService
		self._repository = repository
		self._habit_service = habit_service
		# self._kvi_service = kvi_service


	def _validate_goal(self, action, goal_id=None, goal_name=None, habit_id_id=None, target_kvi_value=None, current_kvi_value=None):
		"""
		Ensures that goal input data meets certain constraints before action.
		"""
		if action not in ["create", "update", "delete"]:
			raise ValueError(f"Invalid action '{action}'. Allowed: create, update, delete.")

		if action in ["update", "delete"] and not goal_id:
			raise ValueError("goal_id is required for updating or deleting a goal.")

		# if action == "create" and not (kvi_type_id_id and habit_id_id):
		# 	raise ValueError("kvi_type_id_id and habit_id_id is required for creating a goal.")

		if action == "create" and not goal_name:
			raise ValueError("user_goal_name is required for creating a goal type.")

		if action in ["create", "update"] and target_kvi_value is not None:
			if not (target_kvi_value >= 0.0 and target_kvi_value <= float('inf')):
				raise ValueError("target_kvi_value must be between 0.0 and float max.")

		if action in ["create", "update"] and current_kvi_value is not None:
			if not (current_kvi_value >= 0.0 and current_kvi_value <= float('inf')):
				raise ValueError("current_kvi_value must be between 0.0 and float max.")



	@handle_log_service_exceptions
	def validate_goal_id(self, goal_id):
		"""
		Validates that a goal with the given ID exists.

		Args:
			goal_id (int): The ID of the goal to validate.

		Returns:
			int: The validated goal ID.

		Raises:
			GoalNotFoundError: If no such goal is found.
		"""
		validated_goal_id = self._repository.validate_a_goal(goal_id)
		return validated_goal_id



	@handle_log_service_exceptions
	def get_current_kvi(self, goal_id):
		"""
		Retrieves the current KVI value of a specified goal.

		Args:
			goal_id (int): The goal’s ID.

		Returns:
			float: The current KVI value.
		"""
		current_goal_kvi = self._repository.get_current_kvi(goal_id=goal_id)
		return current_goal_kvi


	@handle_log_service_exceptions
	def get_goal_id(self, goal_name, habit_id):
		"""
		Fetches the goal ID based on the goal name and habit ID.

		Args:
			goal_name (str): The goal’s name.
			habit_id (int): The associated habit’s ID.

		Raises:
			GoalNotFoundError: If the goal is not found.

		Returns:
			int: The ID of the found goal.
		"""
		goal_id = self._repository.get_goal_id(goal_name=goal_name, habit_id=habit_id)
		return goal_id



	@handle_log_service_exceptions
	def get_goal_entity_by_id(self, goal_id, habit_id):
		"""
		Retrieves comprehensive goal data (including streak and names).

		Args:
			goal_id (int): The goal’s ID.
			habit_id (int): The habit’s ID linked to the goal.

		Returns:
			dict: Goal entity with fields like 'goal_name', 'target_kvi',
			'current_kvi', and 'streak'.
		"""
		goal_entity = self._repository.get_goal_entity_by_id(goal_id=goal_id, habit_id=habit_id)
		return goal_entity



	@handle_log_service_exceptions
	def create_a_goal(self, goal_name, habit_id, target_kvi_value, current_kvi_value, goal_description):
		"""
		Creates a goal after validating input and habit existence.

		Args:
			goal_name (str): Name of the goal.
			habit_id (int): Associated habit’s ID.
			target_kvi_value (float): Target KVI needed for goal.
			current_kvi_value (float): Current KVI progress.
			goal_description (str): Brief description of the goal.

		Returns:
			dict: Newly created goal data (including goal_id and others).

		Raises:
			HabitNotFoundError: If the given habit ID is invalid.
			GoalAlreadyExistError: If a goal with the same name/habit combo exists.
		"""
		validated_habit_id = self._habit_service.validate_a_habit(habit_id)
		self._validate_goal("create", goal_id=None, goal_name=goal_name, habit_id_id=validated_habit_id, target_kvi_value=target_kvi_value, current_kvi_value=current_kvi_value)
		goal_entity = self._repository.create_a_goal(goal_name, habit_id, target_kvi_value, current_kvi_value, goal_description)
		return goal_entity



	@handle_log_service_exceptions
	def delete_a_goal(self, goal_id):
		"""
		Removes a goal record from the system.

		Args:
			goal_id (int): The ID of the goal to delete.

		Returns:
			int: The number of rows affected.

		Raises:
			GoalNotFoundError: If no goal with the specified ID exists.
		"""
		validated_goal_id = self._repository.validate_a_goal(goal_id)
		deleted_count = self._repository.delete_a_goal(validated_goal_id)
		return deleted_count



	@handle_log_service_exceptions
	def query_goals_and_related_habits(self):
		"""
		Fetches goals joined with related habit data.

		Returns:
			list: A list of tuples containing goal and habit information.
		"""
		inner_joined_goals_and_related_habits = self._repository.query_goals_and_related_habits()
		return inner_joined_goals_and_related_habits


	
	#NOT SURE WHETHER WE NEED THIS AT THE MOMENT, we will use only to update the current kvi value, later this might be more extensive
	@handle_log_service_exceptions
	def update_a_goal(self, goal_id, goal_name=None, target_kvi_value=None, current_kvi_value=None):
		"""
		Updates the specified fields of a goal.

		Args:
			goal_id (int): ID of the goal to update.
			goal_name (str, optional): New name for the goal.
			target_kvi_value (float, optional): New target KVI.
			current_kvi_value (float, optional): New current KVI.

		Returns:
			int: Number of rows affected.

		Raises:
			GoalNotFoundError: If no matching goal is found.
		"""
		self._validate_goal("update", goal_id=goal_id, goal_name=goal_name, target_kvi_value=target_kvi_value, current_kvi_value=current_kvi_value)
		updated_rows = self._repository.update_goal_field(goal_id, goal_name, target_kvi_value, current_kvi_value)
		return updated_rows



	@handle_log_service_exceptions
	def query_goals_of_a_habit(self, habit_id):
		"""
		Retrieves all goals associated with a specific habit.

		Args:
			habit_id (int): The habit ID.

		Returns:
			list: List of goal records.
		"""
		goals = self._repository.query_goals_of_a_habit(habit_id)
		return goals
	


	@handle_log_service_exceptions
	def query_goal_of_a_habit(self, habit_id):
		"""
		Fetches a single goal ID for a habit, if it exists.

		Args:
			habit_id (int): ID of the habit.

		Returns:
			list or tuple: The goal ID linked to the habit, or empty if none exist.
		"""
		goal = self._repository.query_goal_of_a_habit(habit_id=habit_id)
		return goal
	
	

	@handle_log_service_exceptions
	def query_all_goals(self):
		"""
		Retrieves all goals from the repository.

		Returns:
			list of dict: Each item representing goal data.
		"""
		all_goals = self._repository.query_all_goals()
		return all_goals



	@handle_log_service_exceptions
	def get_last_progress_entry_associated_with_goal_id(self, goal_id):
		"""
		Fetches the most recent progress entry for a specified goal.

		Args:
			goal_id (int): The goal’s ID.

		Returns:
			dict or list: Dictionary with occurence_date or an empty list if none found.
		"""
		last_progress = self._repository.get_last_progress_entry_associated_with_goal_id(goal_id=goal_id)
		return last_progress