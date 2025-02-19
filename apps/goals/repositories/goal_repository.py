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


#baseclass
class GoalRepositoryError(Exception):
	def __init__(self, message="An unexpected error occurred in goal repository."):
		super().__init__(message)


class GoalNotFoundError(GoalRepositoryError):
	"""Raised when a goal is not found."""
	def __init__(self, goal_id):
		message = f"Goal not found with ID: {goal_id}"
		super().__init__(message)


class GoalAlreadyExistError(GoalRepositoryError):
	"""Raised when creating goal fails due to a already existing entry."""
	def __init__(self, goal_name, goal_user_id):
		message = f"Goal '{goal_name}' already exists for user with id: {goal_user_id}"
		super().__init__(message)

def handle_goal_repository_errors(f):
	"""Decorator to clean up and handle errors in goal repository methods."""
	def exception_wrapper(self, *args, **kwargs):
		try:
			return f(self, *args, **kwargs)
		except IntegrityError as ierror:
			self._db._connection.rollback()
			#in create_a_habit the first argument is habit_name and last is habit_user_id?
			raise GoalAlreadyExistError(goal_name=args[0], goal_user_id=args[-1]) from ierror
		except GoalRepositoryError as herror:
			raise herror
		except Exception as error:
			self._db._connection.rollback()
			raise error
	return exception_wrapper



class GoalRepository:
	def __init__(self, database: MariadbConnection, habit_repository: HabitRepository): #, kvi_repository: KviTypeRepository
		self._db = database
		self._habit_repository = habit_repository
		# self._kvi_repository = kvi_repository


	@handle_goal_repository_errors
	def validate_a_goal(self, goal_id):
		with self._db._connection.cursor() as cursor:
			query = "SELECT goal_id FROM goals WHERE goal_id = %s;"
			cursor.execute(query, (goal_id,))
			current_value = cursor.fetchone()

			if not current_value:
				raise GoalNotFoundError(goal_id)
			return current_value[0] #no rows updated but also no error found
	

	@handle_goal_repository_errors
	def create_a_goal(self, goal_name, habit_id, target_kvi_value, current_kvi_value, goal_description):
		'''
		Create a goal in the goals table.

		Args:
			(str, int, int, int, str): The name, habit_id, target_kvi_value, current_kvi_value type, goal_description of the goal."
		
		Returns:
			Dict: Entire goal entity.
		'''
		with self._db._connection.cursor() as cursor:
			query = "INSERT INTO goals(goal_name, habit_id_id, target_kvi_value, current_kvi_value, goal_description, created_at) VALUES (%s, %s, %s, %s, %s,  NOW());"
			cursor.execute(query, (goal_name, habit_id, target_kvi_value, current_kvi_value, goal_description))
			self._db._connection.commit()
			return {
				'goal_id': cursor.lastrowid,
				'goal_name': goal_name,
				'target_kvi_value': target_kvi_value,
				'current_kvi_value': current_kvi_value,
				'goal_description': goal_description,
				'habit_id_id': habit_id,
				# 'kvi_type_id_id': kvi_type_id,
			}


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

	@handle_goal_repository_errors
	def get_goal_entity_by_id(self, goal_id, habit_id):
		#we will validate the habit in the service layer so by this time it exists
		with self._db._connection.cursor() as cursor:
			query = "SELECT goal_id, target_kvi_value, current_kvi_value FROM goals WHERE (goal_id = %s AND habit_id_id = %s)"
			cursor.execute(query, (goal_id, habit_id))
			result = cursor.fetchall()
			if result:
				return result
			else:
				raise GoalNotFoundError(goal_id)

	@handle_goal_repository_errors
	def get_current_kvi(self, goal_id):
		with self._db._connection.cursor() as cursor:
			query = "SELECT current_kvi_value FROM goals WHERE goal_id = %s"
			cursor.execute(query, (goal_id,))
			result = cursor.fetchone() #later it might be more goals, for now will be one

			if result:
				return result[0]
			else:
				raise GoalNotFoundError(goal_id)


	@handle_goal_repository_errors
	def update_goal_field(self, goal_id, goal_name=None, target_kvi_value=None, current_kvi_value=None):
		try:

			#WE GOTTA DO SOME INPUT VALIDATION OUTSIDE
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

	@handle_goal_repository_errors
	def delete_a_goal(self, goal_id):
		'''
		Create a goal in the goals table.

		Args:
			(str, int, int, int, str): The name, habit_id, target_kvi_value, current_kvi_value type, goal_description of the goal."
		
		Returns:
			Dict: Entire goal entity.
		'''
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
	
	@handle_goal_repository_errors
	def query_goals_and_related_habits(self):
		'''
		Requests all goals with their associated habits.

		Args:
			None
		
		Returns:
			dict(list): every goal data with goal_name, goal_id, habit_name, habit_id
		'''
		with self._db._connection.cursor() as cursor:
			query = "SELECT goal_name, goal_id, habit_id_id, habit_name from goals INNER JOIN habits ON goals.habit_id_id = habits.habit_id;"
			cursor.execute(query)

			result = cursor.fetchall()

			if result:
				return result
			else:
				return []


	@handle_goal_repository_errors
	def query_goals_of_a_habit(self, habit_id):
		'''
		Requests all goals of one specific habit. Initially this will be only one goal per habit, eventually can have more goals.

		Args:
			None
		
		Returns:
			dict(list): every goal data with goal_name, goal_id, habit_name, habit_id
		'''
		with self._db._connection.cursor() as cursor:
			query = "SELECT goal_name, goal_id, habit_id_id, habit_name from goals INNER JOIN habits ON %s = goals.habit_id_id;"
			cursor.execute(query, (habit_id, ))

			result = cursor.fetchall()

			if result:
				return result
			else:
				return []