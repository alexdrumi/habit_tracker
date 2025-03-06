from abc import ABC, abstractmethod


class NotificationStrategy(ABC):
	# @abstractmethod
	# def before_deadline_message(self, goal_subject):
	# 	pass
	
	@abstractmethod
	def on_completion_message(self, goal_subject):
		pass

	@abstractmethod
	def on_expired_message(self, goal_subject):
		pass