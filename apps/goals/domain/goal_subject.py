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
		self._observers = [] #mostly notification observer for now but later can be many others assigned here
	
	def attach(self, observer):
		self._observers.append(observer)
	
	def notify(self):
		for observer in self._observers: #will trigger all observers (notification, progress observer for blueprint)
			observer.update(goal_subject=self) #this will be a notification method
	
	def increment_kvi(self, increment=1.0):
		target_kvi_value = self._goal_data['target_kvi']
		new_kvi_value = float(self._goal_data['current_kvi']) + increment
		
		
		#update goalfield PROBABLY BETTER IF ITS VIA THE SERVICE FOR INPUT CHECK?????????
		self._goal_service.update_a_goal(goal_id=self._goal_data['goal_id'], current_kvi_value=new_kvi_value)

		self._goal_data['current_kvi'] = new_kvi_value
		self._goal_data[self._goal_data['target_kvi']] = target_kvi_value - new_kvi_value

		# #create the blueprint with the updated values
		# distance_from_goal_kvi_value = target_kvi_value - new_kvi_value
		# progress_entity = self._habit_facade.create_a_progress(validated_goal_id, current_kvi_value=new_kvi_value, distance_from_kvi_value=distance_from_goal_kvi_value, progress_description=None)
		
		#notify other observerrs?
		self.notify() #creates a progress blueprint