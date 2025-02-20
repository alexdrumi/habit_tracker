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

	#get goal data (dict) from goal repo
	goal_data = goal_service.get_goal_entity_by_id(goal_id, habit_id) #this will need validation thus should go through facade or service

	goal_subject = GoalSubject(goal_service=goal_service, goal_data=goal_data)

	#attach observer (s?)
	goal_subject.attach(ProgressObserver(progress_service=progress_service))

	return goal_subject