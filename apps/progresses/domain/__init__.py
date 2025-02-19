from apps.progresses.repositories.progress_repository import ProgressesRepository


class ProgressObserver:
	def __init__(self, progress_repo):
		self.progress_repo = progress_repo  # So we can store progress in DB


	def update(self, goal_subject):
