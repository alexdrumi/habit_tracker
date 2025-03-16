import sys
import os
import django

#for correct import path
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

#ensure that we can locate the apps 
sys.path.insert(0, BASE_DIR)

#setuop the config otherwise cli doesnt see the modules
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

import datetime
import random

def signal_handler(sig, frame):
	print('You pressed Ctrl+C, doei!')
	sys.exit(0)

# def seed()
# #seed data here


def main():
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
	

	#--------SEED---------

	test_user = habit_controller.create_user(f'Testuser{random.random()}', 35, "Male", "user")
	test_user_id = test_user["user_id"]

	habits_to_create = [
		(f"daily reading{random.random()}", "read 5 pages", "daily"),
		(f"daily meditation{random.random()}", "meditate 10 mins", "daily"),
		(f"weekly run{random.random()}", "run 10 kms", "weekly"),
		(f"weekly blog writing{random.random()}", "write 2 pages for your blog", "weekly"),
	]

	created_habits = []
	#self, habit_name, habit_action, habit_periodicity_type, habit_user_id, habit_streak=None, habit_periodicity_value=None):
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
		new_goal = habit_controller.create_a_goal(
			goal_name=goal_name, 
			habit_id=new_habit['habit_id'], 
			target_kvi_value=habit_periodicity_value, 
			current_kvi_value=0.0, 
			goal_description=goal_description)

	now = datetime.datetime.now()
	thirty_days_ago = now - datetime.timedelta(days = 30)

	for habit in created_habits:
		habit_id = habit["habit_id"]

		current_date = thirty_days_ago
		while current_date <= now:
			if random.random() < 0.7:
				goal_id = goal_service.query_goal_of_a_habit(habit_id=habit_id) #maybe we can write a controller call for this
				print(f"{goal_id} is the goal_id")
				if goal_id and current_date.weekday() != 6:  #not sunday for instance
					progress_service.create_progress(
						goal_id=goal_id[0],
						current_kvi_value=1.0, #should be +1 each time to be honest, we ll see
						distance_from_target_kvi_value=0.0,
						# current_streak= 1, #+=1 compared to prev..
						goal_name= f"fake_progress{random.random()}",
						habit_name= f"name:{random.random()}",
						progress_description="Auto seeded progress",
						occurence_date=current_date
					)
				#update the related habits streak to the progress streak
			current_date += datetime.timedelta(days=1)	

	print("SEEDING IS COMPLETED")	
	cli = CLI(controller=habit_controller)
	cli.run()

if __name__ == '__main__':
	main()