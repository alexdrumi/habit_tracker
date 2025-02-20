from apps.progresses.repositories.progress_repository import ProgressesRepository
from apps.progresses.services.progress_service import ProgressesService
from apps.goals.domain.goal_subject import GoalSubject

class ProgressObserver:
	def __init__(self, progress_service: ProgressesService):
		self._progress_service = progress_service

	def update(self, goal_subject: GoalSubject):
		"""
		Should be updated when the goals current kvi value changes.
		Creates a progress entry in the database.

		Args:
			goal_subject (Goalsubject): The goal object containing the updated values.
		"""
		goal_id = goal_subject._goal_data['goal_id']
		current_val = goal_subject._goal_data['current_kvi']
		target_val = goal_subject._goal_data['target_kvi']

		distance_from_goal = target_val - current_val

		#should we handle this via the service? No validation logic is applied here.
		self._progress_service.create_progress(
			goal_id=goal_id,
			current_kvi_value=current_val,
			distance_from_target_kvi_value=distance_from_goal,
			progress_description="some autogen entry"
		)
