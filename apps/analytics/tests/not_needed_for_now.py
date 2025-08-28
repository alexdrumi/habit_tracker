import pytest
from apps.habits.models import Habits
from apps.analytics.models import Analytics
from django.db import IntegrityError

@pytest.mark.django_db
def test_create_valid_analytics(setup_habit):
	'''Test for creating valid analytics.'''
	test_analytics = Analytics.objects.create(
		habit_id=setup_habit,
	)

	assert test_analytics.habit_id == setup_habit


@pytest.mark.django_db
def test_create_different_analytics_for_same_habit(setup_habit):
	'''Test for creating double analytics for the same habit.'''
	test_analytics = Analytics.objects.create(
		habit_id=setup_habit,
	)
	with pytest.raises(IntegrityError):
		test_analytics2 = Analytics.objects.create(
			habit_id=setup_habit,
		)


@pytest.mark.django_db
def test_create_different_analytics_for_same_habit(setup_habit):
	'''Test for creating double analytics for the same habit.'''
	test_analytics = Analytics.objects.create(
		habit_id=setup_habit,
	)
	with pytest.raises(IntegrityError):
		test_analytics2 = Analytics.objects.create(
			habit_id=setup_habit,
		)




@pytest.mark.django_db
@pytest.mark.parametrize(
	"test_streak_len, error_raised",
	[
		(-1, True),
		(1e309, True),
		(-1e309, True),
	]
)
def test_invalid_streak(setup_habit, test_streak_len, error_raised):
	'''Test for trying invalid streak values.'''
	if error_raised == True:
		with pytest.raises(ValueError) as error:
			test_analytics = Analytics.objects.create(
				habit_id=setup_habit,
				streak_length = test_streak_len
			)





@pytest.mark.django_db
@pytest.mark.parametrize(
	"test_times_completed, error_raised",
	[
		(-1, True),
		(366, True),
		(-1e309, True),
		(1e309, True),
	]
)
def test_invalid_times_completed(setup_habit, test_times_completed, error_raised):
	if error_raised == True:
		with pytest.raises(ValueError) as error:
			test_analytics = Analytics.objects.create(
				habit_id=setup_habit,
				streak_length = test_times_completed
			)