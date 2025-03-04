from datetime import datetime, timedelta
from apps.goals.services.goal_service import GoalService

class ReminderService:
	def __init__(self, goal_service: GoalService):
		self._goal_service = goal_service
	

	def calculate_time_between_last_occurence_and_now(self, last_occurence_datetime, current_time, deadline_timedelta_object):
		time_between_last_occurrence_and_now = current_time - last_occurence_datetime
		if time_between_last_occurrence_and_now < deadline_timedelta_object:
			return f"You have {deadline_timedelta_object - time_between_last_occurrence_and_now} to tick this habit/goal."
		return None



	def is_tickable(self, daily_or_weekly, last_occurence):
		if len(last_occurence) == 0:
			return None
		
		current_time = datetime.now()
		print(f'last occurence is {last_occurence['occurence_date']}')
		last_occurence_datetime = last_occurence['occurence_date'] #$print(last_occurence)	
		if daily_or_weekly == 1:
			return self.calculate_time_between_last_occurence_and_now(last_occurence_datetime, current_time, timedelta(hours=24))
		elif daily_or_weekly == 7:
			return self.calculate_time_between_last_occurence_and_now(last_occurence_datetime, current_time, timedelta(weeks=1))
		return None



	def get_pending_goals(self):
		#get all goals via goal service
		all_goals = self._goal_service.query_all_goals()

		goals_which_need_reminders = []
		#go through all goals
		for goal in all_goals:
			last_occurence = self._goal_service.get_last_progress_entry_associated_with_goal_id(goal['goal_id'])
			print(f'{last_occurence} of {goal['goal_id']}')
			
			daily_or_weekly = 1 if goal	['target_kvi_value'] == 1.0 else 7
			is_tickable = self.is_tickable(daily_or_weekly, last_occurence)
			# if is_tickable is not None:
			goals_which_need_reminders.append({
				'goal_id': goal['goal_id'],
				'goal_name': goal['goal_name'],
				'habit_id': goal['habit_id'],
				'print_message': is_tickable
				})
		self.print_reminders(goals_which_need_reminders)


	def print_reminders(self, goals_which_need_reminders):
		if not goals_which_need_reminders:
			print("\033[92mNo pending goals to complete!\033[0m")
			return

		print("\033[91m⏳ GOALS THAT NEED TO BE TICKED ⏳\033[0m")
		for goal in goals_which_need_reminders:
			if goal['print_message'] == None:
				goal['print_message'] = "Habit was never ticked, you are free to tick it for the first time!"
			print(f"\033[91m- Goal: {goal['goal_name']}, Habit ID: {goal['habit_id']}, {goal['print_message']}\033[0m")  # Red text
 