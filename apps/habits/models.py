from django.db import models
from apps.users.models import AppUsers
from django.db.models import UniqueConstraint

class ValidPeriodicityTypes(models.TextChoices):
	DAILY = 'daily'
	WEEKLY = 'weekly'
	MONTHLY = 'monthly'

class Habits(models.Model):
	habit_id = models.AutoField(primary_key=True)
	habit_name = models.CharField(max_length=40, blank=False, null=False, unique=True)
	habit_user = models.ForeignKey(
		AppUsers,
		on_delete=models.CASCADE,
		related_name="user_habits",
		default=1
	)
	habit_action = models.CharField(max_length=120, blank=False, null=False)
	habit_streak = models.IntegerField(default=0)
	habit_periodicity_type = models.CharField(
		max_length=7,
		choices=ValidPeriodicityTypes.choices
	)
	habit_periodicity_value = models.PositiveIntegerField(blank=True, null=True)
	created_at = models.DateTimeField(auto_now_add=True)

	class Meta:
		db_table = "habits"
		constraints = [
			UniqueConstraint(fields=["habit_name", "habit_user"], name="unique_habit_per_user")
		]

	def save(self, *args, **kwargs):
		if not self.habit_name.strip():
			raise ValueError("Habit name can not be empty or whitespace.")
		
		habit_periodicity_value_mapping = {
			ValidPeriodicityTypes.DAILY: 1,
			ValidPeriodicityTypes.WEEKLY: 7,
			ValidPeriodicityTypes.MONTHLY: 30,
		}

		if not self.habit_periodicity_value:
			self.habit_periodicity_value = habit_periodicity_value_mapping[self.habit_periodicity_type]
		if (self.habit_periodicity_value <= 0 or self.habit_periodicity_value > 30):
			raise ValueError("Periodicity value must be between 0 and 30.")
		
		super().save(*args, **kwargs)

	def __str__(self):
		return f"{self.habit_name} for user_id{self.user_id}"