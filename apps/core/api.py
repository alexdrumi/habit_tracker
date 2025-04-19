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


#crete user
@router.post("/create_user", status_code=status.HTTP_201_CREATED)
def create_user(
	user_name: str,
	user_age: int,
	user_gender: str,
	user_role: str,
	ctrl: HabitController = Depends(create_habit_controller)):

	try:
		return ctrl.create_user(user_name, user_age, user_gender, user_role)
	except ValueError as error:
		raise HTTPException(status_code=422, detail=str(error))


#query all user data
@router.get("/query_all_users", status_code=status.HTTP_200_OK)
def query_all_users(ctrl: HabitController = Depends(create_habit_controller)):
	try:
		return ctrl.query_all_users()
	except Exception as error:
		raise HTTPException(status_code=400, detail=str(error))


#create a habit
@router.post("/create_a_new_habit", status_code=status.HTTP_201_CREATED):
	def option_4_create_new_habit(
	habit_name: str,
	habit_action: str,
	user_id: int,
	periodicity_type: str,
	ctrl: HabitController = Depends(create_habit_controller)):):




	def option_4_create_new_habit(self):
		"""
		CLI flow to create a new habit for a specific user. 
		It also creates an associated goal for that habit.
		"""
		click.echo(click.style("\n[Option 4] Create a habit for a certain user", fg="cyan", bold=True))
		click.pause()

		click.echo(click.style("\nStep 1: Habit Basic Information", fg="yellow", bold=True))
		habit_name = click.prompt(click.style("Enter the habit name", fg="white", bold=True), type=str)
		habit_action = click.prompt(click.style("Enter the habit action", fg="white", bold=True), type=str)
		user_id = self.prompt_for_valid_integer(click.style("Enter the user ID for whom this habit is being created", fg="white", bold=True))
		habit_periodicity_type = self.prompt_for_choice(
			click.style("Select the periodicity type (1 for DAILY, 2 for WEEKLY)", fg="white", bold=True),
			['1', '2'])
	
		periodicity_type = 'daily' if int(habit_periodicity_type) == 1 else 'weekly'
		target_kvi_val = 1.0 if periodicity_type == 'daily' else 7.0
		habit_goal_name = click.prompt(click.style("Enter the name of the goal associated with this habit", fg="white", bold=True), type=str).strip()
		habit_goal_description = click.prompt(click.style("Describe the goal", fg="white", bold=True), type=str).strip()
	
		try:
			new_habit = self._controller.create_a_habit_with_validation(habit_name, habit_action, periodicity_type, user_id)
			new_goal = self._controller.create_a_goal(goal_name=habit_goal_name, habit_id=new_habit['habit_id'], target_kvi_value=target_kvi_val, current_kvi_value=0.0, goal_description=habit_goal_description)
			click.echo(click.style("\n=New Habit and associated Goal created successfully!", fg="green", bold=True))
			click.echo(click.style(f"\nHabit ID: {new_habit['habit_id']}", fg="yellow"))
			click.echo(click.style(f"Goal ID: {new_goal['goal_id']}\n", fg="yellow"))
		except Exception as error:
			click.echo(click.style(f"Error while creating a new habit and its associated goal: {error}", fg="red", bold=True))





















@router.get("/hi", status_code=status.HTTP_201_CREATED)
def hi():
	try:
		return {"message": "hi there from api/hi"}
	except ValueError as e:
		raise HTTPException(status_code=422, detail=str(e))