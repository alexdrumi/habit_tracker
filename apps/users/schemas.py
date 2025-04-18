from typing import Literal, Union

from typing import Annotated

from pydantic import BaseModel, Field, schema_json_of


class UserCreate(BaseModel):
    user_name: str = Field(..., example="Beno")
    user_age: int = Field(..., ge=1, le=110, example=30)
    user_gender: str = Field(..., example='female')
    user_role: str = Field(..., example='user')

class UserRead(BaseModel):
    user_id: int
    user_name: str
    user_role: str