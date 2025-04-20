from fastapi import APIRouter, Depends, HTTPException, status
from apps.core.api import get_database, create_habit_controller
from .schemas import  HabitCreate, HabitRead, PeriodicityType
from apps.core.controllers.habit_controller import HabitController
from typing import List
from fastapi.responses import JSONResponse


router = APIRouter(
    prefix="/analytics",
    tags=["analytics"]
)

