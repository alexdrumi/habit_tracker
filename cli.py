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

from apps.core.controllers.habit_controller import HabitController

def signal_handler(sig, frame):
	click.echo(click.style('\nYou pressed Ctrl+C, doei...', fg='red', bold=True))
	sys.exit(0)


class CLI:
	def __init__(self, controller: HabitController):
		self._controller = controller

	def display_users(self, all_users):
		click.echo(click.style("\n---ALL USERS---", fg="cyan", bold=True))
		
		if not all_users:
			click.echo("No users found.")
			return

		for user in all_users:
			click.echo(f" - user_id: {user[0]}, user_name: {user[1]}")



	def display_habits(self, habits):
		click.echo(click.style("\n---LIST OF ALL HABITS---", fg="cyan", bold=True))

		if len(habits) == 0:
			print(click.style("There are currently no habits tracked. Create a first one!", fg="green", bold=True))
			return

		print("\n" + "-" * 80)
		print(click.style(f"{'Habit ID':<10} {'User ID':<10} {'Habit Name':<20} {'Action':<30}", fg="green", bold=True))
		print("-" * 80)

		#pretty display
		for habit in habits:
			print(
				click.style(f"{habit[0]:<10}", fg="yellow", bold=True) +
				click.style(f"{habit[3]:<10}", fg="cyan") +
				click.style(f"{habit[1]:<20}", fg="white", bold=True) +
				click.style(f"{habit[2]:<30}", fg="magenta")
			)

		print("-" * 80)


	#pretty ddisplay ll be needed for thisone as well
	def display_goals_and_habits(self, goals_and_habits):
		click.echo(click.style("\n---GOALS AND THEIR ASSOCIATED HABITS---", fg="cyan", bold=True))

		if not goals_and_habits:
				click.echo("No goals and associated habits have been found.")

		for data in goals_and_habits:
			click.echo(f"\nGoal Name: {click.style(data[0], fg='green', bold=True)}\n"
						f"Goal ID: {data[1]}\n"
						f"Habit Name: {click.style(data[3], fg='yellow', bold=True)}\n"
						f"Habit ID: {data[2]}")

		
	def display_same_periodicity_type_habits(self, habits):
		if not habits:
			click.echo(click.style("No habits found by periodicity grouping.", fg="green", bold=True))
			return
	
		for habit_type in habits:
			periodicity = habit_type[0]  #daily or weekly atm
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


	def display_tickable_habits(self, goals):
		click.echo(click.style("\n---TICKABLE HABITS AND THEIR ASSOCIATED GOALS---", fg="cyan", bold=True))
		if not goals:
			click.echo("No tickable habits found.")
			return

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
			click.echo(
				f"\n{click.style('Habit ID:', fg='yellow', bold=True)} {habit_id}\n"
				f"{click.style('Goal ID:', fg='yellow', bold=True)} {goal_id}\n"
				f"{click.style('Goal Name:', fg='yellow', bold=True)} {goal_name}\n"
				f"{click.style('Target KVI:', fg='yellow', bold=True)} {target_kvi_value}\n"
				f"{click.style('Current KVI:', fg='yellow', bold=True)} {current_kvi_value}\n"
				f"{click.style('Last Ticked:', fg='yellow', bold=True)} {occurence_date_str}\n"
				+ "-" * 80
			)


	def display_tracked_habits(self, habits):
		click.echo(click.style("\n---CURRENTLY TRACKED HABITS (WITH AT LEAST ONE TIME TICKED HABITS)---", fg="cyan", bold=True))
		if not habits:
			click.echo(click.style("\nNo habits are currently being tracked.", fg="red", bold=True))
			return

		click.echo("\n" + "-" * 80)
		click.echo(click.style(" Currently tracked habits ", fg="green", bold=True))
		click.echo("-" * 80)

		for habit in habits:
			habit_id, habit_name, streak, periodicity = habit

			click.echo(
				click.style("Habit ID: ", fg="yellow", bold=True) + 
				click.style(str(habit_id), fg="green") + 
				click.style(" | Habit name: ", fg="yellow", bold=True) + 
				click.style(habit_name, fg="white", bold=True) +
				click.style(" | Streak: ", fg="yellow", bold=True) +
				click.style(str(streak), fg="magenta") +
				click.style(" | Periodicity: ", fg="yellow", bold=True) + 
				click.style(periodicity.capitalize(), fg="blue", bold=True)
			)  

		click.echo("-" * 80)



	def display_menu(self):
		click.echo("\nMain menu:")
		click.echo("1, Create a new user")
		# click.echo("2, Delete a user")
		click.echo("3, Get all user info")
		click.echo("4, Create a habit for a certain user")
		click.echo("5, List all habits")
		# click.echo("6, Delete a certain habit")
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
			click.echo(click.style("Invalid input. Please enter a valid integer.", fg="red", bold=True))

	def prompt_for_choice(self, message, choices):
		while True:
			value = click.prompt(message, type=str).strip()
			if value in choices:
				return value
			click.echo(
				click.style(f"Invalid choice. Please select from: {', '.join(choices)}.", fg="red", bold=True)
			)



	def option_1_create_user(self):
		click.echo(click.style("\n[Option 1] Create a new user", fg="cyan", bold=True))
		click.pause()

		user_name =  click.prompt("Enter user name:")
		user_age =  click.prompt("Enter user age:")
		user_gender = click.prompt("Enter user gender:")
		user_role = click.prompt("Enter user role:")

		#this layer puts the propagated errors from the layers beneath to the CLI 
		try:
			user = self._controller.create_user(user_name, user_age, user_gender, user_role)
			click.echo(click.style("User created successfully:\n", fg="green", bold=True) + str(user))
		except Exception as error:
			click.echo(click.style(f"Error creating user: {error}", fg="red", bold=True))



	# def option_2_delete_user(self):
	# 	click.echo("You selected option 2 - delete a user. ")
	# 	click.pause()

	# 	user_id =  click.prompt("Enter user id:")

	# 	try:
	# 		self._controller.delete_user(int(user_id)) #we could check for row count but it will throw an error anyway
	# 		click.echo(f"User with user_id {user_id} deleted.")
	# 	except Exception as error:
	# 		click.echo(click.style(f"Error deleting user: {error}", fg="red", bold=True))




	def option_3_query_all_user_data(self):
		click.echo(click.style("\n[Option 3] Get all user info", fg="cyan", bold=True))
		click.pause()

		try:
			all_users = self._controller.query_all_users()
			self.display_users(all_users)
		except Exception as error:
			click.echo(click.style(f"Error while querying all user data: {error}", fg="red", bold=True))



	def option_4_create_new_habit(self):
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



	def option_5_get_all_habits(self):
		click.echo(click.style("\n[Option 5] List all habits", fg="cyan", bold=True))
		click.pause()

		try:
			all_habits = self._controller.get_all_habits()
			self.display_habits(all_habits)
		except Exception as error:
			click.echo(click.style(f"Error while querying all habits: {error}", fg="red", bold=True))



	# def option_6_delete_a_habit(self):
	# 	click.echo("You selected option 7 - delete a habit.")
	# 	click.pause()

	# 	habit_id = self.prompt_for_valid_integer("Enter the habit ID to delete.")
	# 	try:
	# 		deleted_amount = self._controller.delete_a_habit(int(habit_id)) #eventually we might change the deletes? As in, should it return the amount of rows it deleted?
	# 		click.echo(f"\nDeleted habit with id {habit_id}")
	# 	except Exception as error:
	# 		click.echo(click.style(f"Error while deleting a habit: {error}", fg="red", bold=True))



	def option_7_list_all_goals_with_habits(self):
		click.echo(click.style("\n[Option 7] List goals with associated habits", fg="cyan", bold=True))
		click.pause()

		try:
			users_and_related_habits = self._controller.query_goals_and_related_habits()
			self.display_goals_and_habits(users_and_related_habits)
		except Exception as error:
			click.echo(click.style(f"Error while listing goals and habits: {error}", fg="red", bold=True))



	def option_8_complete_habit(self):
		click.echo(click.style("\n[Option 8] Complete a habit (tick a goal)", fg="cyan", bold=True))
		click.pause()

		self.option_7_list_all_goals_with_habits() #gotta form this a bit prettier

		try:
			tickable_habits_and_goals = self._controller.fetch_ready_to_tick_goals_of_habits()
			self.display_tickable_habits(tickable_habits_and_goals)
			
			habit_id = self.prompt_for_valid_integer("Enter a habit ID.")
			goal_id = self.prompt_for_valid_integer("Enter a goal ID.")

			self._controller.complete_a_habit(habit_id=int(habit_id), goal_id=int(goal_id))
		except Exception as error:
			click.echo(click.style(f"Error while completing a habit: {error}", fg="red", bold=True))



	def option_9_longest_streak_in_database(self):
		click.echo(click.style("\n[Option 9] Longest Habit Streak in the Database", fg="cyan", bold=True))
		click.pause()

		try:
			result = self._controller.calculate_longest_streak()

			if result:
				#we can style it like this also for the rest
				click.echo(click.style("\nHabit with the longest current streak:", fg="green", bold=True))
				click.echo(click.style(f"  Habit Name: {result[1]}", fg="white"))
				click.echo(click.style(f"  Habit ID: {result[0]}", fg="white"))
				click.echo(click.style(f"  Streak: {result[2]} days", fg="yellow", bold=True))
			else:
				click.echo(click.style("\nNo habits found with streaks yet. Complete a habit first!", fg="red", bold=True))
		except Exception as error:
			click.echo(click.style(f"Error while querying the longest streak: {error}", fg="red", bold=True))


	def option_10_same_habit_periodicity(self):
		click.echo(click.style("\n[Option 10] Group habits by periodicity", fg="cyan", bold=True))
		click.pause()
		
		try:
			result = self._controller.get_same_periodicity_type_habits()
			self.display_same_periodicity_type_habits(result)
		except Exception as error:
			click.echo(click.style(f"Error while grouping habits by periodicity: {error}", fg="red", bold=True))


	def option_11_get_currently_tracked_habits(self):
		click.echo(click.style("\n[Option 11] Get currently tracked habits", fg="cyan", bold=True))
		click.pause()

		try:
			result = self._controller.get_currently_tracked_habits()
			self.display_tracked_habits(result)
		except Exception as error:
			click.echo(click.style(f"Error while querying currently tracked habits: {error}", fg="red", bold=True))



	def option_12_get_longest_ever_streak_for_habit(self):
		click.echo(click.style("\n[Option 12] Get the longest ever streak for a habit", fg="cyan", bold=True))
		click.pause()
		
		try:
			self.option_5_get_all_habits()
			habit_id = self.prompt_for_valid_integer("Select a habit id for its longest ever streak recorded")
			result = self._controller.longest_streak_for_habit(habit_id)
			if result:
				click.echo(click.style(f"Longest streak opf habit {habit_id}: {result[0][6]} days", fg="yellow", bold=True))
			else:
				click.echo(click.style(f"No longest streak for habit {habit_id} yet.", fg="yellow", bold=True))

		except Exception as error:
			click.echo(click.style(f"Error while querying the longest streak ever: {error}", fg="red", bold=True))


	
	def run(self):
		signal.signal(signal.SIGINT, signal_handler)
		self._controller.get_pending_goals()

		while True:
			self.display_menu()
			choice = click.prompt("\nEnter your choice", type=int)

			if choice == 1:
				self.option_1_create_user() 
				
			# if choice == 2:
			# 	self.option_2_delete_user() #WE CANT DELETE USER ATM because of foreign key issues

			if choice == 3:
				self.option_3_query_all_user_data()

			if choice == 4:
				self.option_4_create_new_habit()

			if choice == 5:
				self.option_5_get_all_habits()

			# if choice == 6:
			# 	self.option_6_delete_a_habit()

			if choice == 7:
				self.option_7_list_all_goals_with_habits()

			if choice == 8:
				self.option_8_complete_habit()

			if choice == 9:
				self.option_9_longest_streak_in_database()
			
			if choice == 10:
				self.option_10_same_habit_periodicity()

			if choice == 11:
				self.option_11_get_currently_tracked_habits()

			if choice == 12:
				self.option_12_get_longest_ever_streak_for_habit()
