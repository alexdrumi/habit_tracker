import pytest
from unittest.mock import MagicMock
from mysql.connector.errors import IntegrityError

from apps.analytics.services.analytics_service import AnalyticsService
from apps.analytics.repositories.analytics_repository import AnalyticsNotFoundError
from apps.habits.services.habit_service import HabitService
from apps.progresses.services.progress_service import ProgressesService


#fixtures for the required objects for analytics tests
@pytest.fixture
def mock_analytics_repo():
	return MagicMock()
  
@pytest.fixture
def mock_habit_service():
	return MagicMock(spec=HabitService)

@pytest.fixture
def mock_progress_service():
	return MagicMock(spec=ProgressesService)

@pytest.fixture
def analytics_service(mock_analytics_repo, mock_habit_service, mock_progress_service):
	return AnalyticsService(  
		repository=mock_analytics_repo,
		habit_service=mock_habit_service, 
		progress_service=mock_progress_service 
	)


#create tests
def test_create_analytics_success(analytics_service, mock_analytics_repo, mock_habit_service):
	#validate habit
	mock_habit_service.validate_a_habit.return_value = 101

	#analytics returns a dict, imitatet that here for expected return val
	mock_analytics_repo.create_analytics.return_value = {
		'analytics_id': 1,
		'times_completed': 10,
		'streak_length': 5,
		#do we need last completed at as well? prob bnot
		'habit_id_id': 101
	}

	result = analytics_service.create_analytics(
		habit_id=101,  
		times_completed=10,
		streak_length=5
	)

	#check that everything was called, once
	mock_habit_service.validate_a_habit.assert_called_once_with(101)
	mock_analytics_repo.create_analytics.assert_called_once_with(
		10, 5, 101, last_completed_at=None
	)
	assert result['analytics_id'] == 1
	assert result['times_completed'] == 10


def test_create_analytics_integrity_error(analytics_service, mock_analytics_repo, mock_habit_service):
	mock_habit_service.validate_a_habit.return_value = 42
	mock_analytics_repo.create_analytics.side_effect = IntegrityError("Duplicate entry")

	with pytest.raises(IntegrityError):
		analytics_service.create_analytics(
			habit_id=42,
			times_completed=5,
			streak_length=2
		)

#update part
def test_update_analytics_success(analytics_service, mock_analytics_repo):
	#get return value with analytics id 10
	mock_analytics_repo.get_analytics_id.return_value = 10
	#if update succesfull, return val will be 1
	mock_analytics_repo.update_analytics.return_value = 1  #one row gets updated

	rows = analytics_service.update_analytics(
		habit_id=101,
		times_completed=20,
		streak_length=10
	)
	assert rows == 1 #ret value is 1 upon successful update for 1 row


	mock_analytics_repo.get_analytics_id.assert_called_once_with(101) #assert w habit id 99, (related analytics ll be id 10)
	mock_analytics_repo.update_analytics.assert_called_once_with(10, 20, 10, None) #and the related update



def test_update_analytics_not_found(analytics_service, mock_analytics_repo):
	#incorrect analytics id, should raise notfound error
	mock_analytics_repo.get_analytics_id.return_value = 101
	mock_analytics_repo.update_analytics.side_effect = AnalyticsNotFoundError("notfound")

	with pytest.raises(AnalyticsNotFoundError):
		analytics_service.update_analytics(habit_id=10, times_completed=5)

#get tests
def test_get_analytics_id_success(analytics_service, mock_analytics_repo):
	#existing test
	mock_analytics_repo.get_analytics_id.return_value = 123  
	analytics_id = analytics_service.get_analytics_id(habit_id=10) 
	assert analytics_id == 123
	mock_analytics_repo.get_analytics_id.assert_called_once_with(10)

def test_get_analytics_id_not_found(analytics_service, mock_analytics_repo):
	#not found test
	mock_analytics_repo.get_analytics_id.side_effect = AnalyticsNotFoundError("notfound")
	with pytest.raises(AnalyticsNotFoundError): 
		analytics_service.get_analytics_id(habit_id=124) 
 
