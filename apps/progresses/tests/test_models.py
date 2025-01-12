import pytest
from django.db.utils import DataError
from django.core.exceptions import ValidationError
from django.db import IntegrityError
from apps.habits.models import Habits
from apps.users.models import AppUsers, AppUsersRoles
from apps.goals.models import Goals
from apps.kvi_types.models import KviTypes
from apps.progresses.models import Progresses
from datetime import date, timedelta


@pytest.mark.django_db
def test_for_valid_progress(setup_goal):
	'''Test for creating a valid progress.'''
	test_progress = Progresses.objects.create(
		goal_id = setup_goal,
		current_kvi_value = 1.1,
		progress_description = "Current progress for test_goal"
	)

	assert test_progress.goal_id == setup_goal
	assert test_progress.current_kvi_value == 1.1
	assert test_progress.progress_description ==  "Current progress for test_goal"


@pytest.mark.django_db
@pytest.mark.parametrize(
	"invalid_kvi_val, expected_mesage, error_raised",
	[
		(-1.0, "Invalid KVI value.", True),
		(-0.01, "Invalid KVI value.", True),
		(-1e309, "Invalid KVI value.", True),
	]
)
def test_for_invalid_current_kvi(setup_goal, invalid_kvi_val, expected_mesage, error_raised):
	'''Test for creating an invalid current_kvi value progress.'''
	if error_raised == True:
		with pytest.raises(ValueError) as error:
			test_progress = Progresses.objects.create(
				goal_id = setup_goal,
				current_kvi_value = invalid_kvi_val,
				progress_description = "Current progress for test_goal"
			)
		assert expected_mesage == str(error.value)



@pytest.mark.django_db
@pytest.mark.parametrize(
	"valid_kvi_val, error_raised",
	[
		(0.1,False),
		(1.1, False),
		(15, False),
	]
)
def test_for_valid_current_kvi(setup_goal, valid_kvi_val, error_raised):
	'''Test for creating a valid progress.'''
	if error_raised == False:
		test_progress = Progresses.objects.create(
			goal_id = setup_goal,
			current_kvi_value = valid_kvi_val,
			progress_description = "Current progress for test_goal"
		)
	assert test_progress.current_kvi_value == valid_kvi_val


'''
TODO:
#max len progress descrioption
#relationship tests with goal

'''