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
		#maybe some more extensive validation?
		validated_goal_id = self._repository.validate_a_goal(goal_id)
		return validated_goal_id
	
	@handle_log_service_exceptions
	def get_current_kvi(self, goal_id):
		#maybe some more extensive validation?
		current_goal_kvi = self._repository.get_current_kvi(goal_id=goal_id)
		return current_goal_kvi


	def get_goal_id(self, goal_name, habit_id):
		try:
			goal_id = self._repository.get_goal_id(goal_name=goal_name, habit_id=habit_id)
		except GoalNotFoundError as gerror:
			logging.error(f"Goal with ID '{goal_id}' not found: {gerror}")
			raise
		except Exception as error:
			logging.error(f"Unexpected error in update a goal: {error}")
			raise

	@handle_log_service_exceptions
	def get_goal_entity_by_id(self, goal_id, habit_id):
		goal_entity = self._repository.get_goal_entity_by_id(goal_id=goal_id, habit_id=habit_id)
		return goal_entity


	@handle_log_service_exceptions
	def create_a_goal(self, goal_name, habit_id, target_kvi_value, current_kvi_value, goal_description):
		
		#validate habit
		validated_habit_id = self._habit_service._repository.validate_a_habit(habit_id)

		#validate goal input
		self._validate_goal("create", goal_id=None, goal_name=goal_name, habit_id_id=validated_habit_id, target_kvi_value=target_kvi_value, current_kvi_value=current_kvi_value)

		#create new goal
		goal_entity = self._repository.create_a_goal(goal_name, habit_id, target_kvi_value, current_kvi_value, goal_description)
		return goal_entity



	@handle_log_service_exceptions
	def delete_a_goal(self, goal_id):
		#validate id
		validated_goal_id = self._repository.validate_a_goal(goal_id)

		#delete the goal
		deleted_count = self._repository.delete_a_goal(validated_goal_id)
		return deleted_count


	@handle_log_service_exceptions
	def query_goals_and_related_habits(self):
		inner_joined_goals_and_related_habits = self._repository.query_goals_and_related_habits()
		return inner_joined_goals_and_related_habits

	
	@handle_log_service_exceptions
	def delete_a_goal(self, goal_id):
		validated_goal_id = self._repository.validate_a_goal(goal_id)
		deleted_count = self._repository.delete_a_goal(validated_goal_id)
		return deleted_count
	

	#NOT SURE WHETHER WE NEED THIS AT THE MOMENT, we will use only to update the current kvi value, later this might be more extensive
	@handle_log_service_exceptions
	def update_a_goal(self, goal_id, goal_name=None, target_kvi_value=None, current_kvi_value=None):
			#validate
			self._validate_goal("update", goal_id=goal_id, goal_name=goal_name, target_kvi_value=target_kvi_value, current_kvi_value=current_kvi_value)
			
			#update
			updated_rows = self._repository.update_goal_field(goal_id, goal_name, target_kvi_value, current_kvi_value)
			return updated_rows


	@handle_log_service_exceptions
	def query_goals_of_a_habit(self, habit_id):
		goals = self._repository.query_goals_of_a_habit(habit_id)
		return goals