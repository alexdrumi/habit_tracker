import pytest
from apps.users.services.user_service import UserService
from apps.habits.services.habit_service import HabitService
from apps.users.repositories.user_repository import AlreadyExistError, UserNotFoundError
from apps.habits.repositories.habit_repository import HabitNotFoundError, HabitAlreadyExistError

#dummy repo for users
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

#dummy repo for habit
class DummyHabitRepository:
	def __init__(self):
		self.habits = {}
		self.next_id = 1

	def create_a_habit(self, habit_name, habit_action, habit_streak, habit_periodicity_type, habit_periodicity_value, habit_user_id):
		#simulate a duplicate
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
		#for integration, simulate that id is 1
		if habit_id not in self.habits:
			raise HabitNotFoundError(habit_id)
		return 1


@pytest.fixture
def dummy_user_repo():
	return DummyUserRepository()

@pytest.fixture
def user_service(dummy_user_repo):
	return UserService(dummy_user_repo)

@pytest.fixture
def dummy_habit_repo():
	return DummyHabitRepository()

@pytest.fixture
def habit_service(dummy_habit_repo):
	return HabitService(dummy_habit_repo)


def test_integration_create_user_and_habit(user_service, habit_service):
	user = user_service.create_a_user("jozsi", 35, "male", "user")
	user_id = user["user_id"]

	habit = habit_service.create_a_habit("morning sleepback", "sleepback for 2 hours", "daily", user_id)
	assert habit["habit_id"] == 1
	assert habit["habit_name"] == "morning sleepback"  
	assert habit["habit_periodicity_type"].lower() == "daily"  



def test_create_duplicate_user(user_service):
	user_service.create_a_user("aliz", 30, "female", "user")  
	with pytest.raises(AlreadyExistError):
		user_service.create_a_user("aliz", 30, "female", "user")   
  
def test_create_duplicate_habit_same_user(habit_service, user_service):
	user = user_service.create_a_user("peti", 40, "male", "user")
	habit_service.create_a_habit("yoga", "morning yoga", "daily", user["user_id"])  
	with pytest.raises(HabitAlreadyExistError):
		habit_service.create_a_habit("yoga", "morning yoga", "daily", user["user_id"])  

def test_create_same_habit_different_user(user_service, habit_service):
	user1 = user_service.create_a_user("nori", 31, "female", "user")
	user2 = user_service.create_a_user("zoli", 42, "male", "user")
	   
	habit1 = habit_service.create_a_habit("read book", "read 3 pages", "daily", user1["user_id"])
	habit2 = habit_service.create_a_habit("read book", "read 3 pages", "daily", user2["user_id"])
 
	assert habit1["habit_id"] == 1   
	assert habit2["habit_id"] == 2 




#better below 

# @pytest.fixture
# def dummy_user_repo():
#     from apps.users.repositories.user_repository import UserNotFoundError, AlreadyExistError
#     class DummyUserRepository:
#         def __init__(self):
#             self.users = {}
#             self.next_id = 1
#         def create_a_user(self, name, age, gender, role):
#             if name in self.users:
#                 raise AlreadyExistError(name)
#             u = {'user_id': self.next_id, 'user_name': name}
#             self.users[name] = u
#             self.next_id += 1
#             return u
#         def get_user_id(self, name):
#             if name in self.users:
#                 return self.users[name]['user_id']
#             raise UserNotFoundError(name)
#         def validate_user_by_name(self, name): return self.get_user_id(name)
#         def validate_user_by_id(self, uid):
#             for u in self.users.values():
#                 if u['user_id'] == uid: return uid
#             raise UserNotFoundError(uid)
#         def query_all_user_data(self): return []
#         def query_user_and_related_habits(self): return []
#     return DummyUserRepository()

