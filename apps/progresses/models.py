from django.db import models
from apps.goals.models import Goals
from django.core.validators import MinValueValidator
from math import isinf, isnan
from datetime import date
from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator
from django.db import models
from math import isinf, isnan



class Progresses(models.Model):
	progress_id = models.AutoField(primary_key=True)
	goal_id = models.ForeignKey(
		Goals,
		on_delete=models.SET_NULL,
		related_name='goal_progresses',
		null=True,
		blank=True
	)
	progress_description = models.CharField(max_length=30, blank=True, null=True)
	current_kvi_value = models.FloatField(validators=[MinValueValidator(0.0)], default=0.0)
	distance_from_goal_kvi_value = models.FloatField(validators=[MinValueValidator(0.0)], default=0.0)
	current_streak = models.IntegerField(default=0)
	occurence_date = models.DateTimeField(auto_now_add=True)
	goal_name = models.CharField(max_length=60, blank=True, null=True, default=None)
	habit_name = models.CharField(max_length=60, blank=True, null=True, default=None)

	class Meta:
		db_table = "progresses"
	
	def save(self, *args, **kwargs):
		if isinf(self.goal_id.current_kvi_value) or isnan(self.goal_id.current_kvi_value):
			raise ValueError("Invalid KVI value.")
		if self.goal_id.current_kvi_value < 0.0:
			raise ValueError("Invalid KVI value.")
		self.current_kvi_value = self.goal_id.current_kvi_value
		self.distance_from_goal_kvi_value = self.goal_id.target_kvi_value - self.goal_id.current_kvi_value
		super().save(*args, **kwargs)

def __str__(self):
	return (f"Progress ID: {self.progress_id} | Date: {self.occurence_date} | "
		f"Current KVI: {self.current_kvi_value} | Distance from Goal: {self.distance_from_goal_kvi_value}")