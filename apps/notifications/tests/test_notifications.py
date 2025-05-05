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



# @pytest.mark.parametrize("Strategy", [DailyNotificationStrategy, WeeklyNotificationStrategy])
# def test_strategy_completion_and_expiry(Strategy, make_dto):
# 	"""
# 	Both daily & weekly strategies:
# 	  - should return a !None completion message when streak > 0
# 	  - should return a !None expired message when streak == 0
# 	  - should return None for the opposite case
# 	"""
# 	strategy = Strategy()

# 	#completion
# 	dto_pos = make_dto(streak=5, days_ago=1)
# 	assert strategy.on_completion_message(dto_pos)  is not None
# 	assert strategy.on_expired_message(dto_pos) is  None

# 	#expiry
# 	dto_zero = make_dto(streak=0, days_ago=100)
# 	assert strategy.on_completion_message(dto_zero) is None
# 	assert strategy.on_expired_message(dto_zero) is not None



# def test_observer_prints_both(monkeypatch, capsys, make_dto):
# 	"""
# 	NotificationObs should pick the right strategy (dail or weekly)
# 	and echo both completion and expired messages if present.
# 	"""
# 	#fake strategy that returns known strings
# 	class FakeStrat:
# 		def on_completion_message(self, dto): return "completion"
# 		def on_expired_message(self, dto):    return "expired"

# 	#monkeypath mapping inside notobsrvr
# 	monkeypatch.setattr( #https://docs.pytest.org/en/stable/how-to/monkeypatch.html
# 		NotificationObserver, 
# 		"_NotificationObserver__strat_map",  # force‐invisible private attr
# 		{"daily": lambda: FakeStrat(), "weekly": lambda: FakeStrat()} #inline lambda is pretty
# 	)

# 	#patch click.echo to prefix messages to detecth themsa
# 	outputs = []
# 	monkeypatch.setattr(click, "echo", lambda msg: outputs.append(msg))

# 	#test for both daily and weekly
# 	for name in ("daily", "weekly"):
# 		outputs.clear()
# 		obs = NotificationObserver(name)
# 		obs.update({
# 			"last_occurence": datetime.now(),
# 			"target_kvi": 1.0,
# 			"current_kvi": 1.0,
# 			"streak": 1
# 		})
# 		assert "completion" in "".join(outputs)
# 		assert "expired" in "".join(outputs)


  