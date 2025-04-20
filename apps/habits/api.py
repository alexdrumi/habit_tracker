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

		new_goal = ctrl.create_a_goal(
			goal_name=payload.habit_goal_name, 
			habit_id=new_habit.habit_id, 
			target_kvi_value=payload.periodicity_type.set_default_kvi(), 
			current_kvi_value=0.0,
			goal_description=payload.habit_goal_description)
	
		return new_habit

	except Exception as error:
		raise HTTPException(status_code=422, detail=str(error))



#get all the habits
@router.get("/get_all_habits", response_model=List[HabitRead], status_code=status.HTTP_200_OK)
def get_all_habits(
	ctrl: HabitController = Depends(create_habit_controller)):
	try:
		all_habits = ctrl.get_all_habits()
		# print(f"{all_habits} ARE THE ALL HABITS")
		return all_habits
	except Exception as error:
		raise HTTPException(status_code=400, detail=str(error))


# #list goals and habits
# @router.get("/get_goals_and_habits")
# def list_all_goals_with_habits(ctrl: HabitController = Depends(create_habit_controller)):
# 	try:
# 		goals_and_related_habits = ctrl.query_goals_and_related_habits()
# 		return goals_and_related_habits
# 	except Exception as error:
# 		raise HTTPException(status_code=400, detail=str(error))


# #get list of tickable habits
# @router.get("/list_tickable_habits")
# def fetch_ready_to_tick_goals(ctrl: HabitController = Depends(create_habit_controller)):
# 	try:
# 		tickable_habits_and_goals = ctrl.fetch_ready_to_tick_goals_of_habits()
# 		return tickable_habits_and_goals
# 	except Exception as error:
# 		raise HTTPException(status_code=400, detail=str(error))
