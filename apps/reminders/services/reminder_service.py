from datetime import datetime, timedelta
from apps.goals.services.goal_service import GoalService
from mysql.connector.errors import IntegrityError
import logging

def handle_reminder_service_exceptions(f):
	def wrapper(*args, **kwargs):
		try:
			return f(*args, **kwargs)
		except IntegrityError as ierror:
			logging.error(f"ReminderService error in {f.__name__}: {ierror}")
			raise ierror
		except Exception as error:
			logging.error(f"Unexpected error in {f.__name__}: {error}")
			raise error
	return wrapper

  
  
class ReminderService:
	def __init__(self, goal_service: GoalService):
		self._goal_service = goal_service
	


	@handle_reminder_service_exceptions
	def calculate_tickability(self, last_occurence_datetime, current_time, time_delta_difference):
		"""
		Determines whether a habit/goal is currently 'tickable', if 
		it is within the valid window to record progress.

		Args:
			last_occurence_datetime (datetime): The datetime of the last occurrence or progress.
			current_time (datetime): The current system time.
			time_delta_difference (timedelta): The standard interval (daily or weekly) for completion.

		Returns:
			bool: True if it is currently acceptable to record progress, False otherwise.
		"""
		time_between_last_occurrence_and_now = current_time - last_occurence_datetime
		absolute_time_difference = abs(time_between_last_occurrence_and_now.total_seconds())
		is_too_early = (absolute_time_difference < time_delta_difference.total_seconds())
		is_too_late = (absolute_time_difference > time_delta_difference.total_seconds() * 2)
 
		return not (is_too_early or is_too_late)
		


	@handle_reminder_service_exceptions
	def is_tickable(self, daily_or_weekly, last_occurence):
		"""
		Determines if the given goal (daily or weekly) can be ticked now 
		based on the last recorded occurrence.

		Args:
			daily_or_weekly (int): An integer signifying daily (1) or weekly (7).
			last_occurence (dict): A dictionary containing the last occurrence info 
				for the goal, including 'occurence_date'.

		Returns:
			bool: True if the goal can be ticked, otherwise False.
		"""
		if len(last_occurence) == 0: #if it was never ticked, its tickable, time to track it
			return True
		
		current_time = datetime.now()
		last_occurence_datetime = last_occurence['occurence_date']
		td = timedelta(hours=24) if daily_or_weekly == 1 else timedelta(weeks=1)
		return self.calculate_tickability(last_occurence_datetime, current_time, td)



	@handle_reminder_service_exceptions
	def get_pending_goals(self):
		"""
		Retrieves all goals from the GoalService, checks whether each goal 
		is 'tickable', and prints reminders for those that are pending.

		Raises:
			Exception: For any unexpected errors during the reminder process.
		"""
		#get all goals via goal service
		all_goals = self._goal_service.query_all_goals()
		goals_which_need_reminders = []
		#go through all goals
		for goal in all_goals:
			last_occurence = self._goal_service.get_last_progress_entry_associated_with_goal_id(goal['goal_id'])
			daily_or_weekly = 1 if goal	['target_kvi_value'] == 1.0 else 7
			is_tickable = self.is_tickable(daily_or_weekly, last_occurence)

			if is_tickable == False:
				continue

			#if is_tickable is not None:
			goals_which_need_reminders.append({
				'goal_id': goal['goal_id'],
				'goal_name': goal['goal_name'],
				'habit_id': goal['habit_id'],
				'print_message': is_tickable
				})
		self.print_reminders(goals_which_need_reminders)



	@handle_reminder_service_exceptions
	def print_reminders(self, goals_which_need_reminders):
		"""
		Prints a list of goals for which the user should be reminded to 
		update progress. Highlights them for visibility in the console.

		Args:
			goals_which_need_reminders (list): A list of dictionaries containing 
				details about each goal that needs a reminder.
		"""
		if not goals_which_need_reminders:
			print("\033[92mNo pending goals to complete!\033[0m")
			return

		print("\033[91mGOALS THAT NEED TO BE TICKED\033[0m")
		for goal in goals_which_need_reminders:
			if goal['print_message'] == None:
				goal['print_message'] = "Habit was never ticked, you are free to tick it for the first time!"
			print(f"\033[91m- Goal name: {goal['goal_name']}, Goal ID: {goal['goal_id']}, Habit ID: {goal['habit_id']}\033[0m")  # Red text
 