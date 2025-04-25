from fastapi import APIRouter, Depends, HTTPException, status
from apps.core.api import get_database, create_habit_controller
from .schemas import GoalsAndRelatedHabits
from apps.core.controllers.habit_controller import HabitController
from typing import List

router = APIRouter(
    prefix = "/goals",
    tags = ["goals"]
)




#get list of tickable habits
@router.get("/list_tickable_habits",
			response_model=List[GoalsAndRelatedHabits],
			status_code=status.HTTP_200_OK)
def fetch_ready_to_tick_goals(ctrl: HabitController = Depends(create_habit_controller)):
	try:
		tickable_habits_and_goals = ctrl.fetch_ready_to_tick_goals_of_habits()
		return tickable_habits_and_goals
	except Exception as error:
		raise HTTPException(status_code=400, detail=str(error))


@router.get("/get_goals_and_habits",
			response_model=List[GoalsAndRelatedHabits],
			status_code=status.HTTP_200_OK)
def list_all_goals_with_habits(ctrl: HabitController = Depends(create_habit_controller)):
	try:
		goals_and_related_habits = ctrl.query_goals_and_related_habits()
		return goals_and_related_habits
	except Exception as error:
		raise HTTPException(status_code=400, detail=str(error))
