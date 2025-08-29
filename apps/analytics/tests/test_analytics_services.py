import pytest
from unittest.mock import MagicMock
from mysql.connector.errors import IntegrityError

from apps.analytics.services.analytics_service import AnalyticsService
from apps.analytics.repositories.analytics_repository import AnalyticsNotFoundError
from apps.habits.services.habit_service import HabitService, HabitNotFoundError
from apps.progresses.services.progress_service import ProgressesService


@pytest.fixture
def mock_analytics_repo():
	"""
	Fixture that returns a MagicMock simulating AnalyticsRepository methods.

	Returns:
		MagicMock: The mocked analytics repository.
	"""
	return MagicMock()



@pytest.fixture
def mock_habit_service():
	"""
	Fixture that returns a MagicMock spec'd to HabitService.

	Returns:
		MagicMock: The mocked habit service.
	"""
	return MagicMock(spec=HabitService)



@pytest.fixture
def mock_progress_service():
	"""
	Fixture that returns a MagicMock spec'd to ProgressesService.

	Returns:
		MagicMock: The mocked progress service.
	"""
	return MagicMock(spec=ProgressesService)



@pytest.fixture
def analytics_service(mock_analytics_repo, mock_habit_service, mock_progress_service):
	"""
	Fixture to create an AnalyticsService with mocked dependencies.

	Args:
		mock_analytics_repo (MagicMock): The analytics repo mock.
		mock_habit_service (MagicMock): The habit service mock.
		mock_progress_service (MagicMock): The progress service mock.

	Returns:
		AnalyticsService: Service instance wired to mocks.
	"""
	return AnalyticsService(  
		repository=mock_analytics_repo,
		habit_service=mock_habit_service, 
		progress_service=mock_progress_service 
	)



def test_create_analytics_success(analytics_service, mock_analytics_repo, mock_habit_service):
	"""
	Test creating analytics entry with valid habit.

	Given:
		- habit_service.validate_a_habit returns a valid habit_id.
		- repository.create_analytics returns an analytics dict.
	When:
		- create_analytics is called.
	Then:
		- validate_a_habit and create_analytics are called once.
		- The returned dict is forwarded.
	"""
	mock_habit_service.validate_a_habit.return_value = 101

	mock_analytics_repo.create_analytics.return_value = {
		'analytics_id': 1,
		'times_completed': 10,
		'streak_length': 5,
		'habit_id_id': 101
	}

	result = analytics_service.create_analytics(
		habit_id=101,  
		times_completed=10,
		streak_length=5
	)

	mock_habit_service.validate_a_habit.assert_called_once_with(101)
	mock_analytics_repo.create_analytics.assert_called_once_with(
		10, 5, 101, last_completed_at=None
	)
	assert result['analytics_id'] == 1
	assert result['times_completed'] == 10



def test_create_analytics_habit_not_found(analytics_service, mock_habit_service):
	"""
	Test that creating analytics for non-existent habit raises HabitNotFoundError.

	Given:
		- habit_service.validate_a_habit raises HabitNotFoundError.
	When:
		- create_analytics is called.
	Then:
		- HabitNotFoundError is propagated.
	"""
	mock_habit_service.validate_a_habit.side_effect = HabitNotFoundError(42)

	with pytest.raises(HabitNotFoundError):
		analytics_service.create_analytics(habit_id=42, times_completed=1, streak_length=1)



def test_create_analytics_integrity_error(analytics_service, mock_analytics_repo, mock_habit_service):
	"""
	Test that repository IntegrityError propagates on create.

	Given:
		- habit_service.validate_a_habit returns valid ID.
		- repository.create_analytics raises IntegrityError.
	When:
		- create_analytics is called.
	Then:
		- IntegrityError is raised.
	"""
	mock_habit_service.validate_a_habit.return_value = 42
	mock_analytics_repo.create_analytics.side_effect = IntegrityError("Duplicate entry")

	with pytest.raises(IntegrityError):
		analytics_service.create_analytics(
			habit_id=42,
			times_completed=5,
			streak_length=2
		)



def test_update_analytics_success(analytics_service, mock_analytics_repo):
	"""
	Test updating analytics for a habit when entry exists.

	Given:
		- repository.get_analytics_id returns an analytics_id.
		- repository.update_analytics returns number of rows updated.
	When:
		- update_analytics is called.
	Then:
		- get_analytics_id and update_analytics are invoked.
		- The row count is returned.
	"""

	mock_analytics_repo.get_analytics_id.return_value = 10
	mock_analytics_repo.update_analytics.return_value = 1

	rows = analytics_service.update_analytics(
		habit_id=101,
		times_completed=20,
		streak_length=10
	)
	assert rows == 1

	mock_analytics_repo.get_analytics_id.assert_called_once_with(101)
	mock_analytics_repo.update_analytics.assert_called_once_with(10, 20, 10, None)


