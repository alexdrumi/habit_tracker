import pytest
from django.db.utils import DataError
from apps.habits.models import Habits
from apps.users.models import AppUsers, AppUsersRoles

@pytest.fixture
def setup_roles():
	'''Fixtures are how we prepare for a certain test, here setup the AppUsersRoles'''
	AppUsersRoles.objects.all().delete() #clear test results from before
	
	roles = ['user', 'admin', 'bot']
	for role in roles:
		AppUsersRoles.objects.create(user_role=role)
	return roles



@pytest.mark.django_db
def test_create_valid_habit(setup_roles):
	AppUsersRoles.objects.all().delete() #clear test results from before
	# AppUsers.objects.all().delete() #before test clear all users? y
	'''Test for creating a habit with valid parameters'''
	test_user_role = AppUsersRoles.objects.create(user_role="user")
	test_user = AppUsers.objects.create(
		user_name = "test_user_1",
		user_role = test_user_role,
		user_age = 22,
		user_gender = "male",
	)

	habit = Habits.objects.create(
		habit_name = 'test_habit_1',
		habit_user = test_user,
		habit_action = 'cleaning laundry',
		habit_streak = 0,
		habit_periodicity_type = 'weekly',
		habit_periodicity_value = None,
	)

	assert habit.habit_name == "test_habit_1"
	assert habit.habit_user == test_user
	assert habit.habit_action == 'cleaning laundry'
	assert habit.habit_periodicity_type == 'weekly'
	assert habit.habit_periodicity_value == 7




@pytest.mark.django_db
def test_create_too_long_habit_name():
	AppUsersRoles.objects.all().delete() #clear test results from before
	# AppUsers.objects.all().delete() #before test clear all users? y
	'''Test for creating a habit with too long habit name'''
	test_user_role = AppUsersRoles.objects.create(user_role="user")
	test_user = AppUsers.objects.create(
		user_name = "test_user_1",
		user_role = test_user_role,
		user_age = 22,
		user_gender = "male",
	)

	too_long_name = 41 * "a"
	with pytest.raises(DataError):
		habit = Habits.objects.create(
			habit_name = too_long_name,
			habit_user = test_user,
			habit_action = 'cleaning laundry',
			habit_streak = 0,
			habit_periodicity_type = 'weekly',
			habit_periodicity_value = None,
		)



@pytest.mark.django_db
def test_create_empty_habit_name():
	AppUsersRoles.objects.all().delete() #clear test results from before
	# AppUsers.objects.all().delete() #before test clear all users? y
	'''Test for creating a habit with empty habit name'''
	test_user_role = AppUsersRoles.objects.create(user_role="user")
	test_user = AppUsers.objects.create(
		user_name = "test_user_1",
		user_role = test_user_role,
		user_age = 22,
		user_gender = "male",
	)

	empty_name =  0 * 'k'
	with pytest.raises(ValueError):
		habit = Habits.objects.create(
			habit_name = empty_name,
			habit_user = test_user,
			habit_action = 'cleaning laundry',
			habit_streak = 0,
			habit_periodicity_type = 'weekly',
			habit_periodicity_value = None,
		)