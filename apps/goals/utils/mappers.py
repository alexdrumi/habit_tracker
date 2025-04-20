
from apps.goals.schemas import GoalsAndRelatedHabits, HabitSummary, GoalsRead
#{'goal_id': 2, 'habit_id': 2, 'target_kvi_value': 7.0, 'current_kvi_value': 0.0, 'goal_name': 'making ice tea every day', 'occurence_date': None},


def map_to_goals_and_habits_read_schema(goal_info: dict) -> GoalsAndRelatedHabits:
	if goal_info is None or len(goal_info) == 0:
		return

	read_schema = GoalsAndRelatedHabits(
        goal_name = str(goal_info['goal_name']),
        goal_id=int(goal_info['goal_id']),
        related_habit=HabitSummary(
			habit_id_id=int(goal_info['habit_id_id'])
        )
	)
	return read_schema

