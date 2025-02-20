# apps/goals/domain/factories.py
from apps.goals.domain.goal_subject import GoalSubject
from apps.goals.repositories.goal_repository import GoalRepository

from apps.goals.services.goal_service import GoalService

from apps.progresses.repositories.progress_repository import ProgressesRepository
from apps.progresses.services.progress_service import ProgressesService

from apps.progresses.domain.progress_observer import ProgressObserver
from apps.goals.domain.goal_subject import GoalSubject


def build_goal_subject(goal_id, habit_id, goal_service: GoalService, progress_service: ProgressesRepository):
	#creates a Goalsubject, attaches observer (s) and returns it.

	#goal data pulled by id, for now via repo but I prob will change it to facade for input checks via service
	# goal_data = goal_repo.repoget_goal_entity_by_id(validated_goal_id, validated_habit_id)
	# goal_entity = self._habit_facade.get_goal_entity_by_id(validated_goal_id, validated_habit_id)

	#get goal data (dict) from goal repo
	goal_data = goal_service.get_goal_entity_by_id(goal_id, habit_id) #this will need validation thus should go through facade or service


	goal_subject = GoalSubject(goal_service=goal_service, goal_data=goal_data)

	#attach observer (s?)
	goal_subject.attach(ProgressObserver(progress_service=progress_service))

	return goal_subject