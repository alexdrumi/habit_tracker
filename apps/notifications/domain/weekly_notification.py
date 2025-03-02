from apps.notifications.domain.notification_strategy import NotificationStrategy
from apps.goals.domain.goal_subject import GoalSubject
from apps.progresses.domain.progress_dto import ProgressHistoryDTO
from datetime import datetime, timedelta

class WeeklyNotificationStrategy(NotificationStrategy):
	def before_deadline_message(self, progress_data: ProgressHistoryDTO):
		now = datetime.now()

		print(now)
		if progress_data._last_updated_time == None:
			return "NO MESSAGE HERE"
		dto_to_dict = progress_data.to_dict()
		dict_keys = dto_to_dict.keys()
		last_updated_time = dto_to_dict.get('_last_updated_time')
		time_difference = now - last_updated_time
		if time_difference < timedelta(weeks=1):
			return f"You have {timedelta(weeks=1) - time_difference} left!"
		return None
	
	def on_completion_message(self, progress_data: ProgressHistoryDTO):
		now = datetime.now()

		if progress_data._last_updated_time == None:
			return "NO MESSAGE HERE"
		
		#if the last updated time was not yet a week ago, we refuse to get it completed
		dto_to_dict = progress_data.to_dict()
		dict_keys = dto_to_dict.keys()
		last_updated_time = dto_to_dict.get('_last_updated_time')
		time_difference = now - last_updated_time
		if progress_data._distance_from_goal == 0:
			return f"CONGRATS, you completed this {dto_to_dict._total_completed_times} amount of times."
		return None


	def on_failure_message(self, progress_data: ProgressHistoryDTO):
		now = datetime.now()

		if progress_data._last_updated_time == None:
			return "NO MESSAGE HERE"
		if progress_data._last_updated_time > now:
			return "y tho"
		return None