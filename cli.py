import sys
import os
import click
import django
import signal

#for correct import path
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

#ensure that we can locate the apps 
sys.path.insert(0, BASE_DIR)

#setuop the config otherwise cli doesnt see the modules
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()




from apps.database.database_manager import MariadbConnection
from apps.users.repositories.user_repository import UserRepository, UserRepositoryError, UserNotFoundError
from apps.users.services.user_service import UserService
from apps.habits.repositories.habit_repository import HabitRepository, HabitNotFoundError
from apps.habits.services.habit_service import HabitService
from apps.core.facades.habit_tracker_facade_impl import HabitTrackerFacadeImpl
from apps.goals.repositories.goal_repository import GoalRepository, GoalRepositoryError, GoalNotFoundError, GoalAlreadyExistError
from apps.goals.services.goal_service import GoalService
from apps.progresses.repositories.progress_repository import ProgressesRepository
from apps.progresses.services.progress_service import ProgressesService
from apps.reminders.services.reminder_service import ReminderService
from apps.core.controllers.habit_controller import HabitController
from apps.core.orchestrators.habit_orchestrator import HabitOrchestrator

from apps.analytics.repositories.analytics_repository import AnalyticsRepository
from apps.analytics.services.analytics_service import AnalyticsService

def signal_handler(sig, frame):
	print('You pressed Ctrl+C, doei!')
	sys.exit(0)


class CLI:
	def __init__(self, controller: HabitController):
		self._controller = controller

	""""""
	def display_users(self, all_users):
		for user in all_users:
			print(f"user_id: {user[0]}, user_name: {user[1]}")

	def display_habits(self, habits):
		for habit in habits:
			print(f"\nhabit_id: {habit[0]}, habit_user_id: {habit[3]}, habit_name: {habit[1]}, habit_action: {habit[2]}, ")

	def display_goals_and_habits(self, goals_and_habits):
		for data in goals_and_habits:
			print(f"\ngoal_name: {data[0]}, goal_id: {data[1]}, habit_name: {data[3]}, habit_id: {data[2]}")
	

	def display_same_periodicity_type_habits(self, habits):
		for habit_type in habits:
			periodicity = habit_type[0]  #daily or weekly atm
			habit_count = habit_type[1]  #how many are there in the group
			habit_list = habit_type[2]   #concatted string

			#header
			print("\n" + "-" * 80)
			print(click.style(f" Habits with periodicity type: {periodicity.upper()} ", fg="green", bold=True))
			print("\n" + "-" * 80)

			#split into individual habit list
			all_habits = habit_list.split(',')

			for habit in all_habits:
				habit_details = habit.split(':')
				habit_id = habit_details[0].strip()
				habit_name = habit_details[1].strip()
				print(
					click.style("Habit ID: ", fg="yellow", bold=True) + 
					click.style(habit_id, fg="green") +
					click.style(" | Habit Name: ", fg="yellow", bold=True) + 
					click.style(habit_name, fg="white", bold=True)
				)
		print("\n" + "-" * 80)





	def display_tracked_habits(self, habits):
		if not habits:
			click.echo(click.style("\nNo habits are currently being tracked.", fg="red", bold=True))
			return

		print("\n" + "-" * 80)
		print(click.style(" Currently tracked habits ", fg="green", bold=True))
		print("-" * 80)

		for habit in habits:
			habit_id, habit_name, streak, periodicity = habit

			click.echo(
				click.style("Habit ID: ", fg="yellow", bold=True) + 
				click.style(str(habit_id), fg="green") + 
				click.style(" | Habit name: ", fg="yellow", bold=True) + 
				click.style(habit_name, fgs="white", bold=True) +
				click.style(" | Streak: ", fg="yellow", bold=True) +
				click.style(str(streak), fg="magenta") +
				click.style(" | Periodicity: ", fg="yellow", bold=True) + 
				click.style(periodicity.capitalize(), fg="blue", bold=True)
			)  

		print("-" * 80)



	def display_menu(self):
		click.echo("\nMain menu:")
		click.echo("1, Create a new user")
		click.echo("2, Delete a user")
		click.echo("3, Get all user info")
		click.echo("4, Create a habit for a certain user")
		click.echo("5, List all habits")
		click.echo("6, Delete a certain habit")
		click.echo("7, List goals with associated habits")
		click.echo("8, Complete a habit/goal")
		click.echo("9, Get longest habit streak")
		click.echo("10, Get habits by same periodicity type")
		click.echo("11, Get currently tracked habits")
		click.echo("12, Get longest ever streak for habit")

	def prompt_for_valid_integer(self, message):
		while True:
			value = click.prompt(message, type=str).strip()
			if value.isdigit():
				return int(value)
			click.echo("Invalid input. Please enter a valid integer.")

	def prompt_for_choice(self, message, choices):
		while True:
			value = click.prompt(message, type=str).strip()
			if value in choices:
				return value
			click.echo(f"Invalid choice. Please select from: {', '.join(choices)}.")


	def option_1_create_user(self):
		click.echo("You selected option 1 - create a user. ")
		click.pause()

		user_name =  click.prompt("Enter user name:")
		user_age =  click.prompt("Enter user age:")
		user_gender = click.prompt("Enter user gender:")
		user_role = click.prompt("Enter user role:")

		# user = self._facade.create_user(user_name, user_age, user_gender, user_role)
		print(f"The following user has been created:\n{user}")
		user = self._controller.create_user(user_name, user_age, user_gender, user_role)
		click.echo(f"User created: {user}")


	def option_2_delete_user(self):
		click.echo("You selected option 2 - delete a user. ")
		click.pause()

		user_id =  click.prompt("Enter user id:")
		self._controller.delete_user(int(user_id)) #we could check for row count but it will throw an error anyway
		click.echo(f"User with user_id {user_id} deleted.")


	def option_3_query_all_user_data(self):
		click.echo("You selected option 3 - get all user info. ")
		click.pause()

		all_users = self._controller.query_all_users()
		self.display_users(all_users)

