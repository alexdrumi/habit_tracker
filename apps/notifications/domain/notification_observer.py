from apps.notifications.domain.notification_strategy import NotificationStrategy
from apps.goals.domain.goal_subject import GoalSubject
from apps.progresses.domain.progress_dto import ProgressHistoryDTO
from apps.notifications.domain.daily_notification import DailyNotificationStrategy

class NotificationObserver:
	def __init__(self, notification_stragety: str): #notification_service
		self._notification_stragety = notification_stragety


# class DailyNotificationStrategy(NotificationStrategy):
# 	def before_deadline_message(self, progress_data: ProgressHistoryDTO):
# 		now = datetime.now()


# 		print(now)
# 		if progress_data._last_updated_time < now:
# 			return "WHATEVER, JUST TRYING THIS OUT HERE"
	
# 	def on_completion_message(self, progress_data: ProgressHistoryDTO):
# 		if progress_data._distance_from_goal == 0:
# 			return "CONGRATS, YOU COMPLETED THIS!"

	
# 	def on_failure_message(self, progress_data: ProgressHistoryDTO):
# 		now = datetime.now()

# 		if progress_data._last_updated_time  > now:
# 			return "Lazy fella, y u dont work?"


	def update(self, progress_data: dict): #shouldnt we just pass around data instead of this object? too heavy
		"""
		Should be updated when the goals current kvi value changes.
		Creates a progress entry in the database.

		Args:
			goal_subject (Goalsubject): The goal object containing the updated values.
		"""
		goal_id = progress_data['goal_id']
		current_val = progress_data['current_kvi']
		target_val = progress_data['target_kvi']

		distance_from_goal = target_val - current_val

		strategy_mapping = {
			"DAILY": DailyNotificationStrategy
		}

		progress_dto = ProgressHistoryDTO(
			progress_data['occurence_data'][-1], 
			2,
			progress_data['target_kvi'] - progress_data['current_kvi']
			)

		strategy = strategy_mapping[self._notification_stragety]() #this will return DailyNotificationStrategy
		deadline_msg = strategy.before_deadline_message(progress_data=progress_dto)
		completion_msg = strategy.on_completion_message(progress_data=progress_dto)
		failure_msg = strategy.on_failure_message(progress_data=progress_dto)

		print(deadline_msg, completion_msg, failure_msg)
		
		# ProgressHistoryDTO()
		# #should we handle this via the service? No validation logic is applied here.
		# self._notification_stragety()
