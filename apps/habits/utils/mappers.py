from apps.habits.schemas import PeriodicityType, HabitCreate, HabitRead

def map_to_habit_read_schema(habit_info: dict) -> HabitRead:
	if habit_info is None or len(habit_info) == 0:
		return
	per_type = habit_info['habit_periodicity_type']
	if isinstance(per_type, PeriodicityType):
		per_type = per_type.value  #gets daily or weekly

	read_schema = HabitRead(
	habit_name = str(habit_info['habit_name']),
	habit_id=int(habit_info['habit_id']),
	habit_action=str(habit_info['habit_action']),
	habit_streak=int(habit_info['habit_streak']),
	habit_periodicity_type=per_type,  #should be now daily or weeklty
	habit_user_id=int(habit_info['habit_user_id']),
	)
	return read_schema