import pytest
from django.db.utils import DataError
from apps.kvi_types.models import KviTypes
from django.core.exceptions import ValidationError

@pytest.mark.django_db
def test_create_valid_kvi_types():
	'''Test for creating a valid kvi type'''

	kvi_type = KviTypes.objects.create(
		kvi_type_name = 'mood',
		kvi_description = "Will track the quality of my mood.",
		kvi_multiplier = 1.5
	)
	

	assert kvi_type.kvi_type_name == 'mood'
	assert kvi_type.kvi_description == "Will track the quality of my mood."
	assert kvi_type.kvi_multiplier == 1.5



@pytest.mark.django_db
def test_create_too_long_kvi_type_name():
	'''Test for creating a kvi with too long kvi type name'''

	too_long_name = 21 * "x"
	with pytest.raises(DataError):
		kvi_type = KviTypes.objects.create(
			kvi_type_name = too_long_name,
			kvi_description = "Will track the quality of my mood.",
			kvi_multiplier = 1.5
		)
	


@pytest.mark.django_db
def test_create_too_short_kvi_type_name():
	'''Test for creating a kvi with too short kvi type name'''
	too_short_name = 0 * "x"
	with pytest.raises(ValueError):
		kvi_type = KviTypes.objects.create(
			kvi_type_name =	too_short_name,
			kvi_description = "Will track the quality of my mood.",
			kvi_multiplier = 1.5
		)



@pytest.mark.django_db
def test_create_too_high_kvi_multiplier():
	'''Test for creating a too hight kvi multiplier'''
	kvi_type = KviTypes.objects.create(
				kvi_type_name = 'mood',
				kvi_description = "Will track the quality of my mood.",
				kvi_multiplier = 50.0
			)
	with pytest.raises(ValidationError):
		kvi_type.full_clean()



@pytest.mark.django_db
def test_create_too_low_kvi_multiplier():
	'''Test for creating a too long kvi multiplier'''
	kvi_type = KviTypes.objects.create(
				kvi_type_name = 'mood',
				kvi_description = "Will track the quality of my mood.",
				kvi_multiplier = -1.0
			)
	with pytest.raises(ValidationError):
		kvi_type.full_clean()