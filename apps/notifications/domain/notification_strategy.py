from abc import ABC, abstractmethod


class NotificationStrategy(ABC):
	"""
	An abstract base class that defines the interface for different
	notification strategies. Any custom notification strategy should 
	implement these methods.
	"""
	@abstractmethod
	def on_completion_message(self, goal_subject):
		pass

	@abstractmethod
	def on_expired_message(self, goal_subject):
		pass