# @pytest.fixture
# def dummy_habit_repo():
#     from apps.habits.repositories.habit_repository import HabitNotFoundError, HabitAlreadyExistError
#     class DummyHabitRepository:
#         def __init__(self):
#             self.habits = {}
#             self.next_id = 1
#         def create_a_habit(self, name, action, streak, periodicity_type, periodicity_value, user_id):
#             for h in self.habits.values():
#                 if h['habit_name']==name and h['habit_user_id']==user_id:
#                     raise HabitAlreadyExistError(name, user_id)
#             h = {'habit_id': self.next_id, 'habit_name': name, 'habit_action': action,
#                  'habit_streak': streak, 'habit_periodicity_type': periodicity_type,
#                  'habit_periodicity_value': periodicity_value, 'habit_user_id': user_id}
#             self.habits[self.next_id] = h
#             self.next_id += 1
#             return h
#         def validate_a_habit(self, hid):
#             if hid not in self.habits: raise HabitNotFoundError(hid)
#             return hid
#         def update_habit_field(self, hid, field, val):
#             if hid not in self.habits: raise HabitNotFoundError(hid)
#             self.habits[hid][field] = val
#             return 1
#         def get_all_habits(self):
#             return [(h['habit_id'], h['habit_name'], h['habit_action'], h['habit_user_id'])
#                     for h in self.habits.values()]
#         def get_habit_id(self, user_id, name):
#             for h in self.habits.values():
#                 if h['habit_user_id']==user_id and h['habit_name']==name:
#                     return h['habit_id']
#             raise HabitNotFoundError(name)
#         def get_current_streak(self, habit_id):
#             if habit_id not in self.habits: raise HabitNotFoundError(habit_id)
#             return (self.habits[habit_id]['habit_streak'],)
#         def get_goal_of_habit(self, habit_id):
#             if habit_id not in self.habits: raise HabitNotFoundError(habit_id)
#             return [999]
#         def delete_a_habit(self, habit_id, goal_id=None):
#             if habit_id not in self.habits: raise HabitNotFoundError(habit_id)
#             del self.habits[habit_id]
#             return 1
#     return DummyHabitRepository()

# @pytest.fixture
# def user_service(dummy_user_repo):
#     return UserService(repository=dummy_user_repo)

# @pytest.fixture
# def habit_service(user_service, dummy_habit_repo):
#     return HabitService(repository=dummy_habit_repo)

# def test_integration_update_habit_streak_and_retrieve(user_service, habit_service, dummy_habit_repo):
#     """
#     Test updating a habit’s streak and retrieving it end-to-end.

#     Given:
#         - A user and habit exist in dummy repos.
#     When:
#         - habit_service.update_habit_streak and get_current_streak are called.
#     Then:
#         - The streak is updated and returned correctly.
#     """
#     user = user_service.create_a_user("anna", 28, "female", "user")
#     habit = habit_service.create_a_habit("meditate", "sit still", "daily", user["user_id"])
#     hid = habit["habit_id"]

#     rows = habit_service.update_habit_streak(hid, 3)
#     assert rows == 1
#     assert dummy_habit_repo.habits[hid]["habit_streak"] == 3

#     streak = habit_service.get_current_streak(hid)
#     assert streak == (3,)

# def test_integration_get_all_habits_for_user(user_service, habit_service):
#     """
#     Test retrieving all habits after multiple creations.

#     Given:
#         - A user creates two habits.
#     When:
#         - habit_service.get_all_habits is called.
#     Then:
#         - Both habits appear in the result.
#     """
#     user = user_service.create_a_user("bram", 33, "male", "user")
#     uid = user["user_id"]
#     h1 = habit_service.create_a_habit("run", "jog", "daily", uid)
#     h2 = habit_service.create_a_habit("code", "1hr", "daily", uid)

#     all_h = habit_service.get_all_habits()
#     ids = {h[0] for h in all_h}
#     assert h1["habit_id"] in ids and h2["habit_id"] in ids

# def test_integration_delete_habit_by_name_and_fail_on_next_lookup(user_service, habit_service):
#     """
#     Test deleting a habit by name and ensuring lookups thereafter fail.

#     Given:
#         - A user and a habit exist.
#     When:
#         - habit_service.delete_a_habit is called.
#     Then:
#         - Deletion succeeds and get_habit_id thereafter raises HabitNotFoundError.
#     """
#     user = user_service.create_a_user("carl", 40, "male", "user")
#     uid = user["user_id"]
#     habit = habit_service.create_a_habit("read", "read nightly", "daily", uid)

#     deleted = habit_service.delete_a_habit("carl", "read")
#     assert deleted == 1

#     with pytest.raises(HabitNotFoundError):
#         habit_service.get_habit_id(uid, "read")

# def test_integration_delete_user_then_habit_ops_fail(user_service, habit_service):
#     """
#     Test that deleting a user blocks subsequent habit operations.

#     Given:
#         - A user is created and then deleted.
#     When:
#         - habit_service.create_a_habit or get_habit_id is called with that user’s ID.
#     Then:
#         - UserNotFoundError is raised.
#     """
#     user = user_service.create_a_user("dana", 29, "female", "user")
#     uid = user["user_id"]
#     user_service.delete_user(uid)

#     with pytest.raises(UserNotFoundError):
#         habit_service.create_a_habit("journal", "write", "daily", uid)
#     with pytest.raises(UserNotFoundError):
#         habit_service.get_habit_id(uid, "journal")