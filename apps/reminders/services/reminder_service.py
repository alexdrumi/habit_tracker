from datetime import datetime, timedelta
from apps.goals.services.goal_service import GoalService

class ReminderService:
	def __init__(self, goal_service: GoalService):
		self._goal_service = goal_service
	
	
	def calculate_tickability(self, last_occurence_datetime, current_time, time_delta_difference):
		time_between_last_occurrence_and_now = current_time - last_occurence_datetime
		absolute_time_difference = abs(time_between_last_occurrence_and_now.total_seconds())
		is_too_early = (absolute_time_difference < time_delta_difference.total_seconds())
		is_too_late = (absolute_time_difference > time_delta_difference.total_seconds() * 2)

		return (not (is_too_early or is_too_late))
		



	def is_tickable(self, daily_or_weekly, last_occurence):
		if len(last_occurence) == 0: #if it was never ticked, its tickable, time to track it
			return True
		
		current_time = datetime.now()
		last_occurence_datetime = last_occurence['occurence_date']
		td = timedelta(hours=24) if daily_or_weekly == 1 else timedelta(weeks=1)
		return self.calculate_tickability(last_occurence_datetime, current_time, td)



	def get_pending_goals(self):
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

		print("\033[91mGOALS THAT NEED TO BE TICKED\033[0m")
		for goal in goals_which_need_reminders:
			if goal['print_message'] == None:
				goal['print_message'] = "Habit was never ticked, you are free to tick it for the first time!"
			print(f"\033[91m- Goal name: {goal['goal_name']}, Goal ID: {goal['goal_id']}, Habit ID: {goal['habit_id']}\033[0m")  # Red text
 