from apps.habits.repositories.habit_repository import HabitRepository
from apps.database.database_manager import MariadbConnection
from mysql.connector.errors import IntegrityError

class AnalyticsNotFoundError(Exception):
	"""Custom exception raised when analytics is not found."""
	pass


class AnalyticsRepository:
	def __init__(self, database: MariadbConnection, habit_repository: HabitRepository):
		self._db = database
		self._habit_repository = habit_repository


	def create_analytics(self, times_completed, streak_length, habit_id, last_completed_at=None):
		'''
		Create analytics for a certain analytics.
		'''
		try:
			#validation of habit will come from the service layer
			with self._db._connection.cursor() as cursor:
				#probably validation should happen in the service later
		
				query = "INSERT INTO analytics(times_completed, streak_length, last_completed_at, created_at, habit_id_id) VALUES (%s, %s, %s, NOW(), %s);"
				cursor.execute(query, (times_completed, streak_length, last_completed_at, habit_id))
				self._db._connection.commit()
				return {
					'analytics_id': cursor.lastrowid,
					'times_completed': times_completed,
					'streak_length': streak_length,
					'last_completed_at': last_completed_at,
					'habit_id_id': habit_id,
				}
		except IntegrityError as ierror:
			if "Duplicate entry" in str(ierror):
				raise IntegrityError(f"Duplicate analytics for habit with id '{habit_id}'.") from ierror
			raise
		except Exception as error:
			self._db._connection.rollback()
			raise


	def get_analytics_id(self, habit_id):
		try:
			with self._db._connection.cursor() as cursor:
				query = "SELECT analytics_id FROM analytics WHERE habit_id_id = %s;"
				cursor.execute(query, (habit_id,))
				result = cursor.fetchone()
				if result:
					analytics_id_idx = 0
					return result[analytics_id_idx]
				else:
					raise AnalyticsNotFoundError(f"Analytics for habit with id {habit_id} is not found.")

		except Exception as error: #rolback for unexpected errors
			self._db._connection.rollback()
			raise
	

	def update_analytics(self, analytics_id, times_completed=None, streak_length=None, last_completed_at=None):
		try:
			print("INSIDE UPDATE ANALYTICS REPO")
			updated_fields = []
			updated_values = []

			if times_completed is not None:
				updated_fields.append("times_completed = %s")
				updated_values.append(times_completed)
			
			if streak_length is not None:
				updated_fields.append("streak_length = %s")
				updated_values.append(streak_length)

			if last_completed_at is not None:
				updated_fields.append("last_completed_at = %s")
				updated_values.append(last_completed_at)
			
			if not updated_fields:
				return 0
			
			set_commands = ', '.join(updated_fields)
			updated_values.append(analytics_id)

			query = "UPDATE analytics SET " + set_commands + " WHERE analytics_id = %s;"
			with self._db._connection.cursor() as cursor:
				cursor.execute(query, updated_values)
				self._db._connection.commit()

				if cursor.rowcount == 0: #shouldnt be the case by now
					raise AnalyticsNotFoundError(f"Analytics for habit with analytiacs {analytics_id} is not found.")

				return cursor.rowcount #nr of rows effected in UPDATE SQL (ideally 1)
		except Exception as error:
			self._db._connection.rollback()
			raise


	def delete_analytics(self, analytics_id):
		try:
			with self._db._connection.cursor() as cursor:
				query = "DELETE FROM analytics WHERE analytics_id = %s"
				result = cursor.execute(query, (analytics_id,))
				self._db._connection.commit()
				if cursor.rowcount == 0:
					raise AnalyticsNotFoundError(f"Analytics for habit with id {habit_id} is not found.")
				return cursor.rowcount #nr of rows effected in UPDATE SQL (ideally 1)
				
		except Exception as error:
				self._db._connection.rollback()
				raise

	
	def calculate_longest_streak(self):
		try:
			with self._db._connection.cursor() as cursor:
				query = "SELECT habit_id, habit_name, habit_streak FROM habits WHERE habit_streak = (SELECT MAX(habit_streak) FROM habits) ORDER BY habit_streak DESC;"
				
				cursor.execute(query)
				result = cursor.fetchone()
				#no commit needed, nothing changed
				if result:
					return result
				else:
					raise AnalyticsNotFoundError(f"Analytics is not found.")

		except Exception as error: #rolback for unexpected errors
			self._db._connection.rollback()
			raise


	def get_same_periodicity_type_habits(self):
		try:
			with self._db._connection.cursor() as cursor:
				query = "SELECT habit_periodicity_type, COUNT(*) AS habit_count, GROUP_CONCAT(CONCAT(habit_id, ': ', habit_name) SEPARATOR ', ') AS habit_list FROM habits GROUP BY habit_periodicity_type ORDER BY habit_count DESC;"

				cursor.execute(query)
				result = cursor.fetchall()

				if result:
					return result
				else:
					raise AnalyticsNotFoundError(f"Analytics is not found.")
			
		except Exception as error: #rolback for unexpected errors
			self._db._connection.rollback()
			raise


	def get_currently_tracked_habits(self):
		try:
			with self._db._connection.cursor() as cursor:
				query = "SELECT habit_id, habit_name, habit_streak, habit_periodicity_type FROM habits WHERE habit_streak > 0;"

				cursor.execute(query)
				result = cursor.fetchall()

				if result:
					return result
				else:
					raise AnalyticsNotFoundError(f"Analytics is not found.")
			
		except Exception as error: #rolback for unexpected errors
			self._db._connection.rollback()
			raise

	def longest_streak_for_habit(self, habit_id):
		try:
			with self._db._connection.cursor() as cursor:
				query = " SELECT p.* FROM progresses p JOIN goals g ON p.goal_id_id = g.goal_id WHERE g.habit_id_id = %s ORDER BY p.current_streak DESC LIMIT 1;"
				cursor.execute(query, (habit_id, ))

				result = cursor.fetchall()
			if result:
				return result
			else:
				raise AnalyticsNotFoundError(f"Analytics is not found.")
	
		except Exception as error: #rolback for unexpected errors
			self._db._connection.rollback()
			raise

	# #https://mariadb.com/kb/en/json_arrayagg/ , otherwise I would have split calls in the layers above. This is gonna be a simple loop
	# def get_same_periodicity_type_habits(self):
	# 	try:
	# 		with self._db._connection.cursor() as cursor:
	# 			query = "SELECT habit_periodicity_type, COUNT(*) AS habit_count, JSON_ARRAYAGG(JSON_OBJECT('habit_id', habit_id, 'habit_name', habit_name)) AS habit_list FROM habits GROUP BY habit_periodicity_type ORDER BY habit_count DESC;"

	# 			cursor.execute(query)
	# 			result = cursor.fetchall()

	# 			if result:
	# 				return result
	# 			else:
	# 				raise AnalyticsNotFoundError(f"Analytics is not found.")
			
	# 	except Exception as error: #rolback for unexpected errors
	# 		self._db._connection.rollback()
	# 		raise