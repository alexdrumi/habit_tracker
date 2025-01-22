from apps.habits.repositories.habit_repository import HabitRepository, HabitNotFoundError
from mysql.connector.errors import IntegrityError
from apps.users.repositories.user_repository import UserNotFoundError
import logging

class HabitService:
	def __init__(self, repository: HabitRepository):
		self._repository = repository


	def create_a_habit(self, habit_name, habit_action, habit_streak, habit_periodicity_type, habit_periodicity_value, habit_user):
		try:
			habit_entity = self._repository.create_a_habit(habit_name, habit_action, habit_streak, habit_periodicity_type, habit_periodicity_value, habit_user)
			print(habit_entity)
			
			return habit_entity
		except IntegrityError as ierror:
			#log integrity error
			logging.error(f"Duplicate habit creation error: {ierror}")
			raise
		except UserNotFoundError as uerror:
			#log user not found error
			logging.error(f"User not found: {uerror}")
			raise
		except Exception as error:
			#everything else
			logging.error(f"Unexpected error in create_a_habit: {error}")
			raise


	def get_habit_id(self, user_name, habit_name):
		try:
			habit_id = self._repository.get_habit_id(user_name, habit_name)
			return habit_id
		except HabitNotFoundError as herror:
			#log user not found error
			logging.error(f"Habit not found for user '{user_name}' and habit '{habit_name}': {herror}")
			raise
		except Exception as error:
			#everything else
			logging.error(f"Unexpected error in create_a_habit: {error}")
			raise


	def delete_a_habit(self, user_name, habit_name):
		try:
			habit_id = self.get_habit_id(user_name, habit_name)
			deleted_count = self._repository.delete_a_habit(habit_id)
			return deleted_count
		except HabitNotFoundError as herror:
			logging.error(f"Habit not found for user '{user_name}' and habit '{habit_name}': {herror}")
			raise
		except Exception as error:
			#everything else
			logging.error(f"Unexpected error in create_a_habit: {error}")
			raise
