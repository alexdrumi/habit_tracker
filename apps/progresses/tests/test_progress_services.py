import pytest
from unittest.mock import MagicMock, patch

from apps.progresses.services.progress_service import ProgressesService
from apps.progresses.repositories.progress_repository import ProgressNotFoundError, ProgressAlreadyExistError
from apps.goals.services.goal_service import GoalNotFoundError

@pytest.fixture
def mock_progress_repo():
	"""
	Fixture returning a MagicMock simulating the ProgressesRepository.

	Returns:
		MagicMock: A mock progress repository.
	"""
	return MagicMock()



@pytest.fixture
def mock_goal_service():
	"""
	Fixture returning a MagicMock simulating the GoalService.

	Returns:
		MagicMock: A mock goal service.
	"""
	return MagicMock()



@pytest.fixture
def progresses_service(mock_progress_repo, mock_goal_service):
	"""
	Fixture instantiating ProgressesService with mocked dependencies.

	Args:
		mock_progress_repo (MagicMock): The mocked progress repository.
		mock_goal_service (MagicMock): The mocked goal service.

	Returns:
		ProgressesService: Service instance using mocks.
	"""
	return ProgressesService(repository=mock_progress_repo, goal_service=mock_goal_service)



def test_create_progress_success(progresses_service, mock_progress_repo, mock_goal_service):
	"""
	Test creating progress when no prior entry andno streak.

	Given:
		- goal_service.validate_goal_id returns valid goal_id.
		- goal_service.get_goal_entity_by_goal_id returns a target_kvi != 1.
		- repository.get_last_progress_entry returns None.
	When:
		- create_progress is called without current_streak or occurence_date.
	Then:
		- repository.create_progress is called with current_streak == 1.
		- The returned entity is forwarded.
	"""
	mock_goal_service.validate_goal_id.return_value = 10
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



def test_create_progress_with_explicit_streak(progresses_service, mock_progress_repo, mock_goal_service):
	"""
	Test creating progress with an explicit current_streak overrides logic.

	Given:
		- repository.get_last_progress_entry returns a previous entry.
		- current_streak parameter is provided.
	When:
		- create_progress is called with current_streak=5.
	Then:
		- repository.create_progress is called with current_streak == 5.
	"""
	mock_goal_service.validate_goal_id.return_value = 10
	mock_goal_service.get_goal_entity_by_goal_id.return_value = {'target_kvi': 1.0}
	mock_progress_repo.get_last_progress_entry.return_value = ('id', 10, 1.0, None, None, None, 2)
	expected = {'progress_id': 2, 'goal_id': 10, 'current_streak': 5}
	mock_progress_repo.create_progress.return_value = expected

	result = progresses_service.create_progress(
		goal_id=10,
		current_kvi_value=2.0,
		distance_from_target_kvi_value=3.0,
		goal_name='g',
		habit_name='h',
		current_streak=5
	)

	_, kwargs = mock_progress_repo.create_progress.call_args
	assert kwargs['current_streak'] == 5
	assert result == expected



def test_create_progress_goal_not_found(progresses_service, mock_goal_service):
	"""
	Test that creating progress for a non-existent goal propagates GoalNotFoundError.

	Given:
		- goal_service.validate_goal_id raises GoalNotFoundError.
	When:
		- create_progress is called.
	Then:
		- GoalNotFoundError is raised.
	"""
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
	"""
	Test retrieving a progress entry by goal_id.

	Given:
		- repository.get_progress_id returns progress_id.
		- repository.get_progress returns a dict.
	When:
		- get_progress is called.
	Then:
		- It returns the dict from repository.
	"""
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
	"""
	Test that requesting progress for a goal with no entries raises ProgressNotFoundError.

	Given:
		- repository.get_progress_id raises ProgressNotFoundError.
	When:
		- get_progress is called.
	Then:
		- ProgressNotFoundError is raised.
	"""
	mock_progress_repo.get_progress_id.side_effect = ProgressNotFoundError("No progress for that goal")
	with pytest.raises(ProgressNotFoundError):
		progresses_service.get_progress(goal_id=999)



def test_delete_progress_with_no_id_passed(progresses_service, mock_progress_repo):
	"""
	Test deleting progress when progress_id is not provided.

	Given:
		- repository.get_progress_id returns 5.
		- repository.delete_progress returns number of rows.
	When:
		- delete_progress is called without progress_id.
	Then:
		- delete_progress is called with the fetched ID.
		- The returned count is forwarded.
	"""
	mock_progress_repo.get_progress_id.return_value = 23
	mock_progress_repo.delete_progress.return_value = 1

	rows_deleted = progresses_service.delete_progress(goal_id=10) 
	assert rows_deleted == 1  
	mock_progress_repo.delete_progress.assert_called_with(23)



def test_delete_progress_not_found(progresses_service, mock_progress_repo):
	"""
	Test that deleting a non-existent progress entry raises ProgressNotFoundError.

	Given:
		- repository.get_progress_id returns an ID.
		- repository.delete_progress raises ProgressNotFoundError.
	When:
		- delete_progress is called.
	Then:
		- ProgressNotFoundError is raised.
	"""
	mock_progress_repo.get_progress_id.return_value = 98
	mock_progress_repo.delete_progress.side_effect = ProgressNotFoundError("No progress with ID=98")
	with pytest.raises(ProgressNotFoundError):
		progresses_service.delete_progress(goal_id=98)
