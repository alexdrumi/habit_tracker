from fastapi import APIRouter, Depends, HTTPException, status
from apps.core.api import get_database, create_habit_controller
from .schemas import UserCreate, UserRead
from apps.core.controllers.habit_controller import HabitController
from typing import List

#we create a router for the user, will be  included in the app (main.py)
router = APIRouter(
	prefix = '/users',
	tags = ['users']
)

#create
@router.post("/create_user", response_model=UserRead, status_code=status.HTTP_201_CREATED)
def create_user(
	payload: UserCreate,
	ctrl: HabitController = Depends(create_habit_controller)):

	try:
		return ctrl.create_user(payload.user_name, 
						  payload.user_age, 
						  payload.user_gender, 
						  payload.user_role)
	except ValueError as error:
		raise HTTPException(status_code=422, detail=str(error))


#query existing users
#query = "SELECT user_id, user_name, user_age, user_role_id FROM app_users;"

@router.get("/query_all_users", response_model=List[UserRead], status_code=status.HTTP_200_OK)
def query_all_users(ctrl: HabitController = Depends(create_habit_controller)):
	try:
		result = ctrl.query_all_users()
		return result
	except Exception as error:
		raise HTTPException(status_code=400, detail=str(error))

