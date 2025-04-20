from typing import Literal, Union, Annotated
from pydantic import BaseModel, Field
from enum import Enum

class PeriodicityType(str, Enum):
    daily = 'daily'
    weekly = 'weekly'
    # 3 = 'monthyl'
    def set_default_kvi(self) -> float: #we can already assign a kvi by default here
        return 1.0 if self == PeriodicityType.daily else 7.0


class HabitCreate(BaseModel):
    habit_name: str = Field(..., example="Running")
    habit_action: str = Field(..., example = "Running every week")
    user_id: str = Field(..., example='1')
    periodicity_type: PeriodicityType #acceopts daily or weekly
    habit_goal_name: str
    habit_goal_description: str


class HabitRead(BaseModel): #so these are basically DTO s, what HTTP expects from both client and server side
    habit_name: str
    habit_id: int
    habit_action: str
    habit_streak: int
    habit_periodicity_type: str
    habit_user_id: int


class HabitSummary(BaseModel):
    habit_id_id: int
    habit_name: str