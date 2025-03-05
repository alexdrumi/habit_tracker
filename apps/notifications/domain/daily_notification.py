from apps.notifications.domain.notification_strategy import NotificationStrategy
from apps.goals.domain.goal_subject import GoalSubject
from apps.progresses.domain.progress_dto import ProgressHistoryDTO
from datetime import datetime, timedelta

"""
+-------------+-------------------+----------------------+----------------------------+------------+------------------------------+
| progress_id | current_kvi_value | progress_description | occurence_date             | goal_id_id | distance_from_goal_kvi_value |
+-------------+-------------------+----------------------+----------------------------+------------+------------------------------+
|           1 |                 8 | NULL                 | 2025-02-19 00:00:00.000000 |         13 |                           -7 |
"""


class DailyNotificationStrategy(NotificationStrategy):
	def before_deadline_message(self, progress_data: ProgressHistoryDTO):
		now = datetime.now()
		last_updated_time = progress_data.to_dict().get('_last_updated_time')


		if last_updated_time == None:
			return "NO MESSAGE HERE"
		#can we make a string from the passed dt last occurence?
		dto_to_dict = progress_data.to_dict()
		dict_keys = dto_to_dict.keys()
		last_updated_time = dto_to_dict.get('_last_updated_time')
		time_difference = now - last_updated_time
		# print(f"{last_updated_time} is the last time this was updated, now is {now}, {type(last_updated_time)}, {type(now)}")
		print(f"{now - last_updated_time} is the diff between now and last uipdated")
		if time_difference < timedelta(hours=24): #this has to be eventually 4 hours before the actual deadline
			return "ITS PERFECTLY IN TIME"
		# return None
		return "BEFORE DEADLINE MESSAGE"

	def on_completion_message(self, progress_data: ProgressHistoryDTO):
		# if progress_data._distance_from_goal == 0:
		# 	return "CONGRATS, YOU COMPLETED THIS!"
		# return None
		return "ON COMPLETION MESSAGE"

	def on_failure_message(self, progress_data: ProgressHistoryDTO):
		now = datetime.now()

		# if progress_data._last_updated_time  > now:
		# 	return "Lazy fella, y u dont work?"
		# return None
		return "ON FAILURE MESSAGE"