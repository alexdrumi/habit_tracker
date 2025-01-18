from django.db import models
from apps.users.models import AppUsers
# Create your models here.

'''
CREATE TABLE habits {
	habit_id INT PRIMARY KEY,
	habit_name VARCHAR(40),
	user_id INT UNIQUE,
	habit_action VARCHAR(80),
	periodicity_type 
}
'''
# Table habits {
#   habit_id int [primary key]
#   habit_name varchar
#   user_id int
#   created_at timestamp
#   habit_action varchar
#   habit_streak int
#   habit_periodicity_type varchar  // e.g., 'day', 'week', etc.
#   habit_periodicity_value int     // e.g., 1 for daily, 7 for weekly
# }

class ValidPeriodicityTypes(models.TextChoices):
	DAILY = 'daily'
	WEEKLY = 'weekly'
	MONTHLY = 'monthly'

class Habits(models.Model):
	habit_id = models.AutoField(primary_key=True)
	habit_name = models.CharField(max_length=40, blank=False, null=False) #could more habit be created w the same name? maybe if for different users  
	habit_user = models.ForeignKey(
		AppUsers,
		on_delete=models.CASCADE, #delete the habit if the user is deleted
		related_name="user_habits",
		default=1 #default habituser id
	)
	habit_action = models.CharField(max_length=120, blank=False, null=False)
	habit_streak = models.IntegerField(default=0) #should be 0 at initialization
	habit_periodicity_type = models.CharField( #no need for complete different class just enum is enough
		max_length=7,
		choices=ValidPeriodicityTypes.choices
	)
	habit_periodicity_value = models.PositiveIntegerField(blank=True, null=True) #will be mapped automatically
	created_at = models.DateTimeField(auto_now_add=True)

	class Meta:
		db_table = "habits"

	def save(self, *args, **kwargs):
		if not self.habit_name.strip(): #check for empty name or whitespaces etc
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