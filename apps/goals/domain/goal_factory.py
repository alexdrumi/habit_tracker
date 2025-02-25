# apps/goals/domain/factories.py
from apps.goals.domain.goal_subject import GoalSubject
from apps.goals.repositories.goal_repository import GoalRepository

from apps.goals.services.goal_service import GoalService

from apps.progresses.services.progress_service import ProgressesService

from apps.progresses.domain.progress_observer import ProgressObserver
from apps.goals.domain.goal_subject import GoalSubject
from apps.notifications.domain.notification_observer import NotificationObserver
from apps.notifications.domain.notification_strategy import NotificationStrategy

def build_goal_subject(goal_id, habit_id, habit_periodicity_type, goal_service: GoalService, progress_service: ProgressesService):
	#creates a Goalsubject, attaches observer (s) and returns it.

	#get goal data (dict) from goal repo
	goal_data = goal_service.get_goal_entity_by_id(goal_id, habit_id) #this will need validation thus should go through facade or service

	goal_subject = GoalSubject(goal_service=goal_service, progress_service=progress_service, goal_data=goal_data)

	goal_notification_strategy = habit_periodicity_type[0] #?
	#attach observer (s?)

	print(f"The habit periodicity type is: {goal_notification_strategy}")

	goal_subject.attach(ProgressObserver(progress_service=progress_service))
	goal_subject.attach(NotificationObserver(notification_stragety=goal_notification_strategy))
	return goal_subject