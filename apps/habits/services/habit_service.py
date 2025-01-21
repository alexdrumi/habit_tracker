from apps.habits.repositories.habit_repository import HabitRepository
# from django.db import IntegrityError
from mysql.connector.errors import IntegrityError

from apps.users.repositories.user_repository import UserNotFoundError
import logging

class HabitService:
	def __init__(self):
		self._repository = HabitRepository()


	def create_a_habit(self, habit_name, habit_action, habit_streak, habit_periodicity_type, habit_periodicity_value, habit_user):
		try:
			habit_entity = self._repository.create_a_habit(habit_name, habit_action, habit_streak, habit_periodicity_type, habit_periodicity_value, habit_user)
			print(habit_entity)
			
			return habit_entity
		except IntegrityError as ierror:
			# Log the specific integrity error
			logging.error(f"Duplicate habit creation error: {ierror}")
			raise
		except UserNotFoundError as uerror:
			# Log the specific user not found error
			logging.error(f"User not found: {uerror}")
			raise
		except Exception as error:
			# Log unexpected errors
			logging.error(f"Unexpected error in create_a_habit: {error}")
			raise
