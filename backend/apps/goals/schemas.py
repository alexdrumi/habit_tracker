from typing import Literal, Union, Annotated
from pydantic import BaseModel, Field
from enum import Enum
from apps.habits.schemas import HabitCreate, HabitRead, PeriodicityType, HabitSummary
from datetime import datetime

'''
query = "SELECT goal_name, goal_id, habit_id_id, habit_name from goals INNER JOIN habits ON goals.habit_id_id = habits.habit_id;"
'''


class GoalsAndRelatedHabits(BaseModel):
    goal_name: str
    goal_id: int
    related_habit: HabitSummary


class GoalsRead(BaseModel):
    goal_id: int
    habit_id: int
    target_kvi_value: float
    current_kvi_value: float
    goal_name: str
    occurence_date: datetime