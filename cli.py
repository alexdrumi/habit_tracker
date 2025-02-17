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


def signal_handler(sig, frame):
	print('You pressed Ctrl+C, doei!')
	sys.exit(0)


# def display_menu():
# 	click.echo("\nMain menu:")
# 	click.echo("1, Create a new user")
# 	click.echo("2, Delete a user")
# 	click.echo("3, Get all user info")
# 	click.echo("4, Get users with already existing habits")
# 	click.echo("5, Create a habit for a certain user")
# 	click.echo("6, List all habits")
# 	click.echo("7, Delete a certain habit")


# def print_users(all_users):
# 	for user in all_users:
# 		print(f"user_id: {user[0]}, user_name: {user[1]}")

# def print_habits(habits):
# 	for habit in habits:
# 		print(f"\nhabit_id: {habit[0]}, habit_user_id: {habit[3]}, habit_name: {habit[1]}, habit_action: {habit[2]}, ")
# 	# habit_id, habit_name, habit_action, habit_user_id

# def print_users_and_habits(users_and_habits):
# 	for data in users_and_habits:
# 		print(f"\nuser_name: {data[0]}, user_id: {data[1]}, habit_id: {data[2]}, habit_name: {data[3]}")


# def option_1_create_user():
# 	click.echo("You selected option 1 - create a user. ")
# 	click.pause()
# 	user_name =  click.prompt("Enter user name:")
# 	user_password = click.prompt("Enter a user password:")
# 	user_age =  click.prompt("Enter user age:")
# 	user_gender = click.prompt("Enter user gender:")
# 	user_role = click.prompt("Enter user role:")

# 	return (user_name, user_password, user_age, user_gender, user_role)


# def option_2_delete_user(all_users: dict):
# 	if len(all_users) == 0:
# 		print("No users are found yet. Be the first one to create one!")
# 		return
# 	click.echo("You selected option 2 - delete a user. ")
# 	click.pause()

# 	print_users(all_users)

# 	user_id =  click.prompt("Enter user id:")
# 	return user_id


# def option_3_get_all_user_info(all_users: dict):
# 	if len(all_users) == 0:
# 		print("No users are found yet. Be the first one to create one!")
# 		return
	
# 	click.echo("You selected option 3 - get all user info.")
# 	print_users()


# def option_4_get_users_with_habits(all_users: dict):
# 	if len(all_users) == 0:
# 		print("No users are found yet. Be the first one to create one!")
# 		return
	
# 	click.echo("You selected option 4 - Get users with already existing habits")
# 	print_users_and_habits()



# def option_5_create_a_habit():
# 	#habit_name, habit_action, habit_streak, habit_periodicity_type, habit_periodicity_value, habit_user):
# 	click.pause()
# 	while True:
# 		habit_name =  click.prompt("Enter a habit name:", type=str)
# 		habit_action = click.prompt("Enter a habit action:", type=str)
# 		user_id =  click.prompt("Enter the user_id of the user whos habit you want to create", type=str)
# 		habit_periodicity_type = click.prompt("Enter the periodicity of the habit e.g.: 'DAILY' or 'WEEKLY':", type=str)
# 		if not user_id.isdigit(): #make sure its an int, otherwise keep prompting
# 			click.echo("Invalid input. Please enter a valid user ID, an integer.")
# 		else:
# 			return (habit_name, habit_action, int(user_id), habit_periodicity_type)


# def option_6_list_habits(all_habits):
# 	click.pause()
# 	print_habits(all_habits)
# 	# habit_id, habit_name, habit_action, habit_user_id

# def option_7_delete_a_habit():
# 	while True:
# 		user_input = click.prompt("Enter the habit ID to delete", type=str) #take a string always

# 		if user_input.isdigit(): #make sure its an int, otherwise keep prompting
# 			return int(user_input)
# 		else:
# 			click.echo("Invalid input. Please enter a valid habit ID, an integer.")


# def handle__exceptions(f):
# 	'''A decorator for handling exceptions on the top layer.'''
# 	def exception_wrapper(*args, **kwargs):
# 		while True:
# 			try: #all functions, create, delete etc wil be wrapped in this try block, not sure how to pass already exist error username or id
# 				return f(*args, **kwargs)
# 			except UserRepositoryError as rerror:
# 				click.echo(f"Invalid input: {rerror}. Will prompt you again.")
# 			except Exception as error:
# 				click.echo(f"Invalid input: {error}. Will prompt you again.")
# 			except ValueError as error:
# 				click.echo(f"Invalid input: {error}. Will prompt you again.")
# 			except HabitNotFoundError as error:
# 					click.echo(f"Invalid input: {error}. Will prompt you again.")
# 	return exception_wrapper



# def option_1_create_user():
# 	click.echo("You selected option 1 - create a user. ")
# 	click.pause()
# 	user_name =  click.prompt("Enter user name:")
# 	user_password = click.prompt("Enter a user password:")
# 	user_age =  click.prompt("Enter user age:")
# 	user_gender = click.prompt("Enter user gender:")
# 	user_role = click.prompt("Enter user role:")

