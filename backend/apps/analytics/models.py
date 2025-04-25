from django.db import models
from apps.habits.models import Habits
from django.db.models import UniqueConstraint

# Create your models here.
class Analytics(models.Model):
	analytics_id = models.AutoField(primary_key=True)
	habit_id = models.OneToOneField(
		Habits,
		on_delete=models.CASCADE, #dont delete analytics just cuz habit is deleted
		related_name='habit_analytics',
		unique=True,
	)
	times_completed = models.IntegerField(default=0)
	streak_length = models.IntegerField(default=0)
	last_completed_at = models.DateField(blank=True, null=True)
	created_at = models.TimeField(auto_now_add=True)
	
	class Meta:
		db_table = "analytics"
		constraints = [
			UniqueConstraint(fields=["habit_id", "analytics_id"], name="unique_analytics_per_habit")
		]

	def save(self, *args, **kwargs):
		if self.times_completed < 0 or self.times_completed > 365:
			raise ValueError("Habit is completed invalid amount of times.")
		if self.streak_length < 0 or self.streak_length > 365:
			raise ValueError("Streak is completed invalid amount of times.")

		super().save(*args, **kwargs)
	
	def __str__(self):
		return f"Analytics ID: {self.analytics_id} is created at: {self.created_at}."

