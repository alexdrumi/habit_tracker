from django.db import models
from apps.goals.models import Goals
from django.core.validators import MinValueValidator
from math import isinf, isnan
from datetime import date


from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator
from django.db import models
from math import isinf, isnan



# Create your models here.
class Progresses(models.Model):
	progress_id = models.AutoField(primary_key=True)
	goal_id = models.ForeignKey(
		Goals,
		on_delete=models.CASCADE, #delete the progress if the goal is deleted
		related_name='goal_progresses'
	)
	progress_description = models.CharField(max_length=30, blank=True, null=True)
	current_kvi_value = models.FloatField(validators=[MinValueValidator(0.0)], default=0.0)
	distance_from_goal_kvi_value = models.FloatField(validators=[MinValueValidator(0.0)], default=0.0)
	occurence_date = models.DateField(auto_now_add=True)

	class Meta:
		db_table = "progresses"
		#should there be any unique constrain here?pro not
	
	def save(self, *args, **kwargs):

		if isinf(self.goal_id.current_kvi_value) or isnan(self.goal_id.current_kvi_value):  #mysql would throw tantrum here
			raise ValueError("Invalid KVI value.")
		if self.goal_id.current_kvi_value < 0.0: #technically this would be validation error but for now its fine, most likely redundant, simple
			raise ValueError("Invalid KVI value.")
		
		self.current_kvi_value = self.goal_id.current_kvi_value
		self.distance_from_goal_kvi_value = self.goal_id.target_kvi_value - self.goal_id.current_kvi_value
		#no need to check the kvi probably, goal tester and constrain already checks that
		super().save(*args, **kwargs)

def __str__(self):
	return (f"Progress ID: {self.progress_id} | Date: {self.occurence_date} | "
		f"Current KVI: {self.current_kvi_value} | Distance from Goal: {self.distance_from_goal_kvi_value}")