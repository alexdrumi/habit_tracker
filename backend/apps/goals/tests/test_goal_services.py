import pytest
from unittest.mock import MagicMock
from apps.goals.services.goal_service import GoalService
from apps.goals.repositories.goal_repository import GoalRepository, GoalNotFoundError
from apps.habits.services.habit_service import HabitService, HabitNotFoundError
from apps.kvi_types.services.kvi_type_service import KviTypeService  #if needed here..
from mysql.connector.errors import IntegrityError

@pytest.fixture
def create_mock_goal_service():
	mock_goal_repo = MagicMock(spec=GoalRepository)
	mock_habit_service = MagicMock(spec=HabitService)
	# mock_kvi_service = MagicMock(spec=KviTypeService) in this version no kvi repo needed
	return GoalService(repository=mock_goal_repo, habit_service=mock_habit_service)

def test_create_goal_success(create_mock_goal_service):
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

	#do assert with expected vals
	assert goal["goal_id"] == 1
	assert goal["goal_name"] == "Losing Weight"
	assert goal["target_kvi_value"] == 5.0
	assert goal["current_kvi_value"] == 0.0
	assert goal["habit_id"] == 3
	assert goal["kvi_type_id"] == 3

def test_create_goal_duplicate_error(create_mock_goal_service):
	create_mock_goal_service._habit_service.validate_a_habit.return_value = 3

	create_mock_goal_service._repository.create_a_goal.side_effect = IntegrityError("Duplicate entry")

	with pytest.raises(IntegrityError):
		create_mock_goal_service.create_a_goal("Losing weight", 3, 5.0, 0.0, "Lose 5kg over 2 months")
  
def test_create_goal_invalid_goal_name(create_mock_goal_service):
	with pytest.raises(ValueError) as exc_info:  
		create_mock_goal_service.create_a_goal("", 3, 5.0, 0.0, "Lose 5kg over 2 months")
	assert "user_goal_name is required" in str(exc_info.value)


def test_get_goal_entity_not_found(create_mock_goal_service):
	create_mock_goal_service._repository.get_goal_entity_by_id.side_effect = GoalNotFoundError(99)
	with pytest.raises(GoalNotFoundError):
		create_mock_goal_service.get_goal_entity_by_id(99, 3)
