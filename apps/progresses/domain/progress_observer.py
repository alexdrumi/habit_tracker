from apps.progresses.repositories.progress_repository import ProgressesRepository
from apps.goals.domain.goal_subject import GoalSubject

class ProgressObserver:
	def __init__(self, progress_repo: ProgressesRepository):
		self._progress_repo = progress_repo

	def update(self, goal_subject: GoalSubject): #
		"""
		Shoukld be updated when the goals current kvi val changes
		Creates a progress entry in the database.

		Args

		return
		"""
		goal_data = goal_subject.goal_data
		goal_id = goal_data['goal_id']
		current_val = goal_data['current_kvi_value']
		target_val = goal_data['target_kvi_value']

		distance_from_goal = target_val - current_val

		#SHALL WE GO THROUGH THE SERVICE? AS THESE DO NOT HAVE ANY VALIDATION LOGIC HERE
		self.progress_repo.create_progress(
			goal_id=goal_id,
			current_kvi_value=current_val,
			distance_from_target_kvi_value=distance_from_goal,
			progress_description="Auto-generated progress entry"
		)
