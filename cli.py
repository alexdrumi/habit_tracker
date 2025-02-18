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

def signal_handler(sig, frame):
	print('You pressed Ctrl+C, doei!')
	sys.exit(0)


class CLI:
	def __init__(self, habit_tracker_facade: HabitTrackerFacadeImpl):
		self._facade = habit_tracker_facade

	def print_users(self, all_users):
		for user in all_users:
			print(f"user_id: {user[0]}, user_name: {user[1]}")

	def print_habits(self, habits):
		for habit in habits:
			print(f"\nhabit_id: {habit[0]}, habit_user_id: {habit[3]}, habit_name: {habit[1]}, habit_action: {habit[2]}, ")

	def print_users_and_habits(self, users_and_habits):
		for data in users_and_habits:
			print(f"\nuser_name: {data[0]}, user_id: {data[1]}, habit_id: {data[2]}, habit_name: {data[3]}")

	def print_goals_and_habits(self, goals_and_habits):
		for data in goals_and_habits:
			print(f"\ngoal_name: {data[0]}, goal_id: {data[1]}, habit_name: {data[3]}, habit_id: {data[2]}")



	def display_menu(self):
		click.echo("\nMain menu:")
		click.echo("1, Create a new user")
		click.echo("2, Delete a user")
		click.echo("3, Get all user info")
		click.echo("4, List users with already existing habits")
		click.echo("5, Create a habit for a certain user")
		click.echo("6, List all habits")
		click.echo("7, Delete a certain habit")
		click.echo("8, Create a certain goal for a habit")
		click.echo("9, List goals with associated habits")
		click.echo("10, Delete goal")


	def option_1_create_user(self):
		click.echo("You selected option 1 - create a user. ")
		click.pause()

		user_name =  click.prompt("Enter user name:")
		user_age =  click.prompt("Enter user age:")
		user_gender = click.prompt("Enter user gender:")
		user_role = click.prompt("Enter user role:")

		user = self._facade.create_user(user_name, user_age, user_gender, user_role)
		print(f"The following user has been created:\n{user}")

	def option_2_delete_user(self):

		click.echo("You selected option 2 - delete a user. ")
		click.pause()


		user_id =  click.prompt("Enter user id:")
		self._facade.delete_user(int(user_id)) #we could check for row count but it will throw an error anyway
		print(f"User with id: {user_id} is deleted.")


	def option_3_query_all_user_data(self):
		click.echo("You selected option 3 - get all user info. ")
		click.pause()

		all_users = self._facade.query_all_user_data()
		self.print_users(all_users)

	def option_4_list_users_with_habits(self):
		click.echo("You selected option 4 - List users with already existing habits")
		click.pause()

		users_and_related_habits = self._facade.query_user_and_related_habits()
		self.print_users_and_habits(users_and_related_habits)

	def option_5_create_new_habit(self):
		click.echo("You selected option 5 - create a habit for a certain user.\n")
		click.echo("You selected option 4 - Get users with already existing habits")
		click.pause()
		while True:
			habit_name =  click.prompt("Enter a habit name:", type=str)
			habit_action = click.prompt("Enter a habit action:", type=str)
			user_id =  click.prompt("Enter the user_id of the user whos habit you want to create", type=str)
			habit_periodicity_type = click.prompt("Enter the periodicity of the habit e.g.: 'DAILY' or 'WEEKLY':", type=str)
			if not user_id.isdigit(): #make sure its an int, otherwise keep prompting
				click.echo("Invalid input. Please enter a valid user ID, an integer.")
			else:
				break 
		new_habit = self._facade.create_a_habit(habit_name, habit_action, habit_periodicity_type, user_id)
		print(f"New habit created:\n{new_habit}")


	def option_6_get_all_habits(self):
		click.echo("You selected option 6 - list all habits.")
		click.pause()
		
		all_habits = self._facade.get_all_habits()
		self.print_habits(all_habits)


	def option_7_delete_a_habit(self):
		click.echo("You selected option 7 - delete a habit.")
		click.pause()

		while True:
			selected_habit_id = click.prompt("Enter the habit ID to delete", type=str) #take a string always

			if selected_habit_id.isdigit(): #make sure its an int, otherwise keep prompting
				break
			else:
				click.echo("Invalid input. Please enter a valid habit ID, an integer.")

		deleted_amount = self._facade.delete_a_habit_by_id(int(selected_habit_id)) 
		print(f"Habit with id: {selected_habit_id} is deleted")


	def option_8_create_a_goal(self):
		click.echo("You selected option 8 - create a goal.")
		click.pause()

		all_habits = self._facade.get_all_habits()
		self.print_habits(all_habits)
		click.pause()

		while True:
			goal_name = click.prompt("Enter a goal name.", type=str)
			goal_description = click.prompt("Enter a description for the goal.", type=str)

			habit_id = click.prompt("Enter the habit ID to use for a goal", type=str)
			target_kvi_value= click.prompt("Enter the target value a goal", type=str)
			if not habit_id.isdigit() or not target_kvi_value.isdigit():
				print("Invalid input for one of the numeric inputs (habit_id, target_kvi_value, current_kvi_value)")
			else:
				break
		
		goal_entity = self._facade.create_a_goal(goal_name=goal_name, habit_id=int(habit_id), target_kvi_value=float(target_kvi_value), current_kvi_value=0.0, goal_description=goal_description)
		print(f"Goal is created: {goal_entity}")


	def option_9_list_all_goals_with_habits(self):
		click.echo("You selected option 9 - List goals with their associated habits")
		click.pause()

		users_and_related_habits = self._facade.query_goals_and_related_habits()
		self.print_goals_and_habits(users_and_related_habits)



	def option_10_delete_goal(self):
		click.echo("You selected option 10 - Delete a goal")
		click.pause()

		goal_id = click.prompt("Enter a goal id.", type=str)

		self._facade.delete_a_goal(int(goal_id))


	def run(self):
		signal.signal(signal.SIGINT, signal_handler)

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
				self.option_4_get_users_with_habits()
			
			if choice == 5:
				self.option_5_create_new_habit()

			if choice == 6:
				self.option_6_get_all_habits()

			if choice == 7:
				self.option_7_delete_a_habit()

			if choice == 8:
				self.option_8_create_a_goal()
			
			if choice == 9:
				self.option_9_list_all_goals_with_habits()

			if choice == 10:
				self.option_10_delete_goal()


def main():
	database = MariadbConnection()
	user_repository = UserRepository(database)
	user_service = UserService(user_repository)
	habit_repository = HabitRepository(database, user_repository)
	habit_service = HabitService(habit_repository)
	goal_repository = GoalRepository(database, habit_repository)
	goal_service = GoalService(goal_repository, habit_service)

	habit_tracker_facade = HabitTrackerFacadeImpl(user_service=user_service, habit_service=habit_service, goal_service=goal_service)
	cli = CLI(habit_tracker_facade=habit_tracker_facade)
	cli.run()

if __name__ == '__main__':
	main()