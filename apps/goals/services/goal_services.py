from apps.goals.repositories.goal_repository import GoalNotFoundError, GoalRepository
from apps.habits.repositories.habit_repository import HabitNotFoundError, HabitRepository
from apps.kvi_types.repositories.kvi_type_repository import KviTypesNotFoundError, KviTypeRepository
from mysql.connector.errors import IntegrityError
import logging

class GoalService:
	def __init__(self, repository: GoalRepository, habit_repository: HabitRepository, kvi_repository: KviTypeRepository):
		self._repository = repository
		self._habit_repository = habit_repository
		self._kvi_repository = kvi_repository



	def _validate_goal(self, action, goal_id=None, goal_name=None, habit_id_id=None, kvi_type_id_id=None, target_kvi_value=None, current_kvi_value=None):
		if action not in ["create", "update", "delete"]:
			raise ValueError(f"Invalid action '{action}'. Allowed: create, update, delete.")

		if action in ["update", "delete"] and not goal_id:
			raise ValueError("goal_id is required for updating or deleting a goal.")

		if action == "create" and not (kvi_type_id_id and habit_id_id):
			raise ValueError("kvi_type_id_id and habit_id_id is required for creating a goal.")

		if action == "create" and not goal_name:
			raise ValueError("user_goal_name is required for creating a goal type.")

		if action in ["create", "update"] and target_kvi_value is not None:
			if not (target_kvi_value >= 0.0 and target_kvi_value <= float('inf')):
				raise ValueError("target_kvi_value must be between 0.0 and float max.")

		if action in ["create", "update"] and current_kvi_value is not None:
			if not (current_kvi_value >= 0.0 and current_kvi_value <= float('inf')):
				raise ValueError("current_kvi_value must be between 0.0 and float max.")


	def create_a_goal(self, goal_name, habit_id, kvi_type_id, target_kvi_value, current_kvi_value, goal_description):
		try:
			#get validated habit and kvi ids
			validated_kvi_id = self._kvi_repository.validate_a_kvi_type(kvi_type_id)
			validated_habit_id = self._habit_repository.validate_a_habit(habit_id)

			#validate
			self._validate_goal("create", goal_id=None, goal_name=goal_name, habit_id_id=validated_habit_id, kvi_type_id_id=validated_kvi_id, target_kvi_value=target_kvi_value, current_kvi_value=current_kvi_value)

			#create new goal
			goal_entity = self._repository.create_a_goal(goal_name, habit_id, kvi_type_id, target_kvi_value, current_kvi_value, goal_description)
			return goal_entity

		except HabitNotFoundError as herror:
			logging.error(f"Habit of with id of: {habit_id} is not found.")
			raise
		except KviTypesNotFoundError as kerror:
			logging.error(f"Kvi type with id of: {kvi_type_id} is not found.")
			raise
		except IntegrityError as ierror:
			logging.error(f"Duplicate goal type error: {ierror}")
			raise



	def update_a_goal(self, goal_id, goal_name=None, target_kvi_value=None, current_kvi_value=None):
			try:
				#validate
				self._validate_goal("update", goal_id=goal_id, goal_name=goal_name, target_kvi_value=target_kvi_value, current_kvi_value=current_kvi_value)
				
				#update
				updated_rows = self._repository.update_goal_field(goal_id, goal_name, target_kvi_value, current_kvi_value)
				return updated_rows
	
			except GoalNotFoundError as gerror:
				logging.error(f"Goal with ID '{goal_id}' not found: {gerror}")
				raise
			except Exception as error:
				logging.error(f"Unexpected error in update a goal: {error}")
				raise


	def delete_a_goal(self, goal_id):
		try:
			validated_goal_id = self._repository.validate_a_goal(goal_id)
			deleted_count = self._repository.delete_a_goal(validated_goal_id)
			return deleted_count
		except GoalNotFoundError as gerror:
			logging.error(f"Goal with ID '{goal_id}' not found: {gerror}")
			raise
		except Exception as error:
			#everything else
			logging.error(f"Unexpected error in create_a_habit: {error}")
			raise