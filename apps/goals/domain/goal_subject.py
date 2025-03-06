from apps.goals.repositories.goal_repository import GoalRepository
from apps.goals.services.goal_service import GoalService
from apps.progresses.services.progress_service import ProgressesService
from datetime import datetime, timedelta
#errors?

#when we build this object in a factory pattern, we will attach the observer and notification to it
class GoalSubject:
	def __init__(self, goal_service: GoalService, progress_service: ProgressesService, goal_data: dict):
		"""
		goal_data dict: eg. {'goal_id':3, 'target_kvi_value':7.0, 'current_kvi_value':2.0, maybe habit_id_id ?}
		goal_repo: an instance of GoalRepository so we can call raw sql to persist changes
		"""
		self._goal_service = goal_service
		self._progress_service = progress_service

		self._goal_data = goal_data
		self._observers = [] #mostly progresses and notification observer for now but later can be many others assigned here
	



	def attach(self, observer):
		self._observers.append(observer)



	def notify(self):
		for observer in self._observers: #will trigger all observers (notification, progress observer for blueprint)
			observer.update(progress_data=self._goal_data)#this will be a notification method,forgot to specify goal_subject=self, before...
	

	def is_too_early(self):
		periodicity = 1.0 if self._goal_data['target_kvi'] == 1.0 else 7.0
		last_progress = self._goal_data.get('last_occurence')
		if last_progress is None:
			return False #if never ticked, cant expire
		
		#WE WOULD HAVE TO ALTER THE TIMEDELTA IF ITS WEEKS, TO CHECK WHETHER THE WEEK IS THIS YEAR?
		now = datetime.now()
		time_delta_difference = timedelta(hours=24) if periodicity == 1.0 else timedelta(weeks=1)
		time_difference = now - last_progress
		#time_difference > time_delta_difference and time_difference < time_delta_difference * 2
		absolute_time_difference = abs(time_difference.total_seconds())
		
		# print(f"{time_delta_difference} is timedeltadiff, {time_difference} is timediff. result: {time_difference > time_delta_difference}")
		# return (absolute_time_difference > time_delta_difference.total_seconds())
		#before and after?
		return (absolute_time_difference < time_delta_difference.total_seconds())

	def is_expired(self):
		periodicity = 1.0 if self._goal_data['target_kvi'] == 1.0 else 7.0
		last_progress = self._goal_data.get('last_occurence')
		if last_progress is None:
			return False #if never ticked, cant expire
		
		#WE WOULD HAVE TO ALTER THE TIMEDELTA IF ITS WEEKS, TO CHECK WHETHER THE WEEK IS THIS YEAR?
		now = datetime.now()
		time_delta_difference = timedelta(hours=48) if periodicity == 1.0 else timedelta(weeks=2)
		time_difference = now - last_progress
		#time_difference > time_delta_difference and time_difference < time_delta_difference * 2
		absolute_time_difference = abs(time_difference.total_seconds())
		
		return (absolute_time_difference > time_delta_difference.total_seconds())


	def reset_progress(self):
		self._goal_data['streak'] = 0
		self._goal_data['current_kvi'] = 0.0
		self._goal_service.update_a_goal(goal_id=int(self._goal_data['goal_id']), current_kvi_value=0.0)
		self.notify() #?maybe



	def increment_kvi(self, increment):
		last_progress = self._progress_service.get_last_progress_entry(goal_id=self._goal_data['goal_id'])
		self._goal_data['last_occurence'] = last_progress[3] if last_progress else None

		target_kvi_value = self._goal_data['target_kvi']
		new_kvi_value = float(self._goal_data['current_kvi']) + increment
		#new_streak = self._goal_data['streak'] + 1
		#we also have to update the streak of the related habit
		
		#update goalfield PROBABLY BETTER IF ITS VIA THE SERVICE FOR INPUT CHECK?????????
		self._goal_service.update_a_goal(goal_id=self._goal_data['goal_id'], current_kvi_value=new_kvi_value)

		self._goal_data['current_kvi'] = new_kvi_value
		self._goal_data[self._goal_data['target_kvi']] = target_kvi_value - new_kvi_value

		# occurence_date = self._progress_service.get_progress(self._goal_data['goal_id'])
		# print(f'{occurence_date} IS THE OCCURENCE DATE )progress entity inside the increment kvi')
		# print(f"{self._goal_data['goal_id']} are self._goal_data['goal_id']\n\n")
		last_progress = self._progress_service.get_last_progress_entry(goal_id=self._goal_data['goal_id'])
		self._goal_data['last_occurence'] = last_progress[3] if last_progress else None

		# if last_progress == None:
		# 	self._goal_data['last_occurence'] = None
		# else:
		# 	self._goal_data['last_occurence'] = last_progress[3] #can be None
		# print(f"{self._goal_data['last_occurence']} is the goal last occurence now")

		#depending on daily or weekly tick, we check when was the last occurence. if it was already ticked for today or the week, no increment is needed.

		
		self.notify() #creates a progress blueprint, notifies user
		print(f"Habit ticked successfully!")