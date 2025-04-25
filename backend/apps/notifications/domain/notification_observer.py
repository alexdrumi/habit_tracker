# from apps.notifications.domain.notification_strategy import NotificationStrategy
from apps.goals.domain.goal_subject import GoalSubject
from apps.progresses.domain.progress_dto import ProgressHistoryDTO
from apps.notifications.domain.daily_notification import DailyNotificationStrategy
from apps.notifications.domain.weekly_notification import WeeklyNotificationStrategy
import click

class NotificationObserver:
	"""
	An observer class responsible for triggering notifications when a habit's 
	progress is updated. Based on the notification strategy (daily or weekly), 
	it generates relevant messages.
	"""
	def __init__(self, notification_stragety: str): #notification_service
		self._notification_stragety = notification_stragety



	def update(self, progress_data: dict): #shouldnt we just pass around data instead of this object? too heavy
		"""
		Sends out notifications based on the updated progress data and the 
		chosen notification strategy.

		Args:
			progress_data (dict): A dictionary containing progress information, 
				including the last occurrence date, target KVI, current KVI,
				and current streak.
		"""
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

		#some messages, will extend this in the future
		completion_msg = strategy.on_completion_message(progress_data=progress_dto)
		failure_msg = strategy.on_expired_message(progress_data=progress_dto)

		if completion_msg:
			click.echo(click.style(f"{completion_msg}", fg="green", bold=True))
		if failure_msg:
			click.echo(click.style(f"{failure_msg}", fg="red", bold=True))
