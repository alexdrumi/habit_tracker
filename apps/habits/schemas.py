class UserCreate(BaseModel):
    user_name: str = Field(..., example="Beno")
    user_age: int = Field(..., ge=1, le=110, example=30)
    user_gender: str = Field(..., example='female')
    user_role: str = Field(..., example='user')


class UserRead(BaseModel): #so these are basically DTO s, what HTTP expects from both client and server side
    user_id: int
    user_name: str
    user_age: int
    user_role: str