# 	return (user_name, user_password, user_age, user_gender, user_role)



# @handle__exceptions
# def main():
# 	database = MariadbConnection()
# 	user_repository = UserRepository(database)
# 	user_service = UserService(user_repository)
# 	habit_repository = HabitRepository(database, user_repository)
# 	habit_service = HabitService(habit_repository)
	
# 	signal.signal(signal.SIGINT, signal_handler)

# 	while True:
# 		display_menu()
# 		choice = click.prompt("\nEnter your choice", type=int)

# 		if choice == 1:
# 			user_input = option_1_create_user()
# 			user = user_service.create_a_user(user_input[0], user_input[1], user_input[2], user_input[3], user_input[4])
# 			print(user)

# 		if choice == 2:
# 			all_users = user_service.query_all_user_data()
# 			user_id = option_2_delete_user(all_users)
# 			print(user_id)
# 			deleted_user = user_service.delete_user(int(user_input))
# 			if deleted_user:
# 				print(f"user with id {user_id} is deleted.")
# 			else:
# 				print(f"user with id {user_id} is not found.")

# 		if choice == 3:
# 			all_users = user_service.query_all_user_data()
# 			print_users(all_users)
# 			click.pause()
		
# 		if choice == 4:
# 			all_users_and_related_habits = user_service.quary_user_and_related_habits()
# 			print_users_and_habits(all_users_and_related_habits)
# 			click.pause()
		
# 		if choice == 5:
# 			click.echo("You selected option 5 - create a habit for a certain user.\n")
# 			habit_input = option_5_create_a_habit()

# 			#CHECK IF HABIT INPUT 2 IS INT
# 			validated_user_id = user_service.validate_user_by_id(habit_input[2])
# 			print(validated_user_id)
# 			habit = habit_service.create_a_habit(habit_name=habit_input[0], habit_action=habit_input[1], habit_periodicity_type=habit_input[3], habit_user_id=validated_user_id)
# 			print(habit)
# 			click.pause()

# 			#habit_name, habit_action, user_id, habit_periodicity_type)

# 		if choice == 6:
# 			click.echo("You selected option 6 - list all habits.")
# 			all_habits = habit_service.get_all_habits()
# 			print_habits(all_habits)
# 			click.pause()

# 		if choice == 7:
# 			click.echo("You selected option 7 - delete a habit.")
# 			# all_habits = habit_service.get_all_habits()
# 			# print_habits(all_habits)
# 			selected_habit_id = option_7_delete_a_habit()
# 			print(f"{selected_habit_id} is the selected id with type: {type(selected_habit_id)}")
# 			deleted_amount = habit_service.delete_a_habit_by_id(selected_habit_id)
# 			print(deleted_amount)
# 			click.pause()

		#get a list of all users with their related ids and habit ids?


		# if choice == 2:
		# 	user_input = option_1_create_user()
		# 	user = user_service.create_a_user(user_input[0], user_input[1], user_input[2], user_input[3], user_input[4])
		# 	print(user)
		



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

	def display_menu(self):
		click.echo("\nMain menu:")
		click.echo("1, Create a new user")
		click.echo("2, Delete a user")
		click.echo("3, Get all user info")
		click.echo("4, Get users with already existing habits")
		click.echo("5, Create a habit for a certain user")
		click.echo("6, List all habits")
		click.echo("7, Delete a certain habit")


	def option_1_create_user(self):
		click.echo("You selected option 1 - create a user. ")
		click.pause()

		user_name =  click.prompt("Enter user name:")
		user_age =  click.prompt("Enter user age:")
		user_gender = click.prompt("Enter user gender:")
		user_role = click.prompt("Enter user role:")

		user = self._facade.create_user(user_name, user_age, user_gender, user_role)
		print(f"The following user has been created:\n{user}")

	def option_2_delete_user(self, all_users: dict):
		if len(all_users) == 0:
			print("No users are found yet. Be the first one to create one!")
			return
		
		click.echo("You selected option 2 - delete a user. ")
		click.pause()

		self.print_users(all_users)

		user_id =  click.prompt("Enter user id:")
		self._facade.delete_user(int(user_id)) #we could check for row count but it will throw an error anyway
		print(f"User with id: {user_id} is deleted.")


	def option_3_query_all_user_data(self):
		click.echo("You selected option 3 - get all user info. ")
		click.pause()

		all_users = self._facade.query_all_user_data()
		self.print_users(all_users)

	def option_4_get_users_with_habits(self):
		click.echo("You selected option 4 - Get users with already existing habits")
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


def main():
	database = MariadbConnection()
	user_repository = UserRepository(database)
	user_service = UserService(user_repository)
	habit_repository = HabitRepository(database, user_repository)
	habit_service = HabitService(habit_repository)

	habit_tracker_facade = HabitTrackerFacadeImpl(user_service=user_service, habit_service=habit_service)
	cli = CLI(habit_tracker_facade=habit_tracker_facade)
	cli.run()

if __name__ == '__main__':
	main()