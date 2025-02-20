from apps.goals.repositories.goal_repository import GoalRepository
from apps.goals.services.goal_service import GoalService

#errors?

#when we build this object in a factory pattern, we will attach the observer and notification to it
class GoalSubject:
	def __init__(self, goal_service: GoalService, goal_data: dict):
		"""
		goal_data dict: eg. {'goal_id':3, 'target_kvi_value':7.0, 'current_kvi_value':2.0, maybe habit_id_id ?}
		goal_repo: an instance of GoalRepository so we can call raw sql to persist changes
		"""
		self._goal_service = goal_service
		self._goal_data = goal_data
		self._observers = [] #mostly progresses and notification observer for now but later can be many others assigned here
	
	def attach(self, observer):
		self._observers.append(observer)
	
	def notify(self):
		for observer in self._observers: #will trigger all observers (notification, progress observer for blueprint)
			observer.update(progress_data=self._goal_data)#this will be a notification method,forgot to specify goal_subject=self, before...
	
	def increment_kvi(self, increment=1.0):
		target_kvi_value = self._goal_data['target_kvi']
		new_kvi_value = float(self._goal_data['current_kvi']) + increment
		
		
		#update goalfield PROBABLY BETTER IF ITS VIA THE SERVICE FOR INPUT CHECK?????????
		self._goal_service.update_a_goal(goal_id=self._goal_data['goal_id'], current_kvi_value=new_kvi_value)

		self._goal_data['current_kvi'] = new_kvi_value
		self._goal_data[self._goal_data['target_kvi']] = target_kvi_value - new_kvi_value

		#notify other observerrs?
		self.notify() #creates a progress blueprint, notifies user