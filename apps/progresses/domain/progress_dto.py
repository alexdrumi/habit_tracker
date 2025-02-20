class ProgressHistoryDTO:
	"""
	Instead of passing around objects for observers and notification strategies, we pass around DTOs, more lightweight
	"""
	def __init__(self, last_updated_time, total_completed_times, distance_from_goal_kvi):
		self._last_updated_time = last_updated_time
		self._total_completed_times = total_completed_times
		self._distance_from_goal = distance_from_goal_kvi