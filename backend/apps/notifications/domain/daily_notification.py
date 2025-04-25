from apps.notifications.domain.notification_strategy import NotificationStrategy
from apps.goals.domain.goal_subject import GoalSubject
from apps.progresses.domain.progress_dto import ProgressHistoryDTO
from datetime import datetime, timedelta

class DailyNotificationStrategy(NotificationStrategy):
	"""
	A concrete notification strategy for daily habits. This strategy
	defines how to generate messages when a user completes or fails to
	complete a daily habit on time.
	"""
	def on_completion_message(self, progress_data: ProgressHistoryDTO):
		"""
		Generates a congratulatory message upon successful daily habit completion.

		Args:
			progress_data (ProgressHistoryDTO): Contains information about the current streak,
				distance from the target, and the last occurrence time.

		Returns:
			str or None: A congratulations message if the streak is non-zero. Otherwise None.
		"""
		# if progress_data._distance_from_goal == 0:
		streak = progress_data.to_dict().get('streak')
		if streak != 0:
			return f"Congratulations, you have completed a daily habit with, your current streak is {streak}"



	def on_expired_message(self, progress_data: ProgressHistoryDTO):
		"""
		Generates a reminder message if the user missed a daily habit completion deadline.

		Args:
			progress_data (ProgressHistoryDTO): Contains information about the current streak,
				distance from the target, and the last occurrence time.

		Returns:
			str or None: A message indicating that the habit streak has been reset. Otherwise None.
		"""
		streak = progress_data.to_dict().get('streak')
		if streak == 0:
			return f"You have missed the previous deadline, you have to start to tick your habit again."
