from typing import TYPE_CHECKING

if TYPE_CHECKING:
	from apps.core.facades.habit_tracker_facade_impl import HabitTrackerFacadeImpl

class HabitOrchestrator:
	"""Handles multi-step workflows if facade deems that necessary."""

	def __init__(self, habit_tracker_facade: "HabitTrackerFacadeImpl"): #fix circular dependency
		self._habit_facade = habit_tracker_facade


	#in case we need chained services, we do that from here. For now we keep the create habit in the service also doing validation. 
	#at this point we dont know how much orchestration is needed, in the future probably this will be extended.
	#Facade can keep interacting with single services, and in case its chainedm, we call orchestrator.
	#(orchestrator will still call single facade services but with input check, chained logic BUT NO CIRCULAR DEPENDENCY
	def create_a_habit_with_validation(self, habit_name, habit_action, habit_periodicity_type, user_id):
		
		# if not isinstance(user_id, int) or user_id < 0:
		# 	raise ValueError("Invalid user ID. It must be a positive integer. See list (option 3) for users for available user IDs.")
		# if not habit_name.strip():
		# 	raise ValueError("Habit name cannot be empty.")
		# if not habit_action.strip():
		# 	raise ValueError("Habit action cannot be empty.")
	
		#validate user
		validated_user_id = self._habit_facade._user_service.validate_user_by_id(user_id)
		#check if habit already exist for that user
		existing_habit = self._habit_facade._habit_service.get_habit_id(user_id=validated_user_id, habit_name=habit_name)
# 
		if existing_habit:
			return existing_habit
		
		#create the habit with using essentially one of the methods of the facade
		new_habit = self._habit_facade.create_a_habit(habit_name=habit_name, habit_action=habit_action, habit_periodicity_type=habit_periodicity_type, habit_user_id=user_id)
		return new_habit

	def complete_a_habit(self, habit_id, goal_id):
		#we check whether habit exists
		validated_habit_id = self._habit_facade.validate_a_habit(habit_id=habit_id)

		#check whether the goal exists
		validated_goal_id = self._habit_facade.validate_a_goal(goal_id=goal_id)

		#select one goal id which we will want to tick

		#we will update the goals current kvi val with current += 1

		#get current kvi value of the goal?
		current_kvi_value = self._habit_facade.get_current_kvi(goal_id=goal_id)
		print(current_kvi_value)
		print(f"{type(current_kvi_value)}")
		new_kvi_value = float(current_kvi_value) + 1.0
		# print
		self._habit_facade.update_goal_current_kvi_value(goal_id=validated_goal_id, current_kvi_value=new_kvi_value)
		print(f"{self._habit_facade.get_current_kvi(goal_id=goal_id)}")


		#this is essentially a completed habit for 'a certain interval' 
		#thus we will have to restart the last completed part

		#for that we will also need a progresses blueprint everytime we call this
