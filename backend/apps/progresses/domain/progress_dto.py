class ProgressHistoryDTO:
	"""
	Instead of passing around objects for observers and notification strategies, we pass around DTOs, more lightweight
	"""
	def __init__(self, last_updated_time, distance_from_goal_kvi, streak):
		self.last_updated_time = last_updated_time
		self.distance_from_goal = distance_from_goal_kvi
		self.streak = streak

# {'goal_id': 16, 'habit_id': 35, 'target_kvi': 7.0, 'current_kvi': 14.0, 'streak': 0, 7.0: -7.0, 'last_occurence': datetime.datetime(2025, 3, 4, 9, 4, 31)}  is progress data

	def to_dict(self):
		return self.__dict__