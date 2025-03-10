# from apps.notifications.domain.notification_strategy import NotificationStrategy
from apps.goals.domain.goal_subject import GoalSubject
from apps.progresses.domain.progress_dto import ProgressHistoryDTO
from apps.notifications.domain.daily_notification import DailyNotificationStrategy
from apps.notifications.domain.weekly_notification import WeeklyNotificationStrategy

class NotificationObserver:
	def __init__(self, notification_stragety: str): #notification_service
		self._notification_stragety = notification_stragety

	def update(self, progress_data: dict): #shouldnt we just pass around data instead of this object? too heavy
		"""
		Depending on the chosen strategy, we send a message
			goal_subject (Goalsubject): The goal object containing the updated values.
		"""
		# goal_id = progress_data['goal_id']
		strategy_mapping = {
			"daily": DailyNotificationStrategy,
			"weekly": WeeklyNotificationStrategy
		}
		#does this get the updated kvi or since its updating in sync, its still the old one before update?
		progress_dto = ProgressHistoryDTO(
				progress_data['last_occurence'], 
				progress_data['target_kvi'] - progress_data['current_kvi'],
				progress_data['streak'],
			)

		strategy = strategy_mapping[self._notification_stragety]() #this will return DailyNotificationStrategy
		# deadline_msg = strategy.before_deadline_message(progress_data=progress_dto)
		completion_msg = strategy.on_completion_message(progress_data=progress_dto)
		failure_msg = strategy.on_expired_message(progress_data=progress_dto)

		print(completion_msg, failure_msg)
		# ProgressHistoryDTO()
		# #should we handle this via the service? No validation logic is applied here.
		# self._notification_stragety()
