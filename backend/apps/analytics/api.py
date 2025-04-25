from fastapi import APIRouter, Depends, HTTPException, status
from apps.core.api import get_database, create_habit_controller
from apps.habits.schemas import  HabitCreate, HabitRead, PeriodicityType, HabitSummary
from apps.core.controllers.habit_controller import HabitController
from typing import List
from fastapi.responses import JSONResponse


router = APIRouter(
    prefix="/analytics",
    tags=["analytics"]
)


#return a HabitSummary
@router.get("/get_longest_streak")
def longest_streak_in_database(ctrl: HabitController = Depends(create_habit_controller)):
	try:
		result = ctrl.calculate_longest_streak()
		return result
	except Exception as error:
		raise HTTPException(status_code=400, detail=str(error))



# @router.post("/create_a_new_habit", 
# 			 response_model=HabitRead,
# 			 status_code=status.HTTP_201_CREATED)
# def create_new_habit(
# 	payload: HabitCreate,
# 	ctrl: HabitController = Depends(create_habit_controller)):
	
# 	try:
# 		new_habit = ctrl.create_a_habit_with_validation(
# 			payload.habit_name, 
# 			payload.habit_action, 
# 			payload.periodicity_type, 
# 			payload.user_id)

# 		new_goal = ctrl.create_a_goal(
# 			goal_name=payload.habit_goal_name, 
# 			habit_id=new_habit.habit_id, 
# 			target_kvi_value=payload.periodicity_type.set_default_kvi(), 
# 			current_kvi_value=0.0,
# 			goal_description=payload.habit_goal_description)
	
# 		return new_habit

# 	except Exception as error:
# 		raise HTTPException(status_code=422, detail=str(error))



# #get all the habits
# @router.get("/get_all_habits", response_model=List[HabitRead], status_code=status.HTTP_200_OK)
# def get_all_habits(
# 	ctrl: HabitController = Depends(create_habit_controller)):
# 	try:
# 		all_habits = ctrl.get_all_habits()
# 		# print(f"{all_habits} ARE THE ALL HABITS")
# 		return all_habits
# 	except Exception as error:
# 		raise HTTPException(status_code=400, detail=str(error))


# #tick a habit
# @router.post("/complete_habit")
# def complete_habit(
# 	habit_id: int,
# 	goal_id: int,
# 	ctrl: HabitController = Depends(create_habit_controller)):
# 		try:
# 			ctrl.complete_a_habit(int(habit_id), int(goal_id))
# 			return JSONResponse(
# 				status_code=200,
# 				content={"message": "Habit succesfully completed!"}
# 			)
# 		except Exception as error:
# 			raise HTTPException(status_code=422, detail=str(error))

