from django.db import models
from apps.habits.models import Habits
from apps.kvi_types.models import KviTypes
from django.core.validators import MinValueValidator
from django.db.models import UniqueConstraint
from django.core.exceptions import ValidationError
from math import isinf, isnan

# Create your models here.
'''
CREATE TABLE Goals {
	goal_id INT PRIMARY KEY
	goal_name VARCHAR(50) UNIQUE NOT NULL 
	habit_id 
}
'''
class Goals(models.Model):
	#maybe add a field like deadline
	#kvi type id references kvi types tables, ensure the relation is defined
	#a goal should be unique for a certain habit thus check if the habits id for this exact 'goal' is not in the table yet
	#unique combo os goal name and habit id
	#in case habit is deleted the goal also should be soft deleted
	goal_id = models.AutoField(primary_key=True)
	goal_name = models.CharField(max_length=50) #cant have the same goals
	habit_id = models.ForeignKey(
		Habits,
		on_delete=models.CASCADE, #goals are deleted if the habit associated with goals are deleted
		related_name='goals'
		# default=1 #maybe needed for test later?
	)
	# kvi_type_id = models.ForeignKey(
	# 	KviTypes,
	# 	on_delete=models.PROTECT, #cant delete
	# 	related_name='goals'
	# )
	target_kvi_value = models.FloatField(validators=[MinValueValidator(0.0)]) #cant be neg, this is for: 'walking' goal have 1.0 multiplier, and my goal is 5.0, i would need 5 'periodicity_value' amount of successful habit completion to comlpete my goal
	current_kvi_value = models.FloatField(default=0.0)
	goal_description = models.CharField(max_length=80, blank=True)
	created_at = models.DateTimeField(auto_now_add=True)
	deleted_at = models.DateTimeField(blank=True, null=True) #empty for now, maybe used for statistics later.

	class Meta:
		db_table = "goals"
		constraints = [
			#https://docs.djangoproject.com/en/5.1/ref/models/constraints/
			models.UniqueConstraint(fields=['goal_name', 'habit_id'], name="unique_goal_for_habit_id") #cant have the same goals for the same habit
		]
	
	def save(self, *args, **kwargs):
		if not self.goal_name.strip(): #check for empty name or whitespaces etc
			raise ValueError("Goal name can not be empty or whitespace.")
		if isinf(self.target_kvi_value) or isnan(self.target_kvi_value):  #mysql would throw tantrum here
			raise ValueError("Invalid KVI value.")
		if self.target_kvi_value < 0.0: #technically this would be validation error but for now its fine, simple
			raise ValueError("Invalid KVI value.")

		#shall we also check  target_kvi_value to be limited?
		super().save(*args, **kwargs)

	def __str__(self):
		return f"Goal name is: {self.goal_name} for habit {self.habit_id}"