# 	def option_4_list_users_with_existing_habits(self):
# 		click.echo("You selected option 4 - List users with already existing habits")
# 		click.pause()

# 		users_and_related_habits = self._facade.query_user_and_related_habits()
# 		self.print_users_and_habits(users_and_related_habits)

	def option_4_create_new_habit(self):
		click.echo("You selected option 5 - create a habit for a certain user.\n")
		click.pause()

		habit_name =  click.prompt("Enter a habit name:", type=str)
		habit_action = click.prompt("Enter a habit action:", type=str)
		user_id = self.prompt_for_valid_integer("Enter the user_id of the user whose habit you want to create")
			
			
		habit_periodicity_type = self.prompt_for_choice(
			"Enter the periodicity of the habit. Enter 1 for 'DAILY', Enter 2 for 'WEEKLY'", 
			['1', '2']
		)
		periodicity_type = 'daily' if int(habit_periodicity_type) == 1 else 'weekly'
		target_kvi_val = 1.0 if periodicity_type == 'daily' else 7.0

		habit_goal_name = click.prompt("Enter a name for the goal which you want to achieve with this habit:", type=str).strip()
		habit_goal_description = click.prompt("Describe your goal:", type=str).strip()
	
		new_habit = self._controller.create_a_habit_with_validation(habit_name, habit_action, periodicity_type, user_id)
		new_goal = self._controller.create_a_goal(goal_name=habit_goal_name, habit_id=new_habit['habit_id'], target_kvi_value=target_kvi_val, current_kvi_value=0.0, goal_description=habit_goal_description)

		click.echo(f"\nNew habit created:\n{new_habit}\nAssociated goal: {new_goal}")


	def option_5_get_all_habits(self):
		click.echo("You selected option 6 - list all habits.")
		click.pause()
		
		all_habits = self._controller.get_all_habits()
		self.display_habits(all_habits)


	def option_6_delete_a_habit(self):
		click.echo("You selected option 7 - delete a habit.")
		click.pause()

		habit_id = self.prompt_for_valid_integer("Enter the habit ID to delete.")
		#pull the related goal id
		deleted_amount = self._controller.delete_a_habit(int(habit_id)) 
		
		click.echo(f"\nDeleted habit with id {habit_id}")



	def option_7_list_all_goals_with_habits(self):
		click.echo("You selected option 9 - List goals with their associated habits")
		click.pause()

		users_and_related_habits = self._controller.query_goals_and_related_habits()
		self.display_goals_and_habits(users_and_related_habits)

	def display_tickable_habits(self, goals):
		print("\n==================== TICKABLE HABITS AND THEIR ASSOCIATED GOALS ====================")
		
		for goal in goals:
			habit_id = goal["habit_id"]
			goal_id = goal["goal_id"]
			goal_name = goal["goal_name"]
			target_kvi_value = goal["target_kvi_value"]
			current_kvi_value = goal["current_kvi_value"]
			occurence_date = goal["occurence_date"]

			if occurence_date is None:
				occurence_date_str = "Never Ticked"
			else:
				occurence_date_str = occurence_date.strftime("%Y-%m-%d %H:%M:%S")

			#eventually we could even place these in one single print call, also the rest above
			print(f"\nHabit ID: {habit_id}")
			print(f"Goal ID: {goal_id}")
			print(f"Goal Name: {goal_name}")
			print(f"Target KVI: {target_kvi_value}")
			print(f"Current KVI: {current_kvi_value}")
			print(f"Last Ticked: {occurence_date_str}")
			print("\n" + "-" * 80)


	def option_8_complete_habit(self):
		click.echo("You selected option 11 - Complete a habit")
		click.pause()

		self.option_7_list_all_goals_with_habits()

		tickable_habits_and_goals = self._controller.fetch_ready_to_tick_goals_of_habits()
		self.display_tickable_habits(tickable_habits_and_goals)
		
		habit_id = self.prompt_for_valid_integer("Enter a habit ID.")
		goal_id = self.prompt_for_valid_integer("Enter a goal ID.")

		self._controller.complete_a_habit(habit_id=int(habit_id), goal_id=int(goal_id))

	def option_9_longest_streak(self):
		click.echo("\nYou selected option 9 - Longest Habit Streak")
		click.pause()

		result = self._controller.calculate_longest_streak()

		if result:
			#we can style it like this also for the rest
			click.echo(click.style("\nHabit with the longest current streak:", fg="green", bold=True))
			click.echo(click.style(f"  Habit Name: {result[1]}", fg="white"))
			click.echo(click.style(f"  Habit ID: {result[0]}", fg="white"))
			click.echo(click.style(f"  Streak: {result[2]} days", fg="yellow", bold=True))
		else:
			click.echo(click.style("\nNo habits found with streaks yet. Complete a habit first!", fg="red", bold=True))


	def option_10_same_habit_periodicity(self):
		click.echo("\nYou selected option 10 - Group habits by periodicity.")
		click.pause()
		
		result = self._controller.get_same_periodicity_type_habits()
		#[('daily', 2, '[{"habit_id": 43, "habit_name": "test1"},{"habit_id": 44, "habit_name": "test2"}]'), ('weekly', 1, '[{"habit_id": 45, "habit_name": "tedst3"}]')]
		# print(result)
		self.display_same_periodicity_type_habits(result)


	def option_11_get_currently_tracked_habits(self):
		click.echo("\nYou selected option 11 - Get currently tracked habits.")
		click.pause()

		result = self._controller.get_currently_tracked_habits()
		self.display_tracked_habits(result)


	def option_12_get_longest_ever_streak_for_habit(self):
		click.echo("\nYou selected option 12 - Get_longest_ever_streak_for_habit.")
		click.pause()
		 
		habit_id = self.prompt_for_valid_integer("Select a habit id for its longest ever streak recorded")
		result = self._controller.longest_streak_for_habit(habit_id)
		click.echo(click.style(f"Longest streak opf habit {habit_id}: {result[0][1]} days", fg="yellow", bold=True))


	
	def run(self):
		signal.signal(signal.SIGINT, signal_handler)
		self._controller.get_pending_goals()

		while True:
			self.display_menu()
			choice = click.prompt("\nEnter your choice", type=int)

			if choice == 1:
				self.option_1_create_user() 
				
			if choice == 2:
				self.option_2_delete_user()

			if choice == 3:
				self.option_3_query_all_user_data()

			if choice == 4:
				self.option_4_create_new_habit()

			if choice == 5:
				self.option_5_get_all_habits()

			if choice == 6:
				self.option_6_delete_a_habit()

			if choice == 7:
				self.option_7_list_all_goals_with_habits()

			if choice == 8:
				self.option_8_complete_habit()

			if choice == 9:
				self.option_9_longest_streak()
			
			if choice == 10:
				self.option_10_same_habit_periodicity()

			if choice == 11:
				self.option_11_get_currently_tracked_habits()

			if choice == 12:
				self.option_12_get_longest_ever_streak_for_habit()

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
	
	cli = CLI(controller=habit_controller)
	cli.run()

if __name__ == '__main__':
	main()