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
from apps.habits.repositories.habit_repository import HabitRepository
from apps.habits.services.habit_service import HabitService

def signal_handler(sig, frame):
	print('You pressed Ctrl+C, doei!')
	sys.exit(0)


def display_menu():
	click.echo("Main menu:")
	click.echo("1, Create a new user")
	click.echo("2, Delete a user")
	click.echo("3, Get all user info")
	click.echo("4, Get users with already existing habits")
	click.echo("5, Create a habit for a certain user.")


def print_users(all_users):
	for user in all_users:
		print(f"user_id: {user[0]}, user_name: {user[1]}")


def print_users_and_habits(users_and_habits):
	for data in users_and_habits:
		print(f"user_name: {data[0]}, user_id: {data[1]}, habit_id: {data[2]}, habit_name: {data[3]}")


def option_1_create_user():
	click.echo("You selected option 1 - create a user. ")
	click.pause()
	user_name =  click.prompt("Enter user name:")
	user_password = click.prompt("Enter a user password:")
	user_age =  click.prompt("Enter user age:")
	user_gender = click.prompt("Enter user gender:")
	user_role = click.prompt("Enter user role:")

	return (user_name, user_password, user_age, user_gender, user_role)


def option_2_delete_user(all_users: dict):
	if len(all_users) == 0:
		print("No users are found yet. Be the first one to create one!")
		return
	click.echo("You selected option 2 - delete a user. ")
	click.pause()

	print_users(all_users)

	user_id =  click.prompt("Enter user id:")
	return user_id


def option_3_get_all_user_info(all_users: dict):
	if len(all_users) == 0:
		print("No users are found yet. Be the first one to create one!")
		return
	
	click.echo("You selected option 3 - get all user info.")
	print_users()


def option_4_get_users_with_habits(all_users: dict):
	if len(all_users) == 0:
		print("No users are found yet. Be the first one to create one!")
		return
	
	click.echo("You selected option 4 - Get users with already existing habits")
	print_users_and_habits()



def option_5_create_a_habit():
	#habit_name, habit_action, habit_streak, habit_periodicity_type, habit_periodicity_value, habit_user):
	click.pause()
	habit_name =  click.prompt("Enter a habit name:")
	habit_action = click.prompt("Enter a habit action:")
	user_id =  click.prompt("Enter the user_id of the user whos habit you want to create")
	habit_periodicity_type = click.prompt("Enter the periodicity of the habit e.g.: 'DAILY' or 'WEEKLY':")

	#MAYBE WE COULD DO A VALIDATION HERE, EVERY TIME THERE IS A PROMPT? INSTEAD OF OUTSIDE. JUST
	#TRIGGER THE CLICK AGAIN FOR VALID INPUT

	return (habit_name, habit_action, user_id, habit_periodicity_type)


def handle__exceptions(f):
	'''A decorator for handling exceptions on the top layer.'''
	def exception_wrapper(*args, **kwargs):
		while True:
			try: #all functions, create, delete etc wil be wrapped in this try block, not sure how to pass already exist error username or id
				return f(*args, **kwargs)
			except UserRepositoryError as rerror:
				click.echo(f"Invalid input: {rerror}. Will prompt you again.")
			except Exception as error:
				click.echo(f"Invalid input: {rerror}. Will prompt you again.")
			except ValueError as error:
				click.echo(f"Invalid input: {rerror}. Will prompt you again.")
	return exception_wrapper



@handle__exceptions
def main():
	database = MariadbConnection()
	user_repository = UserRepository(database)
	user_service = UserService(user_repository)
	habit_repository = HabitRepository(database, user_repository)
	habit_service = HabitService(habit_repository)
	
	signal.signal(signal.SIGINT, signal_handler)

	while True:
		display_menu()
		choice = click.prompt("\nEnter your choice", type=int)

		if choice == 1:
			user_input = option_1_create_user()
			user = user_service.create_a_user(user_input[0], user_input[1], user_input[2], user_input[3], user_input[4])
			print(user)

		if choice == 2:
			all_users = user_service.query_all_user_data()
			user_id = option_2_delete_user(all_users)
			print(user_id)
			deleted_user = user_service.delete_user(int(user_input))
			if deleted_user:
				print(f"user with id {user_id} is deleted.")
			else:
				print(f"user with id {user_id} is not found.")

		if choice == 3:
			all_users = user_service.query_all_user_data()
			print_users(all_users)
			click.pause()
		
		if choice == 4:
			all_users_and_related_habits = user_service.quary_user_and_related_habits()
			print_users_and_habits(all_users_and_related_habits)
			click.pause()
		
		if choice == 5:
			click.echo("You selected option 5 - create a habit for a certain user.")
			habit_input = option_5_create_a_habit()

			#CHECK IF HABIT INPUT 2 IS INT
			validated_user_id = user_service.validate_user_by_id(habit_input[2])
			print(validated_user_id)
			habit = habit_service.create_a_habit(habit_name=habit_input[0], habit_action=habit_input[1], habit_periodicity_type=habit_input[3], habit_user_id=validated_user_id)
			print(habit)
			#habit_name, habit_action, user_id, habit_periodicity_type)





		#get a list of all users with their related ids and habit ids?


		# if choice == 2:
		# 	user_input = option_1_create_user()
		# 	user = user_service.create_a_user(user_input[0], user_input[1], user_input[2], user_input[3], user_input[4])
		# 	print(user)
		
			

if __name__ == '__main__':
	main()