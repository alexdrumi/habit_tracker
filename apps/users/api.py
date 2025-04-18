from fastapi import FastAPI

#importing api router
app = FastAPI()

#use the get method first

#we create a router

router = APIRouter(
    prefix = '/users'
    tags = ['user related functions']
)


#calling userinfo funcion

@router.get('get_users')
def get_all_users():
    return "message": "we get all users here"


@app.get('/')
def home():
    return {
        "message": "we are in the home page"
    }