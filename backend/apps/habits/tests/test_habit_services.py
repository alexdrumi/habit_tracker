import pytest
from unittest.mock import MagicMock
from apps.habits.services.habit_service import HabitService
from apps.habits.repositories.habit_repository import HabitNotFoundError, HabitAlreadyExistError

@pytest.fixture
def mock_habit_repository():
	return MagicMock()

#creates a habitservice instance using magicmock
@pytest.fixture
def habit_service(mock_habit_repository):
	return HabitService(repository=mock_habit_repository)

#test successful habit creationg
def test_create_habit_success(habit_service, mock_habit_repository):
	expected_result = {
		 'habit_id': 1,
		 'habit_name': "test1",
		 'habit_action': "testing 1",
		 'habit_streak': 0,
		 'habit_periodicity_type': "daily",
		 'habit_user_id': 1,
	}
	#set an expected return value upon creation
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

	#this should raise a duplicate error
	with pytest.raises(HabitAlreadyExistError) as exc_info:
		habit_service.create_a_habit("test1", "testing 1", "daily", 1)
	assert "Habit 'test1' already exists for user with id: 1" in str(exc_info.value)


#test invalid periodicity type
def test_create_habit_invalid_periodicity(habit_service):
	with pytest.raises(ValueError) as exc_info:
		habit_service.create_a_habit("drinking wateh", "drink 2 liters of water", "millenially", 1)
	assert 'Invalid habit periodicity type. Expected one of "DAILY" "WEEKLY" in str(exc_info.value)'


#test successful streak update
def test_update_habit_streak_success(habit_service, mock_habit_repository):

	#valid habit id
	mock_habit_repository.validate_a_habit.return_value = 1

	#success ful update return 1 for updated amount of rows here
	mock_habit_repository.update_habit_field.return_value = 1

	result = habit_service.update_habit_streak(1, 5)
	mock_habit_repository.validate_a_habit.assert_called_with(1)
	mock_habit_repository.update_habit_field.assert_called_with(1, 'habit_streak', 5)
	# print(f"RESULT IS : {result}")
	assert result == 1


#test updating habit streak negative streak valueå
def test_update_habit_streak_invalid_value(habit_service):
	with pytest.raises(ValueError) as exc_info:
		habit_service.update_habit_streak(1, -1)
	assert "Invalid streak value. It must be a positive integer." in str(exc_info.value) #these messages are raised from the '_validate_habit_input'


#test that get_habit_id returns the correct habit id
def test_get_habit_id_success(habit_service, mock_habit_repository):
	mock_habit_repository.get_habit_id.return_value = 1
	result = habit_service.get_habit_id(1, "test1")
	mock_habit_repository.get_habit_id.assert_called_with(1, "test1")
	assert result == 1

#test that get_habit_id raises HabitNotFoundError when the habit is not found.
def test_get_habit_id_not_found(habit_service, mock_habit_repository):
	mock_habit_repository.get_habit_id.side_effect = HabitNotFoundError("notfound")
	with pytest.raises(HabitNotFoundError):
		habit_service.get_habit_id(1, "notfound")