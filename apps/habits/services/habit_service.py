from apps.habits.repositories.habit_repository import HabitRepository, HabitNotFoundError, HabitRepositoryError, HabitAlreadyExistError
from mysql.connector.errors import IntegrityError
from apps.users.repositories.user_repository import UserNotFoundError
import logging



def handle_log_service_exceptions(f):
	def exception_wrapper(*args, **kwargs):
		try:
			return f(*args, **kwargs)
		# except (HabitAlreadyExistError, HabitRepositoryError) as specific_error:
		# 	logging.error(f"Service error in {f.__name__}: {specific_error}")
		# 	raise specific_error
		except Exception as error:
			logging.error(f"Service error in {f.__name__}: {error}")
			raise error
	return exception_wrapper


class HabitService:
	def __init__(self, repository: HabitRepository):
		self._repository = repository



	def _validate_habit_input(self, habit_name: str, habit_action: str, habit_periodicity_type: str, habit_user_id: int, habit_streak=None, habit_periodicity_value=None, is_update=False):
		"""
		Ensures habit data is valid according to business rules.
		"""
		if not isinstance(habit_name, str) or not habit_name.strip():  
			raise ValueError("Invalid habit name. It must be a non-empty string.")

		if not isinstance(habit_action, str) or not habit_action.strip(): 
			raise ValueError("Invalid habit action. It must be a non-empty string.")
		
		if not isinstance(habit_user_id, int) or habit_user_id <= 0:
			raise ValueError("Invalid user ID. It must be a positive integer. See list (option 3) for users for available user IDs.")

		valid_periodicity_types = {"DAILY", "WEEKLY"} 
		if habit_periodicity_type.upper() not in valid_periodicity_types:
			raise ValueError(f"Invalid habit periodicity type. Expected one of {valid_periodicity_types}.")

		if habit_streak is not None:
			if not isinstance(habit_streak, int) or habit_streak < 0:
				raise ValueError("Invalid habit streak. It must be a positive integer.")

		if habit_periodicity_value is not None:
			if not isinstance(habit_periodicity_value, int) or not (1 <= habit_periodicity_value <= 30):
				raise ValueError("Invalid periodicity value. It must be an integer between 1 and 30.")
		#we could also write one validate for habit_action == UPDATE


	@handle_log_service_exceptions
	def map_periodicity_value(self, habit_periodicity_type):
		"""
		Converts periodicity strings ('DAILY', 'WEEKLY', (eventually->'MONTHLY')) to numeric values.

		Args:
			habit_periodicity_type (str): Periodicity type string.

		Returns:
			int or None: Numeric mapping (1 for DAILY, 7 for WEEKLY, etc.),
			or None if the type is invalid.
		"""	
		capitalized_periodicity_type = habit_periodicity_type.strip().upper()
		periodicity_mapping = {
			"DAILY": 1,
			"WEEKLY": 7,
			"MONTHLY": 30
		}
		if capitalized_periodicity_type not in periodicity_mapping:
			return None

		return periodicity_mapping[capitalized_periodicity_type]



	@handle_log_service_exceptions
	def create_a_habit(self, habit_name, habit_action, habit_periodicity_type, habit_user_id, habit_streak=None, habit_periodicity_value=None):
		"""
		Creates a new habit after validating input.

		Args:
			habit_name (str): Name of the habit.
			habit_action (str): Action or behavior the habit represents.
			habit_periodicity_type (str): 'DAILY', 'WEEKLY', or 'MONTHLY'.
			habit_user_id (int): User ID of the habit owner.
			habit_streak (int, optional): Starting streak, default is None.
			habit_periodicity_value (int, optional): Interval value, e.g., 7 for weekly.

		Returns:
			dict: Data about the newly created habit, including habit_id.

		Raises:
			ValueError: If the input data fails validation.
			HabitAlreadyExistError: If a habit with the same name exists for the user.
		"""
		associated_periodicity_value = self.map_periodicity_value(habit_periodicity_type)
		if associated_periodicity_value == None:
			raise ValueError("Invalid periodicity type. Use 'DAILY', 'WEEKLY', or 'MONTHLY'.")
	
		self._validate_habit_input(
			habit_name=habit_name,
			habit_action=habit_action,
			habit_periodicity_type=habit_periodicity_type,
			habit_periodicity_value=associated_periodicity_value,
			habit_user_id=habit_user_id,
			habit_streak=0
		)

		#UnboundLocalError?=
		habit_entity = self._repository.create_a_habit(
			habit_name=habit_name, 
			habit_action=habit_action, 
			habit_periodicity_type=habit_periodicity_type, 
			habit_periodicity_value=associated_periodicity_value, 
			habit_user_id=habit_user_id, 
			habit_streak=0)
		return habit_entity



	def update_habit_streak(self, habit_id, updated_streak_value):
		"""
		Updates the streak count of a habit.

		Args:
			habit_id (int): The habit’s ID.
			updated_streak_value (int): The new streak value.

		Returns:
			int: Number of rows updated (1 if successful, 0 if no change).

		Raises:
			ValueError: If streak is not a positive integer.
			HabitNotFoundError: If the habit does not exist.
		"""
		if not isinstance(updated_streak_value, int) or updated_streak_value <= 0:
			raise ValueError("Invalid streak value. It must be a positive integer.")

		if not isinstance(habit_id, int) or habit_id <=0:
			raise ValueError("Invalid habit_id. It must be a positive integer.")
		
		validated_habit_id = self.validate_a_habit(habit_id)
		updated_habit_rows = self._repository.update_habit_field(validated_habit_id, 'habit_streak', updated_streak_value)
		return updated_habit_rows



	@handle_log_service_exceptions
	def update_habit_periodicity_type(self, user_name, habit_name, updated_type_value): #should type be updated? this should also automatically trigger value update no?
		"""
		Updates the periodicity type of a habit.

		Args:
			user_name (str): Name of the user who owns the habit.
			habit_name (str): Name of the habit to update.
			updated_type_value (str): New periodicity type ('DAILY', 'WEEKLY', etc.).

		Returns:
			int: Rows affected by the update.

		Raises:
			ValueError: If the updated type is invalid.
		"""
		associated_periodicity_value = self.map_periodicity_value(updated_type_value)
		if associated_periodicity_value is None:
			raise ValueError("Invalid periodicity type. Use 'DAILY', 'WEEKLY'.")

		habit_id = self.get_habit_id(user_name, habit_name)
		updated_habit_rows = self._repository.update_habit_field(habit_id, 'habit_periodicity_type', updated_type_value)
		return updated_habit_rows



	@handle_log_service_exceptions
	def update_habit_periodicity_value(self, user_name, habit_name, updated_value):
		"""
		Updates the numeric periodicity value of a habit.

		Args:
			user_name (str): The user’s name.
			habit_name (str): The habit’s name.
			updated_value (int): The new numeric interval (e.g., 7 for weekly).

		Returns:
			int: Rows affected by the update.

		Raises:
			ValueError: If the new periodicity value is not between 1 and 30.
		"""
		if not isinstance(updated_value, int) or not (1 <= updated_value <= 30):
			raise ValueError("Invalid periodicity value. It must be an integer between 1 and 30.")

		habit_id = self.get_habit_id(user_name, habit_name)
		updated_habit_rows = self._repository.update_habit_field(habit_id, 'habit_periodicity_value', updated_value)
		return updated_habit_rows



	@handle_log_service_exceptions
	def get_habit_id(self, user_name, habit_name):
		"""
		Retrieves the ID of a habit by user and habit name.

		Args:
			user_id (int): The user’s ID.
			habit_name (str): The habit’s name.

		Returns:
			int: The habit ID if found.

		Raises:
			ValueError: If user_id is invalid or habit_name is not a string.
			HabitNotFoundError: If the habit is not found.
		"""
		print(f"HABIT NAME IS: {habit_name}, USERNAME IS: {user_name}")
		if not isinstance(habit_name, str) or not isinstance(user_name, str):
			raise ValueError("Invalid input value. It must be a string for user_name and a str for habit_name.")
		
		habit_id = self._repository.get_habit_id(user_name, habit_name)
		return habit_id



	@handle_log_service_exceptions
	def get_periodicity_type(self, habit_id):
		"""
		Retrieves the periodicity type for the specified habit.

		Args:
			habit_id (int): The habit’s ID.

		Returns:
			tuple: The periodicity type (e.g., ('daily',)).

		Raises:
			ValueError: If habit_id is invalid.
			HabitPeriodicityTypeError: If no periodicity type is found.
		"""
		if not isinstance(habit_id, int) or habit_id <= 0:
			raise ValueError(f"Invalid habit id: {habit_id}.")
		
		habit_periodicity_type = self._repository.get_periodicity_type(habit_id)
		return habit_periodicity_type



	@handle_log_service_exceptions
	def validate_a_habit(self, habit_id):
		"""
		Ensures the habit with the given ID exists.

		Args:
			habit_id (int): The habit’s ID.

		Returns:
			int: The validated habit ID.

		Raises:
			ValueError: If habit_id is not an integer.
			HabitNotFoundError: If the habit is not found in the database.
		"""
		if not isinstance(habit_id, int): 
			raise ValueError(f"Invalid habit id: {habit_id}.")

		validated_habit_id = self._repository.validate_a_habit(habit_id)
		return validated_habit_id



	@handle_log_service_exceptions
	def delete_a_habit(self, user_name, habit_name):
		"""
		Removes a habit record by habit name and user name.

		Args:
			user_name (str): The user who owns the habit.
			habit_name (str): The habit’s name.

		Returns:
			int: Number of rows deleted.
		"""
		habit_id = self.get_habit_id(user_name, habit_name)
		deleted_count = self._repository.delete_a_habit(habit_id)
		return deleted_count



	@handle_log_service_exceptions
	def delete_a_habit_by_id(self, habit_id, goal_id):
		"""
		Deletes a habit by its ID, along with related goals/progress.

		Args:
			habit_id (int): The habit’s ID.
			goal_id (int): The related goal’s ID.

		Returns:
			int: Rows affected by the deletion.

		Raises:
			ValueError: If IDs are invalid.
		"""
		if not isinstance(habit_id, int) or habit_id <= 0: 
			raise ValueError(f"Invalid habit id: {habit_id}.")
		if not isinstance(goal_id, int) or goal_id <= 0: 
			raise ValueError(f"Invalid habit id: {goal_id}.")

		validated_habit_id = self.validate_a_habit(habit_id) #prob we could call validation from orchestrator as well
		deleted_count = self._repository.delete_a_habit(validated_habit_id, goal_id=goal_id)
		return deleted_count



	@handle_log_service_exceptions
	def delete_habit_physical_preserving_progress(self, habit_id, goal_id):
		"""
		Physically deletes a habit from the database, related progresses will persist.

		Args:
			habit_id (int): The habit’s ID.
			goal_id (int): The related goal’s ID used to clear progress references.

		Returns:
			int: Rows affected by the deletion.
		"""
		if not isinstance(habit_id, int) or habit_id <= 0: 
			raise ValueError(f"Invalid habit id: {habit_id}.")
		if not isinstance(goal_id, int) or goal_id <= 0: 
			raise ValueError(f"Invalid habit id: {goal_id}.")

		validated_habit_id = self.validate_a_habit(habit_id)
		deleted_count = self._repository.delete_habit_physical_preserving_progress(habit_id=validated_habit_id, goal_id=goal_id)
		return deleted_count



	@handle_log_service_exceptions
	def get_all_habits(self):
		"""
		Retrieves all habits from the database.

		Returns:
			list: A list of tuples describing each habit.
		"""
		list_of_habits = self._repository.get_all_habits()
		return list_of_habits



	@handle_log_service_exceptions
	def get_goal_of_habit(self, habit_id):
		"""
		Fetches the goal(s) associated with a specific habit.

		Args:
			habit_id (int): The habit’s ID.

		Returns:
			list: A list of goal IDs tied to this habit.

		Raises:
			ValueError: If habit_id is invalid.
			HabitNotFoundError: If no goals or habit is found.
		"""
		if not isinstance(habit_id, int) or habit_id <= 0: 
			raise ValueError(f"Invalid habit id: {habit_id}.")
		goal_id = self._repository.get_goal_of_habit(habit_id)
		return goal_id



	@handle_log_service_exceptions
	def get_current_streak(self, habit_id):
		"""
		Retrieves the current streak for a specific habit.

		Args:
			habit_id (int): The habit’s ID.

		Returns:
			tuple: Contains the streak value (e.g., (5,)).

		Raises:
			ValueError: If habit_id is invalid.
			HabitNotFoundError: If the habit does not exist.
		"""
		if not isinstance(habit_id, int) or habit_id <= 0: 
			raise ValueError(f"Invalid habit id: {habit_id}.")
		
		validated_habit_id = self.validate_a_habit(habit_id)
		streak = self._repository.get_current_streak(habit_id=validated_habit_id)
		
		return streak