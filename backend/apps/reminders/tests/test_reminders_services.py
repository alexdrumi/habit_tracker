import pytest
from datetime import datetime, timedelta
from unittest.mock import MagicMock, patch

from apps.reminders.services.reminder_service import ReminderService

@pytest.fixture
def mock_goal_service():
	return MagicMock()  

@pytest.fixture
def reminder_service(mock_goal_service):
	return ReminderService(goal_service=mock_goal_service)  
 

def test_calculate_tickability_too_early(reminder_service):
	now = datetime(2025, 3, 15, 12, 0, 0)   
	last_occurrence = now - timedelta(hours=1)
	#24 h window
	td_24_hours = timedelta(hours=24)

	#if only 1 h passed, its too early, not tickable
	result = reminder_service.calculate_tickability(
		last_occurence_datetime=last_occurrence,
		current_time=now,
		time_delta_difference=td_24_hours
	)
	assert result is False
  

	
def test_calculate_tickability_within_window(reminder_service):
	now = datetime(2025, 3, 15, 12, 0, 0)
	last_occurrence = now - timedelta(hours=25) 
	td_24_hours = timedelta(hours=24)
	#between 24 and 48 h, should be tickable
	result = reminder_service.calculate_tickability(
		last_occurence_datetime=last_occurrence,
		current_time=now,
		time_delta_difference=td_24_hours
	)
	assert result is True



def test_calculate_tickability_too_late(reminder_service):
	now = datetime(2025, 3, 15, 12, 0, 0)
	last_occurrence = now - timedelta(hours=50)  #more than 2 days
	td_24_hours = timedelta(hours=24)

	#if its beyond 2 * 24 = 48 hours, too late thus false
	result = reminder_service.calculate_tickability(
		last_occurence_datetime=last_occurrence,
		current_time=now,
		time_delta_difference=td_24_hours
	)
	assert result is False



def test_is_tickable_no_history(reminder_service):
	#empty is automatically tickable
	assert reminder_service.is_tickable(daily_or_weekly=1, last_occurence={}) is True

def test_is_tickable_with_history(reminder_service):
	now = datetime(2025, 3, 15, 12, 0, 0)
	#last occurence between 28-48h
	last_occ = {
		'occurence_date': now - timedelta(hours=30)
	}

	with patch("apps.reminders.services.reminder_service.datetime") as mock_datetime:
		mock_datetime.now.return_value = now
		result = reminder_service.is_tickable(daily_or_weekly=1, last_occurence=last_occ)
		#24 h is the base delta
		#30 h is between 24-48
		assert result is True

@patch("builtins.print")
def test_get_pending_goals_some_goals(mock_print, reminder_service, mock_goal_service):
	#if at least 1 goal is there, it should be printed in the pending goals 
	mock_goal_service.query_all_goals.return_value = [
		{"goal_id": 1, "goal_name": "pushups", "habit_id": 80, "target_kvi_value": 1.0},
		{"goal_id": 2, "goal_name": "reading", "habit_id": 11, "target_kvi_value": 1.0},
	]

	mock_goal_service.get_last_progress_entry_associated_with_goal_id.return_value = {}

	reminder_service.get_pending_goals()

	#theseare to be ticked
	mock_print.assert_any_call("\033[91mGOALS THAT NEED TO BE TICKED\033[0m")
	#line for each goal + 1 for header
	assert mock_print.call_count >= 3 
