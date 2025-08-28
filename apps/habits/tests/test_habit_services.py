import pytest
from unittest.mock import MagicMock
from apps.habits.services.habit_service import HabitService
from apps.habits.repositories.habit_repository import HabitNotFoundError, HabitAlreadyExistError

@pytest.fixture
def mock_habit_repository():
	return MagicMock()


@pytest.fixture
def habit_service(mock_habit_repository):
	return HabitService(repository=mock_habit_repository)



def test_create_habit_success(habit_service, mock_habit_repository):
	"""
	Test that create_a_habit returns the repository’s result on success.

	Given:
		- mock_habit_repo.create_a_habit returns a dict with habit data.
	When:
		- habit_service.create_a_habit is called with valid inputs.
	Then:
		- It returns the same dict.
	"""

	expected_result = {
		 'habit_id': 1,
		 'habit_name': "test1",
		 'habit_action': "testing 1",
		 'habit_streak': 0,
		 'habit_periodicity_type': "daily",
		 'habit_user_id': 1,
	}
	mock_habit_repository.create_a_habit.return_value = expected_result
	result = habit_service.create_a_habit("test1", "testing 1", "daily", 1)
	
	mock_habit_repository.create_a_habit.assert_called_with(
		habit_name =  "test1",
		habit_action="testing 1",
		habit_periodicity_type="daily",
		habit_periodicity_value=1,
		habit_user_id = 1,
		habit_streak=0,
	)
	assert result == expected_result



def test_create_habit_with_duplicate_should_raise_error(habit_service, mock_habit_repository):
	"""
	Test that create_a_habit propagates HabitAlreadyExistError on duplicate.

	Given:
		- mock_habit_repo.create_a_habit first returns a success, then raises HabitAlreadyExistError.
	When:
		- habit_service.create_a_habit is called twice with same inputs.
	Then:
		- The second call raises HabitAlreadyExistError.
	"""
	expected_result = {
		'habit_id': 1,
		'habit_action': "testing 1",
		'habit_streak': 0,
		'habit_periodicity_type': "daily",
		'habit_user_id': 1,
	}
	mock_habit_repository.create_a_habit.side_effect = [expected_result, HabitAlreadyExistError("test1", 1)]
	result1 = habit_service.create_a_habit("test1", "testing 1", "daily", 1)
	assert result1 == expected_result

	with pytest.raises(HabitAlreadyExistError) as exc_info:
		habit_service.create_a_habit("test1", "testing 1", "daily", 1)
	assert "Habit 'test1' already exists for user with id: 1" in str(exc_info.value)



def test_create_habit_invalid_periodicity(habit_service):
	"""
	Test that create_a_habit rejects an unknown periodicity type.

	Given:
		- An invalid periodicity type "millenially".
	When:
		- habit_service.create_a_habit is called.
	Then:
		- ValueError is raised.
	"""
	with pytest.raises(ValueError) as exc_info:
		habit_service.create_a_habit("drinking wateh", "drink 2 liters of water", "millenially", 1)
	assert 'Invalid habit periodicity type. Expected one of "DAILY" "WEEKLY" in str(exc_info.value)'



def test_update_habit_streak_success(habit_service, mock_habit_repository):
	"""
	Test that update_habit_streak returns row count on success.

	Given:
		- mock_habit_repo.validate_a_habit returns the same ID.
		- mock_habit_repo.update_habit_field returns 1.
	When:
		- habit_service.update_habit_streak is called with valid inputs.
	Then:
		- It returns 1.
	"""
	mock_habit_repository.validate_a_habit.return_value = 1

	mock_habit_repository.update_habit_field.return_value = 1

	result = habit_service.update_habit_streak(1, 5)
	mock_habit_repository.validate_a_habit.assert_called_with(1)
	mock_habit_repository.update_habit_field.assert_called_with(1, 'habit_streak', 5)
	assert result == 1



def test_update_habit_streak_invalid_value(habit_service):
	"""
	Test that update_habit_streak rejects non-positive streak values.

	Given:
		- updated_streak_value = -1.
	When:
		- habit_service.update_habit_streak is called.
	Then:
		- ValueError is raised.
	"""
	with pytest.raises(ValueError) as exc_info:
		habit_service.update_habit_streak(1, -1)
	assert "Invalid streak value. It must be a positive integer." in str(exc_info.value)



def test_get_habit_id_not_found(habit_service, mock_habit_repository):
	"""
	Test that get_habit_id propagates HabitNotFoundError when the habit is missing.

	Given:
		- mock_habit_repository.get_habit_id raises HabitNotFoundError.
	When:
		- habit_service.get_habit_id is called.
	Then:
		- HabitNotFoundError is raised.
	"""
	mock_habit_repository.get_habit_id.side_effect = HabitNotFoundError("notfound")
	with pytest.raises(HabitNotFoundError):
		habit_service.get_habit_id("firsuser", "notfound")



