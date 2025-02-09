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
	click.echo("2, Log in with existing user")

def option_1_create_user():
	click.echo("You selected option 1 - create a user. ")
	click.pause()
	user_name =  click.prompt("Enter user name:")
	user_password = click.prompt("Enter a user password:")
	user_age =  click.prompt("Enter user age:")
	user_gender = click.prompt("Enter user gender:")
	user_role = click.prompt("Enter user role:")
	return (user_name, user_password, user_age, user_gender, user_role)



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
	signal.signal(signal.SIGINT, signal_handler)

	while True:
		display_menu()

		choice = click.prompt("Enter your choice", type=int)

		if choice == 1:
			user_input = option_1_create_user()
			user = user_service.create_a_user(user_input[0], user_input[1], user_input[2], user_input[3], user_input[4])
			print(user)
		
		# if choice == 2:
		# 	user_input = option_1_create_user()
		# 	user = user_service.create_a_user(user_input[0], user_input[1], user_input[2], user_input[3], user_input[4])
		# 	print(user)
		
			

if __name__ == '__main__':
	main()