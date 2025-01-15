from django.db import models
from apps.habits.models import Habits

# Create your models here.
class Analytics(models.Model):
	analytics_id = models.AutoField(primary_key=True)
	habit_id = models.ForeignKey(
		Habits,
		on_delete=models.PROTECT, #dont delete analytics just cuz habit is deleted
		related_name='habit_analytics'
	)
	times_completed = models.IntegerField(default=0)
	streak_length = models.IntegerField(default=0)
	last_completed_at = models.DateField(blank=True, null=True)
	created_at = models.TimeField(auto_now_add=True)
	
	class Meta:
		db_table = "analytics"
	
	def save(self, *args, **kwargs):
		if self.times_completed < 0 or self.times_completed > 365:
			raise ValueError("Habit is completed invalid amount of times.")
		if self.streak_length < 0 or self.streak_length > 365:
			raise ValueError("Streak is completed invalid amount of times.")

		super().save(*args, **kwargs)
	
	def __str__(self):
		return f"Analytics ID: {self.analytics_id} is created at: {self.created_at}."

