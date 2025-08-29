import pytest
from datetime import datetime, timedelta
import click
from apps.notifications.domain.daily_notification import DailyNotificationStrategy
from apps.notifications.domain.weekly_notification import WeeklyNotificationStrategy
from apps.notifications.domain.notification_observer import NotificationObserver
from apps.progresses.domain.progress_dto import ProgressHistoryDTO



@pytest.fixture
def make_dto():
	"""Factory for ProgressHistoryDTO with given streak and age."""
	def factory(streak, days_ago=0):
		last = datetime.now() - timedelta(days=days_ago)
		return ProgressHistoryDTO(
			last_updated_time=last,
			distance_from_goal=0.0,
			streak=streak
		)
	return factory
