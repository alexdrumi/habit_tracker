from fastapi import APIRouter, Depends, HTTPException, status
from apps.core.api import get_database, create_habit_controller
from .schemas import  HabitCreate, HabitRead, PeriodicityType
from apps.core.controllers.habit_controller import HabitController
from typing import List

router = APIRouter(
    prefix='/habits',
    tags = ['habits']
)


@router.post("/create_a_new_habit", 
			 response_model=HabitRead,
			 status_code=status.HTTP_201_CREATED)
def create_new_habit(
	payload: HabitCreate,
	ctrl: HabitController = Depends(create_habit_controller)):
	
	try:
		new_habit = ctrl.create_a_habit_with_validation(
			payload.habit_name, 
			payload.habit_action, 
			payload.periodicity_type, 
			payload.user_id)
		
		print(type(new_habit))
		print(new_habit)
		new_goal = ctrl.create_a_goal(
			goal_name=payload.habit_goal_name, 
			habit_id=new_habit.habit_id, 
			target_kvi_value=payload.periodicity_type.set_default_kvi(), 
			current_kvi_value=0.0,
			goal_description=payload.habit_goal_description)
	
		return new_habit

	except Exception as error:
		raise HTTPException(status_code=422, detail=str(error))

