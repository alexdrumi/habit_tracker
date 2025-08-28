import pytest
from django.db.utils import DataError
from django.core.exceptions import ValidationError
from django.db import IntegrityError
from apps.habits.models import Habits
from apps.users.models import AppUsers, AppUsersRoles
from apps.goals.models import Goals
from apps.kvi_types.models import KviTypes


@pytest.mark.django_db
def test_create_valid_goal(setup_habit, setup_kvi_type):
	'''Test for creating a valid goal.'''
	test_goals = Goals.objects.create(
		goal_name = "test_goal_1",
		habit_id = setup_habit,
		kvi_type_id = setup_kvi_type,
		target_kvi_value = 7.0,
		current_kvi_value = 0.0,
		goal_description = 'Amount of steps (target kvi value) to complete for a weekly step goal.'
	)

	assert test_goals.goal_name == "test_goal_1"
	assert test_goals.habit_id == setup_habit
	assert test_goals.kvi_type_id == setup_kvi_type
	assert test_goals.target_kvi_value == 7.0
	assert test_goals.current_kvi_value == 0.0
	assert test_goals.goal_description == 'Amount of steps (target kvi value) to complete for a weekly step goal.'



@pytest.mark.django_db
@pytest.mark.parametrize(
	"target_kvi_val, expected_message, error_raised",
	[
		(-1.0, "Invalid KVI value.", True),
		(-0.01, "Invalid KVI value.", True),
		(1e309, "Invalid KVI value.", True),
		(-1e309, "Invalid KVI value.", True),
	]
)
def test_create_too_high_kvi_value(setup_habit, setup_kvi_type, target_kvi_val, expected_message, error_raised):
	'''Test for trying multiple KVI target values.'''
	if error_raised == True:
		with pytest.raises(ValueError) as error:
			test_goals = Goals.objects.create(
				goal_name = "test_goal_1",
				habit_id = setup_habit,
				kvi_type_id = setup_kvi_type,
				target_kvi_value = target_kvi_val,
				current_kvi_value = 0.0,
				goal_description = "Amount of steps (target kvi value) to complete for a weekly step goal."
			)
		assert expected_message == str(error.value)



@pytest.mark.django_db
@pytest.mark.parametrize(
	"goal_name, expected_message, error_raised",
	[
		("", "Goal name can not be empty or whitespace.", True),
		(" ", "Goal name can not be empty or whitespace.", True),
		("\t", "Goal name can not be empty or whitespace.", True),
		("\v", "Goal name can not be empty or whitespace.", True),
	]
)
def test_create_empty_goal_name(setup_habit, setup_kvi_type, goal_name, expected_message, error_raised):
	'''Test for trying multiple KVI target values.'''
	if error_raised == True:
		with pytest.raises(ValueError) as error:
			test_goals = Goals.objects.create(
				goal_name = goal_name,
				habit_id = setup_habit,
				kvi_type_id = setup_kvi_type,
				target_kvi_value = 7.0,
				current_kvi_value = 0.0,
				goal_description = "Amount of steps (target kvi value) to complete for a weekly step goal."
			)
		assert expected_message == str(error.value)



@pytest.mark.django_db
def test_for_unique_goal_name_for_a_habit(setup_habit, setup_kvi_type):
	original_goal = Goals.objects.create(
		goal_name = "original_goal",
		habit_id = setup_habit,
		kvi_type_id = setup_kvi_type,
		target_kvi_value = 7.0,
		current_kvi_value = 0.0,
		goal_description = "Amount of steps (target kvi value) to complete for a weekly step goal."
	)
	with pytest.raises(IntegrityError) as error:
		test_goals = Goals.objects.create(
			goal_name = "original_goal",
			habit_id = setup_habit,
			kvi_type_id = setup_kvi_type,
			target_kvi_value = 7.0,
			current_kvi_value = 0.0,
			goal_description = "Amount of steps (target kvi value) to complete for a weekly step goal."
		)
	assert "unique_goal_for_habit_id" in str(error.value)