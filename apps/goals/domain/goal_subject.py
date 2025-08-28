from apps.goals.repositories.goal_repository import GoalRepository
from apps.goals.services.goal_service import GoalService
from apps.progresses.services.progress_service import ProgressesService
from datetime import datetime, timedelta

class GoalSubject:
	def __init__(self, goal_service: GoalService, progress_service: ProgressesService, goal_data: dict):
		"""
		goal_data dict: eg. {'goal_id':3, 'target_kvi_value':7.0, 'current_kvi_value':2.0, maybe habit_id_id ?}
		goal_repo: an instance of GoalRepository so we can call raw sql to persist changes
		"""
		self._goal_service = goal_service
		self._progress_service = progress_service

		self._goal_data = goal_data
		self._observers = []
	



	def attach(self, observer):
		self._observers.append(observer)



	def notify(self):
		for observer in self._observers:
			observer.update(progress_data=self._goal_data)

	def is_too_early(self):
		periodicity = 1.0 if self._goal_data['target_kvi'] == 1.0 else 7.0
		last_progress = self._goal_data.get('last_occurence')
		if last_progress is None:
			return False
		
		now = datetime.now()
		time_delta_difference = timedelta(hours=24) if periodicity == 1.0 else timedelta(weeks=1)
		time_difference = now - last_progress
		absolute_time_difference = abs(time_difference.total_seconds())
		
		return (absolute_time_difference < time_delta_difference.total_seconds())

	def is_expired(self):
		periodicity = 1.0 if self._goal_data['target_kvi'] == 1.0 else 7.0
		last_progress = self._goal_data.get('last_occurence')
		if last_progress is None:
			return False
		
		now = datetime.now()
		time_delta_difference = timedelta(hours=48) if periodicity == 1.0 else timedelta(weeks=2)
		time_difference = now - last_progress
		absolute_time_difference = abs(time_difference.total_seconds())
		
		return (absolute_time_difference > time_delta_difference.total_seconds())


	def reset_progress(self):
		self._goal_data['streak'] = 0
		self._goal_data['current_kvi'] = 0.0
		self._goal_service.update_a_goal(goal_id=int(self._goal_data['goal_id']), current_kvi_value=0.0)
		self.notify()



	def increment_kvi(self, increment):
		last_progress = self._progress_service.get_last_progress_entry(goal_id=self._goal_data['goal_id'])
		self._goal_data['last_occurence'] = last_progress[3] if last_progress else None

		target_kvi_value = self._goal_data['target_kvi']
		new_kvi_value = float(self._goal_data['current_kvi']) + increment

		self._goal_service.update_a_goal(goal_id=self._goal_data['goal_id'], current_kvi_value=new_kvi_value)
		self._goal_data['current_kvi'] = new_kvi_value
		self._goal_data[self._goal_data['target_kvi']] = target_kvi_value - new_kvi_value


		last_progress = self._progress_service.get_last_progress_entry(goal_id=self._goal_data['goal_id'])
		self._goal_data['last_occurence'] = last_progress[3] if last_progress else None

		self.notify()
		print(f"Habit ticked successfully!")