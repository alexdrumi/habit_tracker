from django.db import models
from apps.habits.models import Habits
from apps.kvi_types.models import KviTypes
from django.core.validators import MinValueValidator
from django.db.models import UniqueConstraint
from django.core.exceptions import ValidationError
from math import isinf, isnan

class Goals(models.Model):
	goal_id = models.AutoField(primary_key=True)
	goal_name = models.CharField(max_length=50)
	habit_id = models.ForeignKey(
		Habits,
		on_delete=models.CASCADE,
		related_name='goals'
	)

	target_kvi_value = models.FloatField(validators=[MinValueValidator(0.0)]) 
	current_kvi_value = models.FloatField(default=0.0)
	goal_description = models.CharField(max_length=80, blank=True)
	created_at = models.DateTimeField(auto_now_add=True)
	deleted_at = models.DateTimeField(blank=True, null=True)

	class Meta:
		db_table = "goals"
		constraints = [
			models.UniqueConstraint(fields=['goal_name', 'habit_id'], name="unique_goal_for_habit_id")
		]
	
	def save(self, *args, **kwargs):
		if not self.goal_name.strip():
			raise ValueError("Goal name can not be empty or whitespace.")
		if isinf(self.target_kvi_value) or isnan(self.target_kvi_value):
			raise ValueError("Invalid KVI value.")
		if self.target_kvi_value < 0.0:
			raise ValueError("Invalid KVI value.")

		super().save(*args, **kwargs)

	def __str__(self):
		return f"Goal name is: {self.goal_name} for habit {self.habit_id}"