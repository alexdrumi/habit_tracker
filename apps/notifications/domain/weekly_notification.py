from apps.notifications.domain.notification_strategy import NotificationStrategy
from apps.goals.domain.goal_subject import GoalSubject
from apps.progresses.domain.progress_dto import ProgressHistoryDTO
from datetime import datetime, timedelta

class WeeklyNotificationStrategy(NotificationStrategy):
	# def before_deadline_message(self, progress_data: ProgressHistoryDTO):
	# 	now = datetime.now()

	# 	print(now)
	# 	if progress_data.last_updated_time == None:
	# 		return "NO MESSAGE HERE"
	# 	dto_to_dict = progress_data.to_dict()
	# 	dict_keys = dto_to_dict.keys()
	# 	last_updated_time = dto_to_dict.get('last_updated_time')
	# 	time_difference = now - last_updated_time
	# 	if time_difference < timedelta(weeks=1):
	# 		return f"You have {timedelta(weeks=1) - time_difference} left!"
	# 	return None


	def on_completion_message(self, progress_data: ProgressHistoryDTO):
		# now = datetime.now()

		streak = progress_data.to_dict().get('streak')
		if streak != 0:
			return f"Congratulations, you have completed a daily habit with, your current streak is {streak}"

	def on_expired_message(self, progress_data: ProgressHistoryDTO):
		streak = progress_data.to_dict().get('streak')

		if streak == 0:
			return f"You have missed the previous deadline, you have to start to tick your habit again."