#delete tests
def test_delete_analytics_without_passing_analytics_id(analytics_service, mock_analytics_repo):
	mock_analytics_repo.get_analytics_id.return_value = 62 #just random ids to test against
	mock_analytics_repo.delete_analytics.return_value = 1 

	rows_deleted = analytics_service.delete_analytics(habit_id=42)  
	assert rows_deleted == 1

	mock_analytics_repo.get_analytics_id.assert_called_once_with(42)
	mock_analytics_repo.delete_analytics.assert_called_once_with(62) 



def test_delete_analytics_explicit_id(analytics_service, mock_analytics_repo):
	#explicits test
	mock_analytics_repo.delete_analytics.return_value = 1
	rows_deleted = analytics_service.delete_analytics(analytics_id=803)
	assert rows_deleted == 1

	mock_analytics_repo.delete_analytics.assert_called_once_with(803)



def test_delete_analytics_not_found(analytics_service, mock_analytics_repo):
	#not found tests 
	mock_analytics_repo.delete_analytics.side_effect = AnalyticsNotFoundError("notfound")
	with pytest.raises(AnalyticsNotFoundError): 
		analytics_service.delete_analytics(analytics_id=807)



#longest streak tests
def test_calculate_longest_streak_success(analytics_service, mock_analytics_repo):
	mock_analytics_repo.calculate_longest_streak.return_value = (10, 'pushups', 15)
	result = analytics_service.calculate_longest_streak()   
	assert result == (10, 'pushups', 15)  

	mock_analytics_repo.calculate_longest_streak.assert_called_once()


def test_calculate_longest_streak_not_found(analytics_service, mock_analytics_repo):
	#not found
	mock_analytics_repo.calculate_longest_streak.side_effect = AnalyticsNotFoundError("notfound")
	with pytest.raises(AnalyticsNotFoundError):
		analytics_service.calculate_longest_streak()  


#same periodicity types
def test_get_same_periodicity_type_habits(analytics_service, mock_analytics_repo):

	mock_analytics_repo.get_same_periodicity_type_habits.return_value = [
		('daily', 2, '1: pushups, 2: planks')  
	]
	result = analytics_service.get_same_periodicity_type_habits()
	assert len(result) == 1 

	mock_analytics_repo.get_same_periodicity_type_habits.assert_called_once() 

def test_get_same_periodicity_type_habits_not_found(analytics_service, mock_analytics_repo):
	#not found
	mock_analytics_repo.get_same_periodicity_type_habits.side_effect = AnalyticsNotFoundError("notfound")
	with pytest.raises(AnalyticsNotFoundError):  
		analytics_service.get_same_periodicity_type_habits() 



def test_get_currently_tracked_habits_success(analytics_service, mock_analytics_repo):
	#at least one tracked success
	mock_analytics_repo.get_currently_tracked_habits.return_value = [
		(1, "pushups", 5, "daily")  
	]
	result = analytics_service.get_currently_tracked_habits()
	assert len(result) == 1 
	mock_analytics_repo.get_currently_tracked_habits.assert_called_once()

#not found habits
def test_get_currently_tracked_habits_not_found(analytics_service, mock_analytics_repo):
	mock_analytics_repo.get_currently_tracked_habits.side_effect = AnalyticsNotFoundError("notfound")
	with pytest.raises(AnalyticsNotFoundError): 
		analytics_service.get_currently_tracked_habits() 

#longest streak 
def test_longest_streak_for_habit_success(analytics_service, mock_analytics_repo):
	mock_analytics_repo.longest_streak_for_habit.return_value = [
		(1, 8, 'pushups', '2025-02-19 00:00:00', 7)
	]
	result = analytics_service.longest_streak_for_habit(habit_id=17)

	assert result[0][0] == 1
	mock_analytics_repo.longest_streak_for_habit.assert_called_once_with(17)

#longest streak notfound
def test_longest_streak_for_habit_not_found(analytics_service, mock_analytics_repo): 
	mock_analytics_repo.longest_streak_for_habit.side_effect = AnalyticsNotFoundError("notfound")
	with pytest.raises(AnalyticsNotFoundError):  
		analytics_service.longest_streak_for_habit(habit_id=807)  
