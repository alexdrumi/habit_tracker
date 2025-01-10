import pytest
from django.db.utils import DataError
from apps.kvi_types.models import KviTypes
from django.core.exceptions import ValidationError

@pytest.mark.django_db
def test_create_valid_kvi_types():
	'''Test for creating a valid kvi type'''
	# AppUsersRoles.objects.all().delete() #clear test results from before

	kvi_type = KviTypes.objects.create(
		kvi_type_name = 'mood',
		kvi_description = "Will track the quality of my mood.",
		kvi_multiplier = 1.5 #how much will it effect the daily stats, steps = 1.0, mood is more important how succesful a day was.
	)
	

	assert kvi_type.kvi_type_name == 'mood'
	assert kvi_type.kvi_description == "Will track the quality of my mood."
	assert kvi_type.kvi_multiplier == 1.5



@pytest.mark.django_db
def test_create_too_long_kvi_type_name():
	'''Test for creating a kvi with too long kvi type name'''
	# AppUsersRoles.objects.all().delete() #clear test results from before

	too_long_name = 21 * "x"
	with pytest.raises(DataError):
		kvi_type = KviTypes.objects.create(
			kvi_type_name = too_long_name,
			kvi_description = "Will track the quality of my mood.",
			kvi_multiplier = 1.5 #how much will it effect the daily stats, steps = 1.0, mood is more important how succesful a day was.
		)
	


@pytest.mark.django_db
def test_create_too_short_kvi_type_name():
	'''Test for creating a kvi with too short kvi type name'''
	# AppUsersRoles.objects.all().delete() #clear test results from before
	too_short_name = 0 * "x"
	with pytest.raises(ValueError):
		kvi_type = KviTypes.objects.create(
			kvi_type_name =	too_short_name,
			kvi_description = "Will track the quality of my mood.",
			kvi_multiplier = 1.5 #how much will it effect the daily stats, steps = 1.0, mood is more important how succesful a day was.
		)



@pytest.mark.django_db
def test_create_too_high_kvi_multiplier():
	'''Test for creating a too hight kvi multiplier'''
	# AppUsersRoles.objects.all().delete() #clear test results from before
	kvi_type = KviTypes.objects.create(
				kvi_type_name = 'mood',
				kvi_description = "Will track the quality of my mood.",
				kvi_multiplier = 50.0 #how much will it effect the daily stats, steps = 1.0, mood is more important how succesful a day was.
			)
	with pytest.raises(ValidationError):
		#eventually we might implement clean as well instead of checking on the save method, that strictly checks whether it could be saved in the SQL via the ORM
		kvi_type.full_clean() #this normally calls clean, but also includes field validation, otherwise this would fail



@pytest.mark.django_db
def test_create_too_low_kvi_multiplier():
	'''Test for creating a too long kvi multiplier'''
	# AppUsersRoles.objects.all().delete() #clear test results from before
	kvi_type = KviTypes.objects.create(
				kvi_type_name = 'mood',
				kvi_description = "Will track the quality of my mood.",
				kvi_multiplier = -1.0 #how much will it effect the daily stats, steps = 1.0, mood is more important how succesful a day was.
			)
	with pytest.raises(ValidationError):
		#eventually we might implement clean as well instead of checking on the save method, that strictly checks whether it could be saved in the SQL via the ORM
		kvi_type.full_clean() #this normally calls clean, but also includes field validation, otherwise this would fail