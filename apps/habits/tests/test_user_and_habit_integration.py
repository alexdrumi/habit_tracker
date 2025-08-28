import pytest
from apps.users.services.user_service import UserService
from apps.habits.services.habit_service import HabitService
from apps.users.repositories.user_repository import AlreadyExistError, UserNotFoundError
from apps.habits.repositories.habit_repository import HabitNotFoundError, HabitAlreadyExistError

class DummyUserRepository:
	def __init__(self):
		self.users = {}
		self.next_id = 1



	def create_a_user(self, user_name, user_age, user_gender, user_role):  
		if user_name in self.users:  
			raise AlreadyExistError(user_name)
		user = {
			'user_id': self.next_id,
			'user_name': user_name,
			'user_age': user_age,
			'user_gender': user_gender,
			'user_role': user_role,
		}
		self.users[user_name] = user
		self.next_id += 1
		return user



	def get_user_id(self, user_name):
		if user_name in self.users:
			return self.users[user_name]['user_id']
		from apps.users.repositories.user_repository import UserNotFoundError
		raise UserNotFoundError(user_name)



	def validate_user_by_name(self, user_name):
		return self.get_user_id(user_name)



	def validate_user_by_id(self, user_id):
		for user in self.users.values():
			if user['user_id'] == user_id:
				return user_id
		from apps.users.repositories.user_repository import UserNotFoundError
		raise UserNotFoundError(user_id)



	def query_all_user_data(self):
		return [(user['user_id'], user['user_name']) for user in self.users.values()]



	def query_user_and_related_habits(self):
		return []



class DummyHabitRepository:
	def __init__(self):
		self.habits = {}
		self.next_id = 1



	def create_a_habit(self, habit_name, habit_action, habit_streak, habit_periodicity_type, habit_periodicity_value, habit_user_id):
		for habit in self.habits.values():
			if habit["habit_name"]== habit_name and habit["habit_user_id"] == habit_user_id:  
				raise HabitAlreadyExistError(habit_name, habit_user_id)
		habit = {
			'habit_id': self.next_id, 
			'habit_name': habit_name,   
			'habit_action': habit_action,
			'habit_streak': habit_streak,  
			'habit_periodicity_type': habit_periodicity_type,
			'habit_periodicity_value': habit_periodicity_value,  
			'habit_user_id': habit_user_id,  
		} 
		self.habits[self.next_id]= habit
		self.next_id += 1
		return habit

  

	def validate_a_habit(self, habit_id):
		if habit_id not in self.habits:  
			raise HabitNotFoundError(habit_id)
		return habit_id



	def update_habit_field(self, habit_id, field, value):
		if habit_id not in self.habits:
			raise HabitNotFoundError(habit_id)
		self.habits[habit_id][field] = value
		return 1



	def get_all_habits(self):
		return [(h["habit_id"], h["habit_name"], h["habit_action"], h["habit_user_id"]) for h in self.habits.values()]  

 

	def get_habit_id(self, user_id, habit_name): 
		for habit in self.habits.values():
			if habit["habit_user_id"] == user_id and habit["habit_name"]== habit_name:
				return habit["habit_id"]
		raise HabitNotFoundError(habit_name)



	def get_periodicity_type(self, habit_id):
		if habit_id not in self.habits:
			raise HabitNotFoundError(habit_id)
		return self.habits[habit_id]['habit_periodicity_type']



	def query_all_habits(self):
		return self.get_all_habits()



	def delete_a_habit(self, habit_id, goal_id=None):
		if habit_id not in self.habits:
			raise HabitNotFoundError(habit_id)
		del self.habits[habit_id]
		return 1



	def get_goal_of_habit(self, habit_id):
		if habit_id not in self.habits:
			raise HabitNotFoundError(habit_id)
		return 1


	def get_current_streak(self, habit_id):
		if not isinstance(habit_id, int) or habit_id <= 0: 
			raise ValueError(f"Invalid habit id: {habit_id}.")
		
		validated_habit_id = self.validate_a_habit(habit_id)
		streak = self._repository.get_current_streak(habit_id=validated_habit_id)
		
		return streak



@pytest.fixture
def dummy_user_repo():
	return DummyUserRepository()



@pytest.fixture
def user_service(dummy_user_repo):
	return UserService(dummy_user_repo)



@pytest.fixture
def habit_service(dummy_habit_repo):
	return HabitService(dummy_habit_repo)


@pytest.fixture
def dummy_habit_repo():
	return DummyHabitRepository()



def test_integration_create_user_and_habit(user_service, habit_service):
	"""
	Test full flow: create a user, then create a habit tied to that user.

	Given:
		- A DummyUserRepository and DummyHabitRepository.
	When:
		- user_service.create_a_user is called.
		- habit_service.create_a_habit is called with the returned user_id.
	Then:
		- Habit is created and returns a dict containing that user_id.
	"""
	
	user = user_service.create_a_user("jozsi", 35, "male", "user")
	user_id = user["user_id"]

	habit = habit_service.create_a_habit("morning sleepback", "sleepback for 2 hours", "daily", user_id)
	assert habit["habit_id"] == 1
	assert habit["habit_name"] == "morning sleepback"  
	assert habit["habit_periodicity_type"].lower() == "daily"  



def test_create_duplicate_user(user_service):
	"""
	Test for creating the same user twice which fails.

	Given:
		- user_service pointed at DummyUserRepository.
	When:
		- create_a_user called twice with same name.
	Then:
		- AlreadyExistError is raised on the second call.
	"""
	user_service.create_a_user("aliz", 30, "female", "user")  
	with pytest.raises(AlreadyExistError):
		user_service.create_a_user("aliz", 30, "female", "user")   



def test_create_duplicate_habit_same_user(habit_service, user_service):
	"""
	Test for same habit name for the same user, which cannot be created twice.

	Given:
		- A user exists.
	When:
		- create_a_habit called twice with same name/user_id.
	Then:
		- HabitAlreadyExistError is raised on second call.
	"""
	user = user_service.create_a_user("peti", 40, "male", "user")
	habit_service.create_a_habit("yoga", "morning yoga", "daily", user["user_id"])  
	with pytest.raises(HabitAlreadyExistError):
		habit_service.create_a_habit("yoga", "morning yoga", "daily", user["user_id"])  



def test_create_same_habit_different_user(user_service, habit_service):
	"""
	Test that two different users can each create a habit with the same name.

	Given:
		- Two distinct users.
	When:
		- Each creates a habit with identical name.
	Then:
		- Both succeed with different habit_id.
	"""
	user1 = user_service.create_a_user("nori", 31, "female", "user")
	user2 = user_service.create_a_user("zoli", 42, "male", "user")
	   
	habit1 = habit_service.create_a_habit("read book", "read 3 pages", "daily", user1["user_id"])
	habit2 = habit_service.create_a_habit("read book", "read 3 pages", "daily", user2["user_id"])
 
	assert habit1["habit_id"] == 1   
	assert habit2["habit_id"] == 2 

