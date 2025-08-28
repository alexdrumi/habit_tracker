import sys
import os
import django
import click
import datetime
import random
import argparse

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

sys.path.insert(0, BASE_DIR)

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()

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
from cli import CLI



def signal_handler(sig, frame):
	"""
	A handler function triggered when the user presses Ctrl+c (SIGINT).
	Prints a dutch farewell message and exits the application gracefully.

	Args:
		sig (int): The signal number that triggered this handler (e.g., SIGINT).
		frame (FrameType): The current stack frame (unused here).

	Returns:
		None
	"""
	print('You pressed Ctrl+C, doei!')
	sys.exit(0)



def seed(habit_controller: HabitController):
	"""
	Seeds the database with a test user, several habits, and associated goals.
	Also generates progress records for those habits randomly over the last 30 days.

	Args:
		habit_controller (HabitController): A controller handling user/habit creation and updates.

		
	Returns:
		None
	"""
	click.echo(click.style("\n--- AS REQUESTED, STARTING DATABASE SEEDING PROCESS---", fg="green", bold=True))

	test_user = habit_controller.create_user(f'Testuser{random.random()}', 35, "Male", "user")
	test_user_id = test_user["user_id"]
	click.echo(f"Created test user with ID: {test_user_id}")

	habits_to_create = [
		(f"daily reading{random.random():.4f}", "read 5 pages", "daily"),
		(f"daily meditation{random.random():.4f}", "meditate 10 mins", "daily"),
		(f"weekly run{random.random():.4f}", "run 10 kms", "weekly"),
		(f"weekly blog writing{random.random():.4f}", "write 2 pages for your blog", "weekly"),
	]

	click.echo("\nCreating sample habits and associated goals.")
	created_habits = []
	for habit_name, habit_action, habit_periodicity_type in habits_to_create:
		habit_periodicity_value = 1.0 if habit_periodicity_type == 'daily' else 7.0
		new_habit = habit_controller.create_a_habit_with_validation(
			habit_name=habit_name,
			habit_action=habit_action,
			periodicity_type=habit_periodicity_type,
			user_id=test_user_id
		)
		created_habits.append(new_habit)
		goal_name = f"Goal for {habit_name}"
		goal_description = f"This is a {habit_periodicity_type} goal."
		habit_controller.create_a_goal(
			goal_name=goal_name, 
			habit_id=new_habit['habit_id'], 
			target_kvi_value=habit_periodicity_value, 
			current_kvi_value=0.0, 
			goal_description=goal_description)

	now = datetime.datetime.now()
	thirty_days_ago = now - datetime.timedelta(days = 30)

	click.echo("\nGenerating progress entries over the last 30 days.")
	for habit in created_habits:
		habit_id = habit["habit_id"]

		current_date = thirty_days_ago
		goal_id = habit_controller.query_goal_of_a_habit(habit_id=habit_id)

		while current_date <= now:
			if random.random() < 0.7:
				if goal_id and current_date.weekday() != 6:
					habit_controller.create_progress(
						goal_id=goal_id[0],
						current_kvi_value=1.0,
						distance_from_target_kvi_value=0.0,
						goal_name= f"fake_progress{random.random()}",
						habit_name= f"name:{random.random()}",
						progress_description="Auto seeded progress",
						occurence_date=current_date
					)
			current_date += datetime.timedelta(days=1)
		last_progress_streak = habit_controller.get_last_progress_entry(goal_id=goal_id[0])
		if last_progress_streak:
			habit_controller.get_current_streak(habit_id=habit_id)[0]
			updated_streak = last_progress_streak[6]
			habit_controller.update_habit_streak(habit_id=habit_id, updated_streak_value=updated_streak)
	
	click.echo(click.style("\n---SEEDING COMPLETED. DATABASE HAS BEEN POPULATED WITH DATA FOR 30 DAYS.---", fg="green", bold=True))



def init_parser():
	"""
	Initializes an argument parser for optional CLI arguments, 
	such as a `--seed` flag to pre-populate the database.

	Returns:
		argparse.Namespace: Parsed arguments with a `seed` attribute (boolean).
	"""
	parser = argparse.ArgumentParser(description="Habit Tracker CLI")
	parser.add_argument(
		'--seed',
		action='store_true',
		help="Seed the database with sample data, in case you would need it."
	)
	return parser.parse_args()



def main():

	args = init_parser()

	database = MariadbConnection()
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
	analytics_service = AnalyticsService(repository=analytics_repository, habit_service=habit_service, progress_service=progress_service) #not sure if we need habit stuff here
	
	habit_tracker_facade = HabitTrackerFacadeImpl(user_service=user_service, habit_service=habit_service, goal_service=goal_service, progress_service=progress_service, reminder_service=reminder_service, analytics_service=analytics_service)
	habit_tracker_orchestrator = HabitOrchestrator(habit_tracker_facade=habit_tracker_facade)
	habit_controller = HabitController(habit_tracker_facade=habit_tracker_facade, habit_tracker_orchestrator=habit_tracker_orchestrator)
	

	if args.seed:
		seed(habit_controller=habit_controller)

	cli = CLI(controller=habit_controller)
	cli.run()

if __name__ == '__main__':
	main()