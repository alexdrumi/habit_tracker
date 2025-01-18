from apps.users.models import AppUsers
from apps.database.database_manager import MariadbConnection
from apps.users.repositories.user_repository import UserNotFoundError

class HabitNotFoundError(Exception):
	"""Custom exception raised when a user is not found."""
	pass

# class HabitCreationError(Exception):
# 	"""Custom raised when a role cannot be created."""
# 	pass
class HabitRepository:
	def __init__(self):
		self._db = MariadbConnection()

	def create_a_habit(self, habit_name, habit_action, habit_streak, habit_periodicity_type, habit_periodicity_value, habit_user):
		'''
		Create a habit in the habits table.

		Args:
			(str, str, int, str, int, int): The name, action, streak, periodicity type, periodicity value, habit user of the habit.
		
		Returns:
			int: The id of existing or newly created role. To be used as a foreign key in app_users.
		'''
		try:
			with self._db._connection.cursor() as cursor:
				#check whether there is a habit user with that habit user entity (user id?)
				query_user = f"SELECT user_id from app_users WHERE user_name = %s"
				cursor.execute(query_user, (habit_user,))
				result_user = cursor.fetchone()
				if not result_user:
					raise UserNotFoundError(f"User with user_name {habit_user} is not found.")

				print(result_user)
				query = "INSERT INTO habits(habit_name, habit_action, habit_streak, habit_periodicity_type, habit_periodicity_value, habit_user_id, created_at) VALUES (%s, %s, %s, %s, %s, %s, NOW());"
				cursor.execute(query, (habit_name, habit_action, habit_streak, habit_periodicity_type, habit_periodicity_value, result_user[0]))
				self._db._connection.commit()
				return {
					'habit_id': cursor.lastrowid,
					'habit_action': habit_action,
					'habit_streak': habit_streak,
					'habit_periodicity_type': habit_periodicity_type,
					'habit_periodicity_value': habit_periodicity_value,
					'habit_user_id': result_user[0],
				}
		except Exception as error:
			self._db._connection.rollback()
			raise



	# def delete_a_user(self, user_id):
	# 	'''
	# 	Delete a user from the app_users table.

	# 	Args:
	# 		user_id (int): ID of the user.

	# 	Returns:
	# 		int: Number of rows effected by deletion.
	# 	'''
	# 	try:
	# 		with self._db._connection.cursor() as cursor: #this closes cursor anyway, https://www.psycopg.org/docs/cursor.html
	# 			query = "DELETE FROM app_users WHERE user_id = %s"
	# 			cursor.execute(query, (user_id,))
	# 			self._db._connection.commit()
	# 			if cursor.rowcount == 0:
	# 				raise UserNotFoundError(f"User with user_name {user_id} is not found.")
	# 			return cursor.rowcount #nr of rows effected in DELETE SQL, this could also be just a bool but x>0 will act anyway as bool
	# 	except Exception as error:
	# 		self._db._connection.rollback()
	# 		raise
		


	# #TODO, make this less repetitive, there must be a pretty pythonic way for the if blocks
	# def update_a_user(self, user_name, user_age=None, user_gender=None, user_role=None):
	# 	'''
	# 	Update a user from the app_users table.

	# 	Args:
	# 		user_role (str, int, str, str): The new name, new age, new gender and new role of the user.
		
	# 	Returns:
	# 		int: Number of rows effected by update.
	# 	'''
	# 	try:
	# 		updated_cols = []
	# 		updated_vals = []
	# 		if user_name is not None:
	# 			updated_cols.append("user_name = %s")
	# 			updated_vals.append(user_name)

	# 		if user_age is not None:
	# 			updated_cols.append("user_age = %s")
	# 			updated_vals.append(user_age)

	# 		if user_gender is not None:
	# 			updated_cols.append("user_gender = %s")
	# 			updated_vals.append(user_gender)

	# 		if user_role is not None:
	# 			#if you need a role_id, you can call self.create_a_role(user_role) to create it
	# 			role_id = self.create_a_role(user_role)
	# 			updated_cols.append("user_role_id = %s")
	# 			updated_vals.append(role_id)
			
	# 		if not updated_cols:
	# 			return 0
	# 		set_commands = ', '.join(updated_cols) 
	# 		query = f"UPDATE app_users SET {set_commands} WHERE user_name = %s"
	# 		updated_vals.append(user_name) #once more for the where clause
			
	# 		with self._db._connection.cursor() as cursor:
	# 			cursor.execute(query, updated_vals)
	# 			self._db._connection.commit()
				
	# 			if cursor.rowcount == 0:
	# 				raise UserNotFoundError(f"User with user_name {user_name} is not found.")
	# 			return cursor.rowcount #nr of rows effected in UPDATE SQL (ideally 1)
	# 	except Exception as error:
	# 		self._db._connection.rollback()
	# 		raise



	# def get_user_id(self, user_name):
	# 	'''
	# 	Get the user_id based on a user_name.

	# 	Args:
	# 		user_name (str): The name of the user.
		
	# 	Returns:
	# 		int: The ID of the user.
	# 	'''
	# 	try:
	# 		with self._db._connection.cursor() as cursor:
	# 			query =  f"SELECT user_id from app_users WHERE user_name = %s"
	# 			cursor.execute(query, (user_name,))
	# 			result = cursor.fetchone()
	# 			if result:
	# 				user_id_idx = 0
	# 				return result[user_id_idx]
	# 			else: #select only handles read only query, no need for rollback, no changes in the database
	# 				raise UserNotFoundError(f"User with user_name: {user_name} is not found.")
	# 	except Exception as error: #rolback for unexpected errors
	# 		self._db._connection.rollback()
	# 		raise




