from django.db import models
from apps.goals.models import Goals



# Create your models here.
class Progresses(models.Model):
    progress_id = models.AutoField(primary_key=True)
    goal_id = models.ForeignKey(
        Goals,
        on_delete=models.CASCADE #delete the progress if the goal is deleted
        related_name='goal_progresses'
    )
    