def test_update_habit_periodicity_type_success(habit_service, mock_habit_repository):
	"""
	Test that update_habit_periodicity_type successfully updates a habit’s periodicity type.

	Given:
		- mock_habit_repository.get_habit_id returns 11.
		- remock_habit_repositorypo.update_habit_field returns 1.
	When:
		- habit_service.update_habit_periodicity_type("kati", "yoga", "weekly") is called.
	Then:
		- It returns 1 and calls the repository correctly.
	"""
	mock_habit_repository.get_habit_id.return_value = 11
	mock_habit_repository.update_habit_field.return_value = 1

	rows = habit_service.update_habit_periodicity_type("kati", "yoga", "weekly")

	mock_habit_repository.get_habit_id.assert_called_with("kati", "yoga")
	mock_habit_repository.update_habit_field.assert_called_with(11, "habit_periodicity_type", "weekly")
	assert rows == 1



def test_update_habit_periodicity_type_invalid_type(habit_service):
	"""
	Test that update_habit_periodicity_type rejects invalid types.

	Given:
		- An invalid type "in millenia".
	When:
		- habit_service.update_habit_periodicity_type is called.
	Then:
		- ValueError is raised.
	"""
	with pytest.raises(ValueError):
		habit_service.update_habit_periodicity_type("gekko", "karlington", "in millenia")



def test_update_habit_periodicity_value_success(habit_service, mock_habit_repository):
	"""
	Test that update_habit_periodicity_value updates numeric periodicity.

	Given:
		- mock_habit_repository.get_habit_id returns 7.
		- mock_habit_repository.update_habit_field returns 1.
	When:
		- svc.update_habit_periodicity_value("mama", "run", 5) is called.
	Then:
		- It returns 1 and calls the repository correctly.
	"""
	mock_habit_repository.get_habit_id.return_value = 7
	mock_habit_repository.update_habit_field.return_value = 1

	rows = habit_service.update_habit_periodicity_value("mama", "run", 5)

	mock_habit_repository.get_habit_id.assert_called_with("mama", "run")
	mock_habit_repository.update_habit_field.assert_called_with(7, "habit_periodicity_value", 5)
	assert rows == 1



def test_update_habit_periodicity_value_invalid(habit_service):
	"""
	Test that update_habit_periodicity_value rejects out-of-range values.

	Given:
		- updated_value = 99.
	When:
		- habit_service.update_habit_periodicity_value is called.
	Then:
		- ValueError is raised.
	"""
	with pytest.raises(ValueError):
		habit_service.update_habit_periodicity_value("alice", "run", 99)



def test_get_current_streak_success(habit_service, mock_habit_repository):
	"""
	Test that get_current_streak returns the correct streak tuple.

	Given:
		- mock_habit_repository.get_current_streak returns (10,).
	When:
		- habit_service.get_current_streak(3) is called.
	Then:
		- It returns (10,).
	"""
	mock_habit_repository.validate_a_habit.return_value = 3
	mock_habit_repository.get_current_streak.return_value = (10,)

	streak = habit_service.get_current_streak(3)

	mock_habit_repository.get_current_streak.assert_called_once_with(habit_id=3)
	assert streak == (10,)



def test_get_current_streak_not_found(habit_service, mock_habit_repository):
	"""
	Test that get_current_streak propagates HabitNotFoundError on missing habit.

	Given:
		- mock_habit_repository.get_current_streak raises HabitNotFoundError.
	When:
		- habit_service.get_current_streak is called.
	Then:
		- HabitNotFoundError is raised.
	"""
	mock_habit_repository.get_current_streak.side_effect = HabitNotFoundError(99)
	with pytest.raises(HabitNotFoundError):
		habit_service.get_current_streak(99)



def test_get_goal_of_habit_success(habit_service, mock_habit_repository):
	"""
	Test that get_goal_of_habit returns list of goal IDs.

	Given:
		- mock_habit_repository.get_goal_of_habit returns [123].
	When:
		- habit_service.get_goal_of_habit(5) is called.
	Then:
		- It returns [123].
	"""
	mock_habit_repository.get_goal_of_habit.return_value = [123]
	goals = habit_service.get_goal_of_habit(5)

	mock_habit_repository.get_goal_of_habit.assert_called_with(5)
	assert goals == [123]



def test_get_goal_of_habit_invalid_id(habit_service):
	"""
	Test that get_goal_of_habit rejects negative habit_id.

	Given:
		- habit_id = -1.
	When:
		- svc.get_goal_of_habit is called.
	Then:
		- ValueError is raised.
	"""
	with pytest.raises(ValueError):
		habit_service.get_goal_of_habit(-1)
