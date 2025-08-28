import pytest
from django.db.utils import DataError
from apps.habits.models import Habits
from apps.users.models import AppUsers, AppUsersRoles
from apps.kvi_types.models import KviTypes


@pytest.fixture
def setup_roles():
	'''Fixtures are how we prepare for a certain test, here setup the AppUsersRoles'''
	AppUsersRoles.objects.all().delete()
	
	roles = ['user', 'admin', 'bot']
	for role in roles:
		AppUsersRoles.objects.create(user_role=role)
	return roles



@pytest.fixture
def setup_user(setup_roles):
	'''Fixture to create a standard user.'''
	AppUsersRoles.objects.all().delete()
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
		kvi_multiplier = 1.5
	)
	return test_kvi_type