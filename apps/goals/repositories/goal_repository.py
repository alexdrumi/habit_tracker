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
		"""
		Checks if a goal with the given ID exists.

		Args:
			goal_id (int): ID of the goal to validate.

		Returns:
			int: The validated goal ID.

		Raises:
			GoalNotFoundError: If the goal is not found.
		"""
		with self._db._connection.cursor() as cursor:
			query = "SELECT goal_id FROM goals WHERE goal_id = %s;"
			cursor.execute(query, (goal_id,))
			current_value = cursor.fetchone()

			if not current_value:
				raise GoalNotFoundError(goal_id)
			return current_value[0]
	



	@handle_goal_repository_errors
	def create_a_goal(self, goal_name, habit_id, target_kvi_value, current_kvi_value, goal_description):
		"""
		Creates a new goal record in the database.

		Args:
			goal_name (str): The goal’s name.
			habit_id (int): The associated habit’s ID.
			target_kvi_value (float): The target KVI to reach.
			current_kvi_value (float): The current KVI progress.
			goal_description (str): Brief description of the goal.

		Returns:
			dict: Details of the newly created goal.

		Raises:
			GoalAlreadyExistError: If a duplicate goal is detected.
		"""
		with self._db._connection.cursor() as cursor:
			query = "INSERT INTO goals(goal_name, habit_id_id, target_kvi_value, current_kvi_value, goal_description, created_at) VALUES (%s, %s, %s, %s, %s,  NOW());"
			cursor.execute(query, (goal_name, habit_id, target_kvi_value, current_kvi_value, goal_description, ))
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


	@handle_goal_repository_errors
	def get_goal_id(self, goal_name, habit_id):
		"""
		Retrieves the goal ID for a given name and habit combination.

		Args:
			goal_name (str): Name of the goal.
			habit_id (int): Habit ID to which the goal belongs.

		Returns:
			int: The found goal ID.

		Raises:
			GoalNotFoundError: If the goal is not found in the database.
		"""
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



	@handle_goal_repository_errors
	def get_goal_entity_by_id(self, goal_id, habit_id):
		"""
		Fetches a goal entity matching the provided goal and habit IDs.

		Args:
			goal_id (int): The goal’s ID.
			habit_id (int): The habit’s ID linked to the goal.

		Returns:
			dict: Goal information including name, KVI values, and streak.

		Raises:
			GoalNotFoundError: If the goal does not exist.
		"""
		with self._db._connection.cursor() as cursor:
			# "SELECT g.goal_id, g.habit_id_id, g.target_kvi_value, g.current_kvi_value, h.habit_streak FROM goals g JOIN habits h ON g.habit_id_id = h.habit_id WHERE g.goal_id = %s AND g.habit_id_id = %s";
			# query = "SELECT goal_id, habit_id_id, target_kvi_value, current_kvi_value FROM goals WHERE (goal_id = %s AND habit_id_id = %s)"
			query = "SELECT g.goal_id, g.goal_name, g.habit_id_id, h.habit_name, g.target_kvi_value, g.current_kvi_value, h.habit_streak FROM goals g JOIN habits h ON g.habit_id_id = h.habit_id WHERE g.goal_id = %s AND g.habit_id_id = %s;"
			cursor.execute(query, (goal_id, habit_id))
			result = cursor.fetchone()
			if result:
				return {
					'goal_id': result[0],
					'goal_name': result[1],
					'habit_id': result[2],
					'habit_name': result[3],
					'target_kvi': result[4],
					'current_kvi': result[5],
					'streak': result[6]
				}
			else:
				raise GoalNotFoundError(goal_id)



	@handle_goal_repository_errors
	def get_current_kvi(self, goal_id):
		"""
		Retrieves the current KVI value for a goal.

		Args:
			goal_id (int): ID of the goal.

		Returns:
			float: The current KVI value.

		Raises:
			GoalNotFoundError: If the goal doesn’t exist.
		"""
		with self._db._connection.cursor() as cursor:
			query = "SELECT current_kvi_value FROM goals WHERE goal_id = %s"
			cursor.execute(query, (goal_id,))
			result = cursor.fetchone() #later there migh be more goals (fetchall), for now will be one
			if result:
				return result[0]
			else:
				raise GoalNotFoundError(goal_id)



	@handle_goal_repository_errors
	def update_goal_field(self, goal_id, goal_name=None, target_kvi_value=None, current_kvi_value=None):
		"""
		Updates one or more fields on a goal record.

		Args:
			goal_id (int): ID of the goal to update.
			goal_name (str, optional): New goal name, if any.
			target_kvi_value (float, optional): New target KVI.
			current_kvi_value (float, optional): New current KVI.

		Returns:
			int: Number of rows affected by the update.

		Raises:
			GoalNotFoundError: If the goal doesn’t exist or rowcount is 0.
		"""
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

			if cursor.rowcount == 0: #if values are the same its also the case, thus this is incorrect
				raise GoalNotFoundError(f"Goal with goal_id {goal_id} is not found.")

			return cursor.rowcount #nr of rows effected in UPDATE SQL (ideally 1)



	@handle_goal_repository_errors
	def delete_a_goal(self, goal_id):
		"""
		Deletes a goal record by ID.

		Args:
			goal_id (int): The ID of the goal to delete.

		Returns:
			int: Number of rows deleted.

		Raises:
			GoalNotFoundError: If the goal does not exist.
		"""
		with self._db._connection.cursor() as cursor:
			query = f"DELETE FROM goals WHERE goal_id = %s"
			cursor.execute(query, (goal_id,))
			self._db._connection.commit()
			
			if cursor.rowcount == 0:
				raise GoalNotFoundError(f"Goal of with id {goal_id} is not found.")
			return cursor.rowcount




	@handle_goal_repository_errors
	def query_goals_and_related_habits(self):
		"""
		Retrieves all goals with their associated habit data.

		Returns:
			list: A list of tuples containing goal and habit fields, or empty list of none is found.
		"""
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
		"""
		Retrieves all goals linked to a specific habit.

		Args:
			habit_id (int): The ID of the habit.

		Returns:
			list: A list of goals (and habit details) for the given habit.
		"""
		with self._db._connection.cursor() as cursor:
			query = "SELECT goal_name, goal_id, habit_id_id, habit_name, habit_periodicity_value from goals INNER JOIN habits ON %s = goals.habit_id_id;"
			cursor.execute(query, (habit_id, ))

			result = cursor.fetchall()
			if result:
				return result
			else:
				return []



	@handle_goal_repository_errors
	def query_goal_of_a_habit(self, habit_id):
		"""
		Retrieves a single goal ID for the specified habit (if it exists).

		Args:
			habit_id (int): The habit’s ID.

		Returns:
			list or tuple: The matching goal ID, or empty if none found.
		"""
		with self._db._connection.cursor() as cursor:
			query = "SELECT goal_id from goals WHERE habit_id_id = %s"
			cursor.execute(query, (habit_id, ))

			result = cursor.fetchone()
			if result:
				return result
			else:
				return []
	


	@handle_goal_repository_errors
	def query_all_goals(self):
		"""
		Retrieves all goals from the database.

		Returns:
			list of dict: Each item containing goal_id, habit_id, target_kvi_value,
			current_kvi_value, and goal_name, or an empty list.
		"""
		with self._db._connection.cursor() as cursor:
			query = "SELECT goal_id, habit_id_id, target_kvi_value, current_kvi_value, goal_name FROM goals;"
			cursor.execute(query)
			result = cursor.fetchall()

			if result:
				return [{"goal_id": row[0], "habit_id": row[1], "target_kvi_value": row[2], "current_kvi_value":row[3], "goal_name": row[4]} for row in result]
			else:
				return []



	#this technically could be in the progresses service.
	@handle_goal_repository_errors
	def get_last_progress_entry_associated_with_goal_id(self, goal_id):
		"""
			Fetches the most recent progress entry (by date) for a given goal.

		Args:
			goal_id (int): The goal’s ID.

		Returns:
			dict or list: A dict containing occurence_date or an empty list if none.

		Raises:
			GoalNotFoundError: If the query fails or the goal is invalid.
		"""
		with self._db._connection.cursor() as cursor:
			query = "SELECT occurence_date FROM progresses WHERE goal_id_id = %s ORDER BY occurence_date DESC LIMIT 1;"
			cursor.execute(query, (goal_id,))

			result = cursor.fetchone()

			if result:
				return {"occurence_date": result[0]}
			else:
				return []
	
		