#https://www.geeksforgeeks.org/conftest-in-pytest/
#https://pytest-with-eric.com/pytest-best-practices/pytest-conftest/#Defining-Pytest-Fixtures-using-conftest-py

import pytest
from django.db.utils import DataError
from apps.habits.models import Habits
from apps.users.models import AppUsers, AppUsersRoles
from apps.kvi_types.models import KviTypes
from apps.goals.models import Goals

@pytest.fixture
def setup_roles():
	'''Fixtures are how we prepare for a certain test, here setup the AppUsersRoles'''
	AppUsersRoles.objects.all().delete() #clear test results from before
	
	roles = ['user', 'admin', 'bot']
	for role in roles:
		AppUsersRoles.objects.create(user_role=role)
	return roles



@pytest.fixture
def setup_user(setup_roles):
	'''Fixture to create a standard user.'''
	AppUsersRoles.objects.all().delete() #clear test results from before
	test_user_role = AppUsersRoles.objects.create(user_role="user")
	test_user = AppUsers.objects.create(
		user_name = "test_user_1",
		user_role = test_user_role,
		user_age = 22,
		user_gender = "male",
	)
	return test_user



@pytest.fixture
def setup_habit(setup_user):
	'''Fixture to create a standard habit.'''
	test_habit = Habits.objects.create(
		habit_name = 'test_habit_1',
		habit_user = setup_user,
		habit_action = 'cleaning laundry',
		habit_streak = 0,
		habit_periodicity_type = 'weekly',
		habit_periodicity_value = None,
	)
	return test_habit



@pytest.fixture
def setup_kvi_type():
	test_kvi_type = KviTypes.objects.create(
		kvi_type_name = 'mood',
		kvi_description = "Will track the quality of my mood.",
		kvi_multiplier = 1.5 #how much will it effect the daily stats. Eg: steps = 1.0, mood = 1.6. Mood would have more weight for calculating how succesful a day was.
	)
	return test_kvi_type


#cant i just import another fixture from goals/tests folder etc? this seems repetitive
@pytest.fixture
def setup_goal(setup_habit, setup_kvi_type):
	'''Test for creating a valid goal.'''
	test_goals = Goals.objects.create(
		goal_name = "test_goal_1",
		habit_id = setup_habit,
		kvi_type_id = setup_kvi_type,
		target_kvi_value = 7.0,
		current_kvi_value = 0.0,
		goal_description = 'Amount of steps (target kvi value) to complete for a weekly step goal.'
	)
	return test_goals