def test_average_streaks_empty(analytics_service, mock_analytics_repo):
	"""
	Test calculating average streaks from nonexisting analytics records.

	Given:
		- repository.get_habit_streaks returns a list of tuples with streak values.
	When:
		- average_streaks is called.
	Then:
		- The correct average is computed and returned.
	"""
	mock_analytics_repo.get_habit_streaks.return_value = []

	result = analytics_service.average_streaks()
	assert result == 0.0
	mock_analytics_repo.get_habit_streaks.assert_called_once()



def test_average_streaks_success(analytics_service, mock_analytics_repo):
	"""
	Test calculating average streaks from existing analytics records.

	Given:
		- repository.get_habit_streaks returns a list of tuples with streak values.
	When:
		- average_streaks is called.
	Then:
		- The correct average is computed and returned.
	"""
	mock_analytics_repo.get_habit_streaks.return_value = [(2,), (4,), (6,)]

	result = analytics_service.average_streaks()
	assert result == 4.0
	mock_analytics_repo.get_habit_streaks.assert_called_once()



def test_update_analytics_not_found(analytics_service, mock_analytics_repo):
	"""
	Test that updating non-existent analytics raises AnalyticsNotFoundError.

	Given:
		- repository.get_analytics_id returns an id.
		- repository.update_analytics raises AnalyticsNotFoundError.
	When:
		- update_analytics is called.
	Then:
		- AnalyticsNotFoundError is raised.
	"""
	mock_analytics_repo.get_analytics_id.return_value = 101
	mock_analytics_repo.update_analytics.side_effect = AnalyticsNotFoundError("notfound")

	with pytest.raises(AnalyticsNotFoundError):
		analytics_service.update_analytics(habit_id=10, times_completed=5)



def test_get_and_delete_analytics_flow(analytics_service, mock_analytics_repo):
	"""
	Test fetching and deleting analytics entries by habit or explicit ID.

	Given:
		- get_analytics_id returns an ID.
		- get_analytics_id / delete_analytics return appropriate values.
	When:
		- get_analytics_id, delete_analytics are called.
	Then:
		- Results are forwarded correctly.
	"""
	mock_analytics_repo.get_analytics_id.return_value = 7
	mock_analytics_repo.delete_analytics.return_value = 1

	a_id = analytics_service.get_analytics_id(habit_id=123)
	assert a_id == 7
	mock_analytics_repo.get_analytics_id.assert_called_once_with(123)

	deleted = analytics_service.delete_analytics(habit_id=123)
	mock_analytics_repo.delete_analytics.assert_called_with(7)
	assert deleted == 1

	mock_analytics_repo.delete_analytics.reset_mock()
	deleted2 = analytics_service.delete_analytics(analytics_id=99)
	mock_analytics_repo.delete_analytics.assert_called_once_with(99)
	assert deleted2 == 1



def test_get_analytics_id_not_found(analytics_service, mock_analytics_repo):
	"""
	Test that deleting non-existent analytics raises AnalyticsNotFoundError.

	Given:
		- repository.get_analytics_id returns an ID or delete_analytics raises.
	When:
		- delete_analytics is called.
	Then:
		- AnalyticsNotFoundError is propagated.
	"""
	mock_analytics_repo.get_analytics_id.side_effect = AnalyticsNotFoundError("notfound")
	with pytest.raises(AnalyticsNotFoundError): 
		analytics_service.get_analytics_id(habit_id=124) 



def test_delete_analytics_without_passing_analytics_id(analytics_service, mock_analytics_repo):
	mock_analytics_repo.get_analytics_id.return_value = 62 
	mock_analytics_repo.delete_analytics.return_value = 1 

	rows_deleted = analytics_service.delete_analytics(habit_id=42)  
	assert rows_deleted == 1

	mock_analytics_repo.get_analytics_id.assert_called_once_with(42)
	mock_analytics_repo.delete_analytics.assert_called_once_with(62) 



def test_misc_analytics_queries(analytics_service, mock_analytics_repo):
	"""
	Test other analytics queries, e.g. longest streak and grouping.

	Cases:
	- calculate_longest_streak
	- get_same_periodicity_type_habits
	- get_currently_tracked_habits
	- longest_streak_for_habit
	"""
	mock_analytics_repo.calculate_longest_streak.return_value = (1, 'peoplewatching', 5)
	assert analytics_service.calculate_longest_streak() == (1, 'peoplewatching', 5)
	mock_analytics_repo.calculate_longest_streak.assert_called_once()

	sampl = [('daily', 2, 'list')]
	mock_analytics_repo.get_same_periodicity_type_habits.return_value = sampl
	assert analytics_service.get_same_periodicity_type_habits() == sampl

	tracked = [(1, 'h', 3, 'weekly')]
	mock_analytics_repo.get_currently_tracked_habits.return_value = tracked
	assert analytics_service.get_currently_tracked_habits() == tracked

	mock_analytics_repo.longest_streak_for_habit.return_value = [(1,7,'h', 'date',3)]
	assert analytics_service.longest_streak_for_habit(habit_id=50) == [(1,7,'h', 'date',3)]
	mock_analytics_repo.longest_streak_for_habit.assert_called_once_with(50)
