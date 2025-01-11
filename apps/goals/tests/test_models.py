import pytest
from django.db.utils import DataError
from apps.habits.models import Habits
from apps.users.models import AppUsers, AppUsersRoles
from apps.goals.models import Goals


# @pytest.fixture
def setup_roles():
	'''Fixtures are how we prepare for a certain test, here setup the AppUsersRoles'''
	AppUsersRoles.objects.all().delete() #clear test results from before
	
	roles = ['user', 'admin', 'bot']
	for role in roles:
		AppUsersRoles.objects.create(user_role=role)
	return roles




@pytest.mark.django_db
def test_create_valid_goal(setup_roles):
	'''Test for creating a valid goal'''
	test_user_role = AppUsersRoles.objects.create(user_role="user")
	test_user = AppUsers.objects.create(
		user_name = "test_user_1",
		user_role = test_user_role,
		user_age = 22,
		user_gender = "male",
	)

	test_habit = Habits.objects.create(
		habit_name = 'test_habit_1',
		habit_user = test_user,
		habit_action = 'cleaning laundry',
		habit_streak = 0,
		habit_periodicity_type = 'weekly',
		habit_periodicity_value = None,
	)

	goals = Goals.objects.create(
		goal_name = "test_goal_1"
		habit_id = test_habit.habit_id,
	)