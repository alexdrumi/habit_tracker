from apps.users.models import AppUsers
from apps.database.database_manager import MariadbConnection

class UserRepository:
	def __init__(self):
		self._db = MariadbConnection()


	def create_a_role(self, user_role):
		'''
		Create a user role in the app_users_roles table. ID will be used as a foreign key in app_user.

		Args:
			user_role (str): The name of the user role (admin, user, bot).
		
		Returns:
			int: The id of existing or newly created role. To be used as a foreign key in app_users.
		'''
		try:
			cursor = self._db._connection.cursor()
			#check if role already there
			query = "SELECT user_role from app_users_role WHERE user_role = %s"
			cursor.execute(query, (user_role,))
			result = cursor.fetchone() #can be only one entry here, more efficient than fetchall()
			if result:
				cursor.close()
				return result[0]

			#if not found, create a new one
			query = "INSERT INTO app_users_role(user_role) VALUES (%s);"
			cursor.execute(query, (user_role,))
			self._db._connection.commit()
			return cursor.lastrowid #id we need to creating users

		except Exception as error:
			#could log but print for now
			print(f"Error while creating a role: {error}")
			self._db._connection.rollback()
			raise
		finally:
			cursor.close()


	def create_a_user(self, user_name, user_age, user_gender, user_role):
		'''
		Create a user in the app_users table.

		Args:
			user_role (str, int, str, str): The name, age, gender and role of the user.
		
		Returns:
			int: The id of existing or newly created role. To be used as a foreign key in app_users.
		'''
		try:
			cursor = self._db._connection.cursor()
			user_role_id = self.create_a_role(user_role)
			query = "INSERT INTO app_users(user_name, user_age, user_gender, user_role_id, created_at) VALUES (%s, %s, %s, %s, NOW());"
			cursor.execute(query, (user_name, user_age, user_gender, user_role_id,))
			self._db._connection.commit()
			return {
				'user_id': cursor.lastrowid,
				'user_name': user_name,
				'user_role': user_role
			} #dict with potentially needed info
		except Exception as error:
			print(f"Error while creating a user: {error}")
			self._db._connection.rollback()
			raise
		finally:
			cursor.close()


	def delete_a_user(self, user_id):
		'''
		Delete a user from the app_users table.

		Args:
			user_id (int): ID of the user.

		Returns:
			int: Number of rows effected by deletion.
		'''
		try:
			cursor = self._db._connection.cursor()
			query = "DELETE FROM app_users WHERE user_id = %s"
			cursor.execute(query, (user_id,))
			self._db._connection.commit()
			return cursor.rowcount #nr of rows effected (ideally 1)
		except Exception as error:
			print(f"Error while deleting a user: {error}")
			self._db._connection.rollback()
			raise
		finally:
			cursor.close()


	#TODO, UPDATE BASED ON USER ID NOT NAME
	def update_a_user(self, user_name, user_age=None, user_gender=None, user_role=None):
		'''
		Update a user from the app_users table.

		Args:
			user_role (str, int, str, str): The new name, new age, new gender and new role of the user.
		
		Returns:
			int: Number of rows effected by update.
		'''
		try:
			cursor = self._db._connection.cursor()
			updated_cols = []
			updated_vals = []
			if user_name is not None:
				updated_cols.append("user_name = %s")
				updated_vals.append(user_name)

			if user_age is not None:
				updated_cols.append("user_age = %s")
				updated_vals.append(user_age)

			if user_gender is not None:
				updated_cols.append("user_gender = %s")
				updated_vals.append(user_gender)

			if user_role is not None:
				#if you need a role_id, you can call self.create_a_role(user_role) to create it
				role_id = self.create_a_role(user_role)
				updated_cols.append("user_role_id = %s")
				updated_vals.append(role_id)
			
			if not updated_cols:
				# if there is nothing to update
				return 0
			set_commands = ', '.join(updated_cols) 
			query = f"UPDATE app_users SET {set_commands} WHERE user_name = %s"
			updated_vals.append(user_name) #once more for the username
			cursor.execute(query, updated_vals)
			self._db._connection.commit()
			return cursor.rowcount #nr of rows effected (ideally 1)
		
		except Exception as error:
			print(f"Error while updating a user: {error}")
			self._db._connection.rollback()
			raise
		finally:
			cursor.close()


	# def get_user_by_id(self, user_name):
