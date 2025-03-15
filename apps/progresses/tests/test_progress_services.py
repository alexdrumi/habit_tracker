import pytest
from unittest.mock import MagicMock, patch

from apps.progresses.services.progress_service import ProgressesService
from apps.progresses.repositories.progress_repository import ProgressNotFoundError, ProgressAlreadyExistError
from apps.goals.services.goal_service import GoalNotFoundError

@pytest.fixture
def mock_progress_repo():
	return MagicMock()

@pytest.fixture
def mock_goal_service():
	return MagicMock()

@pytest.fixture
def progresses_service(mock_progress_repo, mock_goal_service):
	return ProgressesService(repository=mock_progress_repo, goal_service=mock_goal_service)

#create normal progress
def test_create_progress_success(progresses_service, mock_progress_repo, mock_goal_service):
	mock_goal_service.validate_goal_id.return_value = 10  #goal_id
	mock_progress_repo.create_progress.return_value = {   
		'progress_id': 1,  	
		'goal_id': 10,	
		'current_kvi_value': 3.0,
	}

	result = progresses_service.create_progress(
		goal_id=10,
		current_kvi_value=3.0,
		distance_from_target_kvi_value=4.0,
		current_streak=1,
		goal_name="somegoal",
		habit_name="somehabit"
	)
	assert result['goal_id'] == 10   
	assert result['progress_id'] == 1  


def test_create_progress_goal_not_found(progresses_service, mock_goal_service):
	mock_goal_service.validate_goal_id.side_effect = GoalNotFoundError("No such goal")
	with pytest.raises(GoalNotFoundError):
		progresses_service.create_progress(
			goal_id=956,  
			current_kvi_value=1.0,
			distance_from_target_kvi_value=6.0,
			current_streak=1,
			goal_name="whatever",
			habit_name="somehabit" 
		)


def test_get_progress_success(progresses_service, mock_progress_repo):
	mock_progress_repo.get_progress_id.return_value = 1  
	mock_progress_repo.get_progress.return_value = {
		"progress_id": 1, 
		"goal_id_id": 10,
		"current_kvi_value": 5.0  
	}

	progress = progresses_service.get_progress(goal_id=10)
	assert progress["progress_id"] == 1
	assert progress["goal_id_id"] == 10


def test_get_progress_not_found(progresses_service, mock_progress_repo):
	mock_progress_repo.get_progress_id.side_effect = ProgressNotFoundError("No progress for that goal")
	with pytest.raises(ProgressNotFoundError):
		progresses_service.get_progress(goal_id=999)

def test_delete_progress_with_no_id_passed(progresses_service, mock_progress_repo):
	mock_progress_repo.get_progress_id.return_value = 23
	mock_progress_repo.delete_progress.return_value = 1  #deleted amount of rows, 1 expected

	rows_deleted = progresses_service.delete_progress(goal_id=10) 
	assert rows_deleted == 1  
	mock_progress_repo.delete_progress.assert_called_with(23)


def test_delete_progress_not_found(progresses_service, mock_progress_repo):
	mock_progress_repo.get_progress_id.return_value = 98
	mock_progress_repo.delete_progress.side_effect = ProgressNotFoundError("No progress with ID=98")
	with pytest.raises(ProgressNotFoundError):
		progresses_service.delete_progress(goal_id=98)
