class ProgressHistoryDTO:
	"""
	Instead of passing around objects for observers and notification strategies, we pass around DTOs, more lightweight
	"""
	def __init__(self, last_updated_time, distance_from_goal_kvi, streak):
		self.last_updated_time = last_updated_time
		self.distance_from_goal = distance_from_goal_kvi
		self.streak = streak


	def to_dict(self):
		return self.__dict__