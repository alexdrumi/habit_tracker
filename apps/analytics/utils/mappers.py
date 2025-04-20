from apps.habits.schemas import PeriodicityType, HabitAnalytics, HabitRead


def map_to_habit_analytics_schema(habit_info: dict) -> HabitAnalytics:
	if habit_info is None or len(habit_info) == 0:
		return #raise error maybe?

    #check if there is name etc?
	read_schema = HabitAnalytics(
        habit_name = str(habit_info['habit_name']),
        habit_id=int(habit_info['habit_id']),
        habit_streak=int(habit_info['habit_streak']),
	)
	return read_schema

