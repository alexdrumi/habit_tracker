from django.db import models
from apps.goals.models import Goals
from django.core.validators import MinValueValidator
from math import isinf, isnan
from datetime import date


# Create your models here.
class Progresses(models.Model):
	progress_id = models.AutoField(primary_key=True)
	goal_id = models.ForeignKey(
		Goals,
		on_delete=models.CASCADE, #delete the progress if the goal is deleted
		related_name='goal_progresses'
	)
	current_kvi_value = models.FloatField(validators=[MinValueValidator(0.0)])
	progress_description = models.CharField(max_length=30, blank=True, null=True)
	occurence_date = models.DateField(auto_now_add=True)

	class Meta:
		db_table = "progresses"
		#should there be any unique constrain here?
	
	def save(self, *args, **kwargs):
		if not self.current_kvi_value:
			self.current_kvi_value = self.goal_id.current_kvi_value
		if isinf(self.current_kvi_value) or isnan(self.current_kvi_value):  #mysql would throw tantrum here
			raise ValueError("Invalid KVI value.")
		if self.current_kvi_value < 0.0: #technically this would be validation error but for now its fine, most likely redundant, simple
			raise ValueError("Invalid KVI value.")

		#no need to check the kvi, goal tester and constrain already checks that
		super().save(*args, **kwargs)

	def __str__(self):
		return f"Progress ID: {self.progress_id} is created at: {self.occurence_date} with current kvi_value: {self.current_kvi_value}."