from datetime import datetime, timedelta

from apps.core.facades.habit_tracker_facade import HabitTrackerFacadeInterface
from apps.goals.domain.goal_subject import GoalSubject
from apps.goals.domain.goal_factory import build_goal_subject

import click

class HabitOrchestrator:
	"""Handles multi-step workflows if facade deems that necessary."""
	def __init__(self, habit_tracker_facade: HabitTrackerFacadeInterface):
		self._habit_facade = habit_tracker_facade



	def create_a_habit_with_validation(self, habit_name, habit_action, habit_periodicity_type, user_id):
		"""
		Creates a new habit after validating the associated user.

		Args:
			habit_name (str): Name of the habit.
			habit_action (str): Action or behavior for the habit.
			habit_periodicity_type (str): Periodicity (e.g., 'daily', 'weekly').
			user_id (int): ID of the user who will own this habit.

		Returns:
			dict: Newly created habit data, including habit ID and other details.
		"""
		validated_user_id = self._habit_facade.validate_user_by_id(int(user_id))
		new_habit = self._habit_facade.create_a_habit(habit_name=habit_name, habit_action=habit_action, habit_periodicity_type=habit_periodicity_type, habit_user_id=validated_user_id)
		return new_habit



	def complete_a_habit(self, habit_id, goal_id):
		"""
		Marks a habit as complete, updating streaks and progress.

		Validates that both habit and goal exist, then retrieves
		the habit’s periodicity type to determine how much to
		increment Key Value Indicators (KVI) and the streak.

		Args:
			habit_id (int): The habit’s ID.
			goal_id (int): The goal’s ID linked to the habit.

		Returns:
			None or Any: Returns early if it’s too early to tick
			the habit, otherwise executes completion logic. The
			actual return can be None or a custom result depending
			on the implementation.
		"""
		validated_habit_id = self._habit_facade.validate_a_habit(habit_id=int(habit_id))

		validated_goal_id = self._habit_facade.validate_a_goal(goal_id=int(goal_id))

		habit_periodicity_type = self._habit_facade.get_habit_strategy(validated_habit_id)[0]
		
		goal_subject = build_goal_subject(
			habit_id=validated_habit_id,
			goal_id=validated_goal_id,
			habit_periodicity_type = habit_periodicity_type,
			goal_service=self._habit_facade._goal_service,
			progress_service=self._habit_facade._progress_service
		)
		
		kvi_increment_amount = 1.0 if habit_periodicity_type == 'daily' else 7.0
		new_streak_amount = goal_subject._goal_data['streak'] + 1
		goal_subject._goal_data['streak'] = new_streak_amount
		last_progress = self._habit_facade.get_last_progress_entry(goal_id=goal_subject._goal_data['goal_id'])
		goal_subject._goal_data['last_occurence'] = last_progress[3] if last_progress else None

		if goal_subject.is_too_early() == True:
			now = datetime.now()
			difference = now - goal_subject._goal_data['last_occurence']
			if kvi_increment_amount == 1.0:
				waiting_time = timedelta(hours=24) - difference
			else:
				waiting_time = timedelta(hours=168) - difference
			click.echo(click.style(f"\nIt is too early to tick this habit. You need to wait {waiting_time} hours before you can tick it again.", fg="red", bold=True))
			return
		
		elif goal_subject.is_expired() == True:
			self._habit_facade.update_habit_streak(habit_id=validated_habit_id, updated_streak_value=0)
			goal_subject.reset_progress()

		else:
			self._habit_facade.update_habit_streak(habit_id=validated_habit_id, updated_streak_value=new_streak_amount)
			goal_subject.increment_kvi(increment=kvi_increment_amount)



	def fetch_ready_to_tick_goals_of_habits(self):
		"""
		Identifies which goals are ready to be incremented (ticked).

		Pulls all goals, checks their last progress occurrence date,
		and decides if they are tickable based on daily or weekly
		intervals.

		Returns:
			list: A list of goals (or combined habit-goal structures)
			that are eligible for increment based on their schedule.
		"""
		all_goals = self._habit_facade._goal_service.query_all_goals()

		all_goals_with_date = {}
		for goal in all_goals:
			all_goals_with_date[goal["goal_id"]] = goal
			last_entry = self._habit_facade.get_last_progress_entry_associated_with_goal_id(goal_id=int(goal['goal_id']))
			if len(last_entry) != 0:
				all_goals_with_date[goal["goal_id"]]["occurence_date"] = last_entry["occurence_date"]
			else:
				all_goals_with_date[goal["goal_id"]]["occurence_date"] = None

		now = datetime.now()
		tickable_goals_and_habits = []

		for k, v in all_goals_with_date.items():
			last_tick = v['occurence_date']
			target_kvi = v['target_kvi_value']

			if last_tick is None:
				tickable_goals_and_habits.append(v)
				continue 

			time_since_last_tick = now - last_tick
			
			if target_kvi == 1:
				if (timedelta(days=1) <= time_since_last_tick < timedelta(days=2)):
					tickable_goals_and_habits.append(v)
				else:
					pass
			
			elif target_kvi == 7:
				if timedelta(days=7) <= time_since_last_tick < timedelta(days=14):
					tickable_goals_and_habits.append(v)
				else:
					pass

		return tickable_goals_and_habits



	def delete_a_habit(self, habit_id):
		"""
		Deletes a habit record, preserving any associated progress.

		Validates the habit and retrieves its associated goal ID,
		then calls the facade to physically remove the habit while
		keeping progress records intact.

		Args:
			habit_id (int): The ID of the habit to delete.

		Returns:
			Any: Result of the delete operation.
		"""
		validated_habit_id = self._habit_facade.validate_a_habit(habit_id)
		goal_id = self._habit_facade.query_goal_of_a_habit(habit_id=validated_habit_id)

		deleted = self._habit_facade.delete_habit_physical_preserving_progress(habit_id=validated_habit_id, goal_id=int(goal_id[0]))
		return deleted


