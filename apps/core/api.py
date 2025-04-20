from fastapi import APIRouter, Depends, HTTPException, status


from apps.database.database_manager import MariadbConnection
from apps.users.repositories.user_repository import UserRepository
from apps.users.services.user_service import UserService
from apps.habits.repositories.habit_repository import HabitRepository
from apps.habits.services.habit_service import HabitService
from apps.goals.repositories.goal_repository import GoalRepository
from apps.goals.services.goal_service import GoalService
from apps.progresses.repositories.progress_repository import ProgressesRepository
from apps.progresses.services.progress_service import ProgressesService
from apps.reminders.services.reminder_service import ReminderService
from apps.core.facades.habit_tracker_facade_impl import HabitTrackerFacadeImpl
from apps.core.controllers.habit_controller import HabitController
from apps.core.orchestrators.habit_orchestrator import HabitOrchestrator
from apps.analytics.repositories.analytics_repository import AnalyticsRepository
from apps.analytics.services.analytics_service import AnalyticsService

from functools import lru_cache


router = APIRouter(
	prefix="/api",
	tags = ["Habit_tracker_API"]
)


def get_database():
	database = MariadbConnection()
	try:
		return database
	except ValueError as e:
		raise HTTPException(status_code=422, detail=str(e))

#only triggered in the first request, then reuse it. Prefer this to a singleton for now
@lru_cache
def create_habit_controller(database = Depends(get_database)) -> HabitController:
	user_repository = UserRepository(database)
	user_service = UserService(user_repository)
	habit_repository = HabitRepository(database, user_repository)
	habit_service = HabitService(habit_repository)
	goal_repository = GoalRepository(database, habit_repository)
	goal_service = GoalService(goal_repository, habit_service)
	progress_repository = ProgressesRepository(database, goal_repository)
	progress_service = ProgressesService(progress_repository, goal_service)
	reminder_service = ReminderService(goal_service=goal_service)
	analytics_repository = AnalyticsRepository(database=database, habit_repository=habit_repository) #not sure if we need habit stuff here
	analytics_service = AnalyticsService(repository=analytics_repository, 
									  habit_service=habit_service, 
									  progress_service=progress_service) #not sure if we need habit stuff here
	
	habit_tracker_facade = HabitTrackerFacadeImpl(user_service=user_service,
							habit_service=habit_service, 
							goal_service=goal_service, 
							progress_service=progress_service, 
							reminder_service=reminder_service, 
							analytics_service=analytics_service)

	habit_tracker_orchestrator = HabitOrchestrator(habit_tracker_facade=habit_tracker_facade)
	habit_controller = HabitController(habit_tracker_facade=habit_tracker_facade,
									habit_tracker_orchestrator=habit_tracker_orchestrator)
	
	return habit_controller


#---USERS---
# @router.post("/create_user", status_code=status.HTTP_201_CREATED)
# def create_user(
# 	user_name: str,
# 	user_age: int,
# 	user_gender: str,
# 	user_role: str,
# 	ctrl: HabitController = Depends(create_habit_controller)):

# 	try:
# 		return ctrl.create_user(user_name, user_age, user_gender, user_role)
# 	except ValueError as error:
# 		raise HTTPException(status_code=422, detail=str(error))


#query all user data
# @router.get("/query_all_users", status_code=status.HTTP_200_OK)
# def query_all_users(ctrl: HabitController = Depends(create_habit_controller)):
# 	try:
# 		return ctrl.query_all_users()
# 	except Exception as error:
# 		raise HTTPException(status_code=400, detail=str(error))


#---HABITS---
#create a habit
@router.post("/create_a_new_habit", status_code=status.HTTP_201_CREATED)
def create_new_habit(
	habit_name: str,
	habit_action: str,
	user_id: int,
	habit_periodicity_type: int,
	habit_goal_name: str,
	habit_goal_description: str,
	ctrl: HabitController = Depends(create_habit_controller)):

	periodicity_type = 'daily' if int(habit_periodicity_type) == 1 else 'weekly'
	target_kvi_val = 1.0 if periodicity_type == 'daily' else 7.0

	try:
		new_habit = ctrl.create_a_habit_with_validation(habit_name, habit_action, periodicity_type, user_id)
		new_goal = ctrl.create_a_goal(goal_name=habit_goal_name, habit_id=new_habit['habit_id'], target_kvi_value=target_kvi_val, current_kvi_value=0.0, goal_description=habit_goal_description)
		
	except Exception as error:
		raise HTTPException(status_code=422, detail=str(error))



# #get all the habits
# @router.get("/get_all_habits")
# def get_all_habits(ctrl: HabitController = Depends(create_habit_controller)):
# 	try:
# 		all_habits = ctrl.get_all_habits()
# 		return all_habits
# 	except Exception as error:
# 		raise HTTPException(status_code=400, detail=str(error))


#list goals and habits
# @router.get("/get_goals_and_habits")
# def list_all_goals_with_habits(ctrl: HabitController = Depends(create_habit_controller)):
# 	try:
# 		goals_and_related_habits = ctrl.query_goals_and_related_habits()
# 		return goals_and_related_habits
# 	except Exception as error:
# 		raise HTTPException(status_code=400, detail=str(error))


# #get list of tickable habits
# @router.get("/list_tickable_habits")
# def fetch_ready_to_tick_goals(ctrl: HabitController = Depends(create_habit_controller)):
# 	try:
# 		tickable_habits_and_goals = ctrl.fetch_ready_to_tick_goals_of_habits()
# 		return tickable_habits_and_goals
# 	except Exception as error:
# 		raise HTTPException(status_code=400, detail=str(error))


# #tick a habit
# @router.post("/complete_habit")
# def complete_habit(
# 	habit_id: int,
# 	goal_id: int,
# 	ctrl: HabitController = Depends(create_habit_controller)):
# 		try:
# 			ctrl.complete_a_habit(int(habit_id), int(goal_id))
# 		except Exception as error:
# 			raise HTTPException(status_code=422, detail=str(error))



#---ANALYTICS---
#get longest streak in database
# @router.get("/get_longest_streak")
# def longest_streak_in_database(ctrl: HabitController = Depends(create_habit_controller)):
# 	try:
# 		result = ctrl.calculate_longest_streak()
# 		return result
# 	except Exception as error:
# 		raise HTTPException(status_code=400, detail=str(error))



#get the same habit per types
@router.get("/get_same_habit_periodicity")
def same_habit_periodicity(ctrl: HabitController = Depends(create_habit_controller)):
	try:
		result = ctrl.get_same_periodicity_type_habits()
		return result
	except Exception as error:
		raise HTTPException(status_code=400, detail=str(error))



#get currently tracked habits
@router.get("/get_currently_tracked_habits")
def currently_tracked_habits(ctrl: HabitController = Depends(create_habit_controller)):
	try:
		result = ctrl.get_currently_tracked_habits()
		return result
	except Exception as error:
		raise HTTPException(status_code=400, detail=str(error))



#get longest streak ever for a habit
@router.get("/get_longest_ever_streak")
def get_longest_ever_streak_for_habit(
	habit_id:int, 
	ctrl: HabitController = Depends(create_habit_controller)):
	#we should call option 5, get all habits for this, then offer to select a habit id
	try:
		result =  ctrl.longest_streak_for_habit(habit_id=habit_id)
		return result
	except Exception as error:
		raise HTTPException(status_code=400, detail=str(error))





@router.get("/hi", status_code=status.HTTP_201_CREATED)
def hi():
	try:
		return {"message": "hi there from api/hi"}
	except ValueError as e:
		raise HTTPException(status_code=422, detail=str(e))