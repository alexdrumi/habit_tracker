import pytest
from django.db.utils import DataError
from apps.users.models import AppUsers, AppUsersRoles

#https://docs.pytest.org/en/6.2.x/fixture.html
@pytest.fixture
def setup_roles():
	'''Fixtures are how we prepare for a certain test, here setup the AppUsersRoles'''
	AppUsersRoles.objects.all().delete() #clear test results from before
	
	roles = ['user', 'admin', 'bot']
	for role in roles:
		AppUsersRoles.objects.create(user_role=role)
	return roles


@pytest.mark.django_db
def test_create_valid_user_role(setup_roles):
	'''Test for creating a valid user'''
	AppUsersRoles.objects.all().delete() #clear test results from before

	user_role = AppUsersRoles.objects.create(user_role="user")
	user = AppUsers.objects.create(
		user_name="test_user_1",
		user_role=user_role,
		user_age=35,
		user_gender="male",
	)

	assert user.user_name == "test_user_1"
	assert user.user_role.user_role == "user"
	assert user.user_age == 35
	assert user.user_gender == "male"



@pytest.mark.django_db
def test_create_invalid_user_role(setup_roles):
	'''Test for creating an invalid user'''
	with pytest.raises(Exception):
		AppUsersRoles.objects.create(user_role="invalid")



@pytest.mark.django_db
def test_create_too_short_user_name(setup_roles):
	'''Test for creating a valid user'''
	# AppUsersRoles.objects.all().delete() #clear test results from before, if we are using get_or_create, this is not needed.
	user_role, some_bool = AppUsersRoles.objects.get_or_create(user_role="user")
	too_short_name = "a" * 0
	with pytest.raises(ValueError):
		user = AppUsers.objects.create(
			user_name=too_short_name,
			user_role=user_role,
			user_age=35,
			user_gender="male",
		)




@pytest.mark.django_db
def test_create_too_long_user_name(setup_roles):
	'''Test for creating a valid user'''
	# AppUsersRoles.objects.all().delete() #clear test results from before, if we are using get_or_create, this is not needed.
	user_role, some_bool = AppUsersRoles.objects.get_or_create(user_role="user")
	too_long_name = "a" * 101
	with pytest.raises(DataError):
		user = AppUsers.objects.create(
			user_name=too_long_name,
			user_role=user_role,
			user_age=35,
			user_gender="male",
		)


"""next: test querying users by their role using related_name"""