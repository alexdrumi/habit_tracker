import pytest
from unittest.mock import patch, MagicMock

from apps.notifications.domain.notification_strategy import NotificationStrategy
from apps.notifications.domain.notification_observer import NotificationObserver
from apps.notifications.domain.daily_notification import DailyNotificationStrategy
from apps.notifications.domain.weekly_notification import WeeklyNotificationStrategy
from apps.progresses.domain.progress_dto import ProgressHistoryDTO

#abstract method should not be possible to implement directly.
def test_notification_strategy_cannot_instantiate():
	with pytest.raises(TypeError):
		NotificationStrategy()

#DAILY NOTIFICATION TESTS
def test_daily_notification_strategy_on_completion():
	strategy = DailyNotificationStrategy()
	progress_data = ProgressHistoryDTO(last_updated_time=None, distance_from_goal_kvi=5, streak=3)
	msg = strategy.on_completion_message(progress_data)

	assert "Congratulations" in msg
	assert "streak is 3" in msg


def test_daily_notification_strategy_on_expired():
	strategy = DailyNotificationStrategy()
	progress_data = ProgressHistoryDTO(last_updated_time=None, distance_from_goal_kvi=5, streak=0)
	msg = strategy.on_expired_message(progress_data)

	assert "You have missed the previous deadline" in msg


#WEEKLY NOTIFICATION TESTS
def test_weekly_notification_strategy_on_completion():
	strategy = WeeklyNotificationStrategy()
	progress_data = ProgressHistoryDTO(last_updated_time=None, distance_from_goal_kvi=5, streak=2)
	msg = strategy.on_completion_message(progress_data)
	assert "Congratulations" in msg
	assert "streak is 2" in msg

def test_weekly_notification_strategy_on_expired():
	strategy = WeeklyNotificationStrategy()
	progress_data = ProgressHistoryDTO(last_updated_time=None, distance_from_goal_kvi=11, streak=0)
	msg = strategy.on_expired_message(progress_data)
	assert "You have missed the previous deadline" in msg


#OBSERVER LOGIC
#https://pytest-with-eric.com/mocking/mocking-vs-patching/
@patch("builtins.print")
def test_notification_observer_daily(mock_print):
	"""
	Checks that notification observer uses daily strategy, prints msg on completion message
	"""
	observer = NotificationObserver(notification_stragety="daily")
	#progress dto to the notification observers update method
	sample_data = {
		'last_occurence': None,
		'target_kvi': 10,
		'current_kvi': 2,
		'streak': 1,   # triggers on_completion message
	}
	observer.update(sample_data)

	
	mock_print.assert_called()  #we only check that print was called, or we can parse call args

@patch("builtins.print")
def test_notification_observer_weekly(mock_print):
	"""
	Checks that notification observer uses weekly strategy, prints msg on completion message
	"""
	observer = NotificationObserver(notification_stragety="weekly")
	sample_data = {
		'last_occurence': None,
		'target_kvi': 10,
		'current_kvi': 10,  
		'streak': 0,   #triggers on_expired message
	}
	observer.update(sample_data)

	#confirm that print was called, it should print the weekly expired message
	mock_print.assert_called()
