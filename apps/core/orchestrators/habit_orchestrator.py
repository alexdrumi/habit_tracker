from typing import TYPE_CHECKING
from datetime import datetime, timedelta

if TYPE_CHECKING:
	from apps.core.facades.habit_tracker_facade_impl import HabitTrackerFacadeImpl

from apps.goals.domain.goal_subject import GoalSubject
from apps.goals.domain.goal_factory import build_goal_subject

class HabitOrchestrator:
	"""Handles multi-step workflows if facade deems that necessary."""

	def __init__(self, habit_tracker_facade: "HabitTrackerFacadeImpl"): #fix circular dependency
		self._habit_facade = habit_tracker_facade

	#in case we need chained services, we do that from here. For now we keep the create habit in the service also doing validation. 
	#at this point we dont know how much orchestration is needed, in the future probably this will be extended.
	#Facade can keep interacting with single services, and in case its chainedm, we call orchestrator.
	#(orchestrator will still call single facade services but with input check, chained logic BUT NO CIRCULAR DEPENDENCY
	def create_a_habit_with_validation(self, habit_name, habit_action, habit_periodicity_type, user_id):
		#validate user
		validated_user_id = self._habit_facade._user_service.validate_user_by_id(int(user_id))
		#check if habit already exist for that user
		# existing_habit = self._habit_facade._habit_service.get_habit_id(user_id=int(validated_user_id), habit_name=habit_name)
# 
		# if existing_habit:
		# 	return existing_habit
		
		#create the habit with using essentially one of the methods of the facade. shall we just go through again the service instead of the facade?
		new_habit = self._habit_facade.create_a_habit(habit_name=habit_name, habit_action=habit_action, habit_periodicity_type=habit_periodicity_type, habit_user_id=user_id)
		return new_habit


	def complete_a_habit(self, habit_id, goal_id):
		#we check whether habit exists
		validated_habit_id = self._habit_facade.validate_a_habit(habit_id=habit_id)

		#check whether the goal exists
		validated_goal_id = self._habit_facade.validate_a_goal(goal_id=goal_id)

		#get the periodicity type for notification observer
		habit_periodicity_type = self._habit_facade.get_habit_strategy(validated_habit_id)

		#build the subject (this wil be the subject of any kind of observers)
		goal_subject = build_goal_subject(
			habit_id=validated_habit_id,
			goal_id=validated_goal_id,
			habit_periodicity_type = habit_periodicity_type,
			goal_service=self._habit_facade._goal_service,
			progress_service=self._habit_facade._progress_service
			)
		increment_amount = 1.0 if habit_periodicity_type == 'daily' else 7.0
		goal_subject.increment_kvi(increment=increment_amount) #this adds the usual +1 but we can change it later for custom kvi


	def fetch_ready_to_tick_goals_of_habits(self):
		#some validaiton here maybe		
		#now call either a service via the habit facade goal service which filters this available goals data
		#or call straight a service->repo which just gives back a filtered data.
		all_goals = self._habit_facade._goal_service.query_all_goals()

		all_goals_with_date = {}
		for goal in all_goals:
			#dict key will be goal id
			all_goals_with_date[goal["goal_id"]] = goal
			#get last progress associated with that goal_id
			last_entry = self._habit_facade._goal_service.get_last_progress_entry_associated_with_goal_id(goal_id=int(goal['goal_id']))
			
			#assign the occurence date is there was one, otherwise 0
			if len(last_entry) != 0:
				all_goals_with_date[goal["goal_id"]]["occurence_date"] = last_entry["occurence_date"]
			else:
				all_goals_with_date[goal["goal_id"]]["occurence_date"] = None

		now = datetime.now()
		current_week = now.isocalendar()[1]
		current_year = now.year
		tickable_goals_and_habits = []

		for k, v in all_goals_with_date.items():
			last_tick = v['occurence_date']
			target_kvi = v['target_kvi_value']

			if last_tick is None:
				print('Tickable, thus we can return goal and habit id.')
				tickable_goals_and_habits.append(v)
				continue 

			time_since_last_tick = now - last_tick
			last_tick_week = last_tick.isocalendar()[1] #week nr of last tick's week
			last_tick_year = last_tick.year #hypothetically, which year..
			if target_kvi == 1:
				if (now.date() - timedelta(days=2)) <= last_tick.date() and last_tick.date() < (now.date() - timedelta(days=1)):
					print(f'Goal {k} is a daily goal and was last ticked {time_since_last_tick.days} days ago, tickable')
					tickable_goals_and_habits.append(v)
				else:
					print(f'Goal {k} is not tickable')
			
			elif target_kvi == 7:
				if (last_tick_year < current_year) or (last_tick_week < current_week - 1):
					print(f'Goal {k} was last ticked more than 2 weeks ago, not tickable anymore.')
				elif last_tick_week <  current_week: #wouldnt this case it to be tickable every day?
					print(f'Goal is ticked last week thus, its tickable now!')
					tickable_goals_and_habits.append(v)
				else:
					print(f'Goal {k} was ticked this week, not yet tickable')

		return tickable_goals_and_habits




	# def complete_a_habit(self, habit_id, goal_id):
	# 	#we check whether habit exists
	# 	validated_habit_id = self._habit_facade.validate_a_habit(habit_id=habit_id)

	# 	#check whether the goal exists
	# 	validated_goal_id = self._habit_facade.validate_a_goal(goal_id=goal_id)

	# 	#select the goal whos target kvi we want to update
	# 	goal_entity = self._habit_facade.get_goal_entity_by_id(validated_goal_id, validated_habit_id)
	# 	current_kvi_value = goal_entity['current_kvi']
	# 	target_kvi_value = goal_entity['target_kvi']
	# 	print(f"{goal_entity} is the goal entity\n\n\n")
	# 	# [(1, 3, 8.0, 6.0)] is the goal entit
	# 	#goalid, habitid, targetkvi, currentkvi
	# 	new_kvi_value = float(current_kvi_value) + 1.0
	# 	self._habit_facade.update_goal_current_kvi_value(goal_id=validated_goal_id, current_kvi_value=new_kvi_value)

	# 	#create the blueprint with the updated values
	# 	distance_from_goal_kvi_value = target_kvi_value - new_kvi_value
	# 	progress_entity = self._habit_facade.create_a_progress(validated_goal_id, current_kvi_value=new_kvi_value, distance_from_kvi_value=distance_from_goal_kvi_value, progress_description=None)
		
	# 	# print(f"{progress_entity} is the progress entity")
	# 	#we could return the updated progress if needed with the values fso one could see where are we in the progress
	# 	#or we just leave that to the analytics