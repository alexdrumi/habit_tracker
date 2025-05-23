from apps.progresses.repositories.progress_repository import ProgressesRepository
from apps.progresses.services.progress_service import ProgressesService
from apps.goals.domain.goal_subject import GoalSubject


class ProgressObserver:
	def __init__(self, progress_service: ProgressesService):
		self._progress_service = progress_service


	def update(self, progress_data: dict): #we can just pass a dict to update methods in general.
		"""
		Should be updated when the goals current kvi value changes.
		Creates a progress entry in the database.

		Args:
			goal_subject (Goalsubject): The goal object containing the updated values.
		"""
		goal_id = progress_data['goal_id']
		goal_name = progress_data['goal_name']
		habit_name = progress_data['habit_name']
		current_val = progress_data['current_kvi']
		target_val = progress_data['target_kvi']
		current_streak = progress_data['streak']
		distance_from_goal = target_val - current_val

		#should we handle this via the service? No validation logic is applied here.		
		self._progress_service.create_progress(
			goal_id=goal_id,
			current_kvi_value=current_val,
			distance_from_target_kvi_value=distance_from_goal,
			current_streak=current_streak,
			progress_description="some autogen entry",
			goal_name=goal_name,
			habit_name=habit_name
			#progress will need streak as well
			#here we could add the habit name and goal name

		)
