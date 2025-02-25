from apps.notifications.domain.notification_strategy import NotificationStrategy
from apps.goals.domain.goal_subject import GoalSubject
from apps.progresses.domain.progress_dto import ProgressHistoryDTO
from datetime import datetime

class WeeklyNotificationStrategy(NotificationStrategy):
	def before_deadline_message(self, progress_data: ProgressHistoryDTO):
		now = datetime.now()

		print(now)
		if progress_data._last_updated_time < now:
			return "WHATEVER JUST DO SMTH FOR NBW"
		return None
	
	def on_completion_message(self, progres_data: ProgressHistoryDTO):
		if progres_data._distance_from_goal == 0:
			return "CONGRATS, YOU COMPLETED THIS"
		return None
	
	def on_failure_message(self, progress_data: ProgressHistoryDTO):
		now = datetime.now()

		if progress_data._last_updated_time > now:
			return "y tho"
		return None