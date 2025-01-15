import pytest
from apps.habits.models import Habits
from apps.goals.models import Analytics

# analytics_id = models.AutoField(primary_key=True)
# 	habit_id = models.ForeignKey(
# 		Habits,
# 		on_delete=models.PROTECT #dont delete analytics just cuz habit is deleted
# 		related_name='habit_analytics'
# 	)
# 	times_completed = models.IntegerField(default=0)
# 	streak_length = models.IntegerField(default=0)
# 	last_completed_at = models.DateField(blank=True, null=True)
# 	created_at = models.TimeField(auto_now_add=True)


@pytest.mark.django_db
def test_create_valid_analytics(setup_habit):
	'''Test for creating valid analytics.'''
	test_analytics = Analytics.obje