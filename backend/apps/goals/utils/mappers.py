
from apps.goals.schemas import GoalsAndRelatedHabits, HabitSummary, GoalsRead
#{'goal_id': 2, 'habit_id': 2, 'target_kvi_value': 7.0, 'current_kvi_value': 0.0, 'goal_name': 'making ice tea every day', 'occurence_date': None},


def map_to_goals_and_habits_read_schema(goal_info: dict) -> GoalsAndRelatedHabits:
	if goal_info is None or len(goal_info) == 0:
		return

	habit_id = goal_info.get('habit_id') or goal_info.get('habit_id_id')
	habit_name=goal_info.get('habit_name') or "unknown"
	
	if habit_id is None:
		raise ValueError("Missing both habit_id and habit_id_id in goal_info")
	
	read_schema = GoalsAndRelatedHabits(
        goal_name = str(goal_info['goal_name']),
        goal_id=int(goal_info['goal_id']),
        related_habit=HabitSummary(
			habit_id=int(habit_id),
			habit_name=habit_name
		)
	)
	return read_schema

