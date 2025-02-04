from apps.users.models import AppUsers
from apps.database.database_manager import MariadbConnection
from apps.users.repositories.user_repository import UserRepository, UserNotFoundError
from apps.users.services.user_service import UserService
from apps.habits.repositories.habit_repository import HabitRepository, HabitNotFoundError
from apps.kvi_types.repositories.kvi_type_repository import KviTypeRepository, KviTypesNotFoundError

#from django.db import IntegrityError
from mysql.connector.errors import IntegrityError

#goal_name, habit_id, kvi_type_id, target_kvi_value, current_kvi_value, goal_description
class GoalNotFoundError(Exception):
	"""Custom exception raised when a user is not found."""
	pass

class GoalRepository:
	def __init__(self, database: MariadbConnection, habit_repository: HabitRepository, kvi_repository: KviTypeRepository):
		self._db = database
		self._habit_repository = habit_repository
		self._kvi_repository = kvi_repository


	def validate_a_goal(self, goal_id):
		try:
			with self._db._connection.cursor() as cursor:
				query = "SELECT goal_id FROM goals WHERE goal_id = %s;"
				cursor.execute(query, (goal_id,))
				current_value = cursor.fetchone()

				if not current_value:
					raise GoalNotFoundError(f"Goal with id of: {goal_id} is not found.")
				return current_value[0] #no rows updated but also no error found
		except Exception as error:
			self._db._connection.rollback()  # Required if using manual transactions
			raise		


	def create_a_goal(self, goal_name, habit_id, kvi_type_id, target_kvi_value, current_kvi_value, goal_description):
		'''
		Create a goal in the goals table.
		'''
		try:
			with self._db._connection.cursor() as cursor:
				#probably validation should happen in the service later
				# validated_kvi = self._kvi_repository.validate_a_kvi_type(kvi_type_id)
				# validated_habit = self._habit_repository.validate_a_habit(habit_id)

				query = "INSERT INTO goals(goal_name, habit_id_id, kvi_type_id_id, target_kvi_value, current_kvi_value, goal_description, created_at) VALUES (%s, %s, %s, %s, %s, %s, NOW());"
				cursor.execute(query, (goal_name, habit_id, kvi_type_id, target_kvi_value, current_kvi_value, goal_description))
				self._db._connection.commit()
				return {
					'goal_id': cursor.lastrowid,
					'goal_name': goal_name,
					'target_kvi_value': target_kvi_value,
					'current_kvi_value': current_kvi_value,
					'goal_description': goal_description,
					'habit_id_id': habit_id,
					'kvi_type_id_id': kvi_type_id,
				}
		except IntegrityError as ierror:
			if "Duplicate entry" in str(ierror):
				raise IntegrityError(f"Duplicate goal '{goal_name}' for habit with id '{habit_id}'.") from ierror
			raise
		except Exception as error:
			self._db._connection.rollback()
			raise


	def get_goal_id(self, goal_name, habit_id):
		try:
			#we will validate the habit in the service layer so by this time it exists
			with self._db._connection.cursor() as cursor:
				query = "SELECT goal_id FROM goals WHERE (goal_name = %s AND habit_id = %s)"
				cursor.execute(query, (goal_name, habit_id))
				result = cursor.fetchone()
				if result:
					kvi_type_id_idx = 0
					return result[kvi_type_id_idx]
				else:
					raise GoalNotFoundError(f"Goal name: {goal_name} and habit id: {habit_id} is not found.")
		except Exception as error: #rolback for unexpected errors
			self._db._connection.rollback()
			raise



	def update_goal_field(self, goal_id, goal_name=None, target_kvi_value=None, current_kvi_value=None):
		try:
			updated_fields = []
			updated_values = []

			if goal_name is not None:
				updated_fields.append('goal_name = %s')
				updated_values.append(goal_name)
			
			if target_kvi_value is not None:
				updated_fields.append('target_kvi_value = %s')
				updated_values.append(target_kvi_value)

			if current_kvi_value is not None:
				updated_fields.append('current_kvi_value = %s')
				updated_values.append(current_kvi_value)

			if not updated_fields:
				return 0

			set_commands = ', '.join(updated_fields) #goal_name = %s, target_kvi_value = %s etc
			updated_values.append(goal_id)

			query = "UPDATE goals SET " + set_commands + " WHERE goal_id = %s;"
			with self._db._connection.cursor() as cursor:
				cursor.execute(query, updated_values)
				self._db._connection.commit()

				if cursor.rowcount == 0: #this should be checked by now tbh
					raise GoalNotFoundError(f"Goal with goal_id {goal_id} is not found.")
				return cursor.rowcount #nr of rows effected in UPDATE SQL (ideally 1)
		except Exception as error:
			self._db._connection.rollback()
			raise


	def delete_a_goal(self, goal_id):
		try:
			#validate goal in the service layer
			with self._db._connection.cursor() as cursor:
				query = f"DELETE FROM goals WHERE goal_id = %s"
				cursor.execute(query, (goal_id,))
				self._db._connection.commit()
				
				if cursor.rowcount == 0:
					raise GoalNotFoundError(f"Goal of with id {goal_id} is not found.")
				return cursor.rowcount #nr of rows effected in DELETE SQL, this could also be just a bool but x>0 will act anyway as bool
		except Exception as error:
				self._db._connection.rollback()
				raise
	


