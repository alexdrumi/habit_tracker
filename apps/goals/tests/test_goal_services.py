import pytest
from unittest.mock import MagicMock
from apps.goals.services.goal_service import GoalService
from apps.goals.repositories.goal_repository import GoalRepository, GoalNotFoundError
from apps.habits.services.habit_service import HabitService, HabitNotFoundError
from apps.kvi_types.services.kvi_type_service import KviTypeService
from mysql.connector.errors import IntegrityError

@pytest.fixture
def create_mock_goal_service():
	"""
	Fixture to create a GoalService with mocked repository and habit service.

	Returns:
		GoalService: Service instance with MagicMocks.
	"""
	mock_goal_repo = MagicMock(spec=GoalRepository)
	mock_habit_service = MagicMock(spec=HabitService)
	return GoalService(repository=mock_goal_repo, habit_service=mock_habit_service)



def test_create_goal_success(create_mock_goal_service):
	"""
	Test creating a goal with valid inputs.

	Given:
		- A valid goal_name, habit_id, target/current KVI, and description.
		- habit_service.validate_a_habit returns the same habit_id.
		- repository.create_a_goal returns a dict with goal fields.
	When:
		- service.create_a_goal is called.
	Then:
		- It returns the dict from repository.
	"""
	expected_goal = {
		"goal_id": 1,
		"goal_name": "Losing Weight",
		"target_kvi_value": 5.0,
		"current_kvi_value": 0.0,
		"goal_description": "Lose 5kg over 2 months",
		"habit_id": 3,
		"kvi_type_id": 3
	}
	create_mock_goal_service._repository.create_a_goal.return_value = expected_goal
	goal = create_mock_goal_service.create_a_goal("Losing Weight", 3, 5.0, 0.0, "Lose 5kg over 2 months")

	assert goal["goal_id"] == 1
	assert goal["goal_name"] == "Losing Weight"
	assert goal["target_kvi_value"] == 5.0
	assert goal["current_kvi_value"] == 0.0
	assert goal["habit_id"] == 3
	assert goal["kvi_type_id"] == 3



def test_create_goal_duplicate_error(create_mock_goal_service):
	"""
	Test that IntegrityError during creation propagates.

	Given:
		- habit_service.validate_a_habit returns a valid ID.
		- repository.create_a_goal raises IntegrityError.
	When:
		- service.create_a_goal is called.
	Then:
		- It raises IntegrityError.
	"""
	create_mock_goal_service._habit_service.validate_a_habit.return_value = 3
	create_mock_goal_service._repository.create_a_goal.side_effect = IntegrityError("Duplicate entry")

	with pytest.raises(IntegrityError):
		create_mock_goal_service.create_a_goal("Losing weight", 3, 5.0, 0.0, "Lose 5kg over 2 months")



def test_create_goal_empty_goal_name(create_mock_goal_service):
	"""
	Test that an empty goal_name raises ValueError.

	Given:
		- goal_name is empty.
	When:
		- service.create_a_goal is called.
	Then:
		- It raises ValueError mentioning user_goal_name.
	"""
	with pytest.raises(ValueError) as exc_info:  
		create_mock_goal_service.create_a_goal("", 3, 5.0, 0.0, "Lose 5kg over 2 months")
	assert "user_goal_name is required" in str(exc_info.value)



def test_create_goal_habit_not_found(create_mock_goal_service):
	"""
	Test that creating a goal for a non-existent habit raises HabitNotFoundError.

	Given:
		- habit_service.validate_a_habit raises HabitNotFoundError.
	When:
		- service.create_a_goal is called.
	Then:
		- It propagates HabitNotFoundError.
	"""
	create_mock_goal_service._habit_service.validate_a_habit.side_effect = HabitNotFoundError(99)

	with pytest.raises(HabitNotFoundError):
		create_mock_goal_service.create_a_goal("Goal", 99, 1.0, 0.0, "desc")



def test_get_goal_entity_not_found(create_mock_goal_service):
	"""
	Test that retrieving a missing goal entity raises GoalNotFoundError.

	Given:
		- repository.get_goal_entity_by_id raises GoalNotFoundError.
	When:
		- service.get_goal_entity_by_id is called.
	Then:
		- It propagates GoalNotFoundError.
	"""
	create_mock_goal_service._repository.get_goal_entity_by_id.side_effect = GoalNotFoundError(99)
	with pytest.raises(GoalNotFoundError):
		create_mock_goal_service.get_goal_entity_by_id(99, 3)




def test_create_goal_calls_validate_and_repository(create_mock_goal_service):
    """
    Test that create_a_goal first validates habit then calls repository.

    Given:
        - habit_service.validate_a_habit returns valid ID.
    When:
        - service.create_a_goal is called.
    Then:
        - validate_a_habit is called before repository.create_a_goal.
    """
    create_mock_goal_service._habit_service.validate_a_habit.return_value = 7
    create_mock_goal_service._repository.create_a_goal.return_value = {"goal_id": 7}

    create_mock_goal_service.create_a_goal("G1", 7, 2.0, 0.5, "desc")

    create_mock_goal_service._habit_service.validate_a_habit.assert_called_once_with(7)
    create_mock_goal_service._repository.create_a_goal.assert_called_once_with("G1", 7, 2.0, 0.5, "desc")