import pytest
import logging
from unittest.mock import MagicMock
from apps.goals.services.goal_service import GoalService



from apps.goals.repositories.goal_repository import GoalRepository, GoalNotFoundError
from apps.habits.services.habit_service import HabitService, HabitNotFoundError
from apps.kvi_types.services.kvi_type_service import KviTypeService, KviTypesNotFoundError
from mysql.connector.errors import IntegrityError

# https://docs.python.org/3/library/unittest.mock.html
@pytest.fixture
def create_mock_goal_service():
	mock_goal_repo = MagicMock(spec=GoalRepository)
	mock_habit_service = MagicMock(spec=HabitService)
	mock_kvi_service = MagicMock(spec=KviTypeService)

	return GoalService(repository=mock_goal_repo, habit_service=mock_habit_service, kvi_service=mock_kvi_service)



import pytest
from unittest.mock import MagicMock
from apps.goals.services.goal_service import GoalService
from apps.goals.repositories.goal_repository import GoalRepository, GoalNotFoundError
from apps.habits.services.habit_service import HabitService, HabitNotFoundError
from apps.kvi_types.services.kvi_type_service import KviTypeService, KviTypesNotFoundError
from mysql.connector.errors import IntegrityError

@pytest.fixture
def create_mock_goal_service():
	mock_goal_repo = MagicMock(spec=GoalRepository)
	mock_habit_service = MagicMock(spec=HabitService)
	mock_kvi_service = MagicMock(spec=KviTypeService)

	return GoalService(repository=mock_goal_repo, habit_service=mock_habit_service, kvi_service=mock_kvi_service)

def test_create_goal_success(create_mock_goal_service):
	#at the moment id3 exist in the db
	create_mock_goal_service._habit_service._repository.validate_a_habit.return_value = 3
	create_mock_goal_service._kvi_service._repository.validate_a_kvi_type.return_value = 3


	#mock repos return value
	create_mock_goal_service.create_a_goal.return_value = {
		"goal_id": 1,
		"goal_name": "Losing Weight",
		"target_kvi_value": 5.0,
		"current_kvi_value": 0.0,
		"goal_description": "Lose 5kg over 2 months",
		"habit_id": 3,
		"kvi_type_id": 3
	}

	#call the actual service
	goal = create_mock_goal_service.create_a_goal("Losing Weight", 3, 3, 5.0, 0.0, "Lose 5kg over 2 months")

	#assert the results
	assert goal["goal_id"] == 1
	assert goal["goal_name"] == "Losing Weight"
	assert goal["target_kvi_value"] == 5.0
	assert goal["current_kvi_value"] == 0.0
	assert goal["habit_id"] == 3
	assert goal["kvi_type_id"] == 3
