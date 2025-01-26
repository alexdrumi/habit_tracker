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
			return habit_entity
		except IntegrityError as ierror:
			logging.error(f"Duplicate habit creation error: {ierror}")
			raise
		except UserNotFoundError as uerror:
			logging.error(f"User not found: {uerror}")
			raise
		except Exception as error:
			logging.error(f"Unexpected error in create_a_habit: {error}")
			raise

	#we could do user_id
	def update_habit_streak(self, user_name, habit_name, streak_value):
		try:
			habit_id = self.get_habit_id(user_name, habit_name)
			#we could eventually check how big is the streak value?
			updated_habit_rows = self._repository.update_habit_field(habit_id, 'habit_streak', streak_value)
			return updated_habit_rows
		except HabitNotFoundError as herror:
			logging.error(f"Habit not found for user '{user_name}' and habit '{habit_name}': {herror}")
			raise
		except Exception as error:
			logging.error(f"Unexpected error in create_a_habit: {error}")
			raise

	def update_habit_periodicity_type(self, user_name, habit_name, type_value):
		try:
			habit_id = self.get_habit_id(user_name, habit_name)
			#we could eventually check how big is the streak value?
			updated_habit_rows = self._repository.update_habit_field(habit_id, 'habit_periodicity_type', type_value)
			return updated_habit_rows
		except HabitNotFoundError as herror:
			logging.error(f"Habit not found for user '{user_name}' and habit '{habit_name}': {herror}")
			raise
		except Exception as error:
			logging.error(f"Unexpected error in create_a_habit: {error}")
			raise

	def update_habit_periodicity_value(self, user_name, habit_name, value):
		try:
			habit_id = self.get_habit_id(user_name, habit_name)
			#we could eventually check how big is the streak valnue?
			
			updated_habit_rows = self._repository.update_habit_field(habit_id, 'habit_periodicity_value', value)
			return updated_habit_rows
		except HabitNotFoundError as herror:
			logging.error(f"Habit not found for user '{user_name}' and habit '{habit_name}': {herror}")
			raise
		except Exception as error:
			logging.error(f"Unexpected error in create_a_habit: {error}")
			raise

	def get_habit_id(self, user_name, habit_name):
		try:
			habit_id = self._repository.get_habit_id(user_name, habit_name)
			return habit_id
		except HabitNotFoundError as herror:
			logging.error(f"Habit not found for user '{user_name}' and habit '{habit_name}': {herror}")
			raise
		except Exception as error:
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
