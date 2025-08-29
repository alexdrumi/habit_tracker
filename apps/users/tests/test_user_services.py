import pytest
from   unittest.mock import MagicMock
from   apps.users.services.user_service import UserService, RoleCreationError, UserNotFoundError

@pytest.fixture
def mock_repository():
	"""
	Fixture that returns a MagicMock to simulate the UserRepository.
	See: https://martinxpn.medium.com/mocking-and-fixtures-in-python-87-100-days-of-python-b3812e48f491
	
	Returns:
		MagicMock: A mock repository instance.
	"""
	mock_repo = MagicMock()
	return mock_repo



@pytest.fixture
def user_service(mock_repository):
	"""
	Fixture that instantiates the UserService with a mocked repository.

	Args:
		mock_repository (MagicMock): The mocked repository.

	Returns:
		UserService: Service instance using the mock.
	"""
	return UserService(repository=mock_repository)


def test_create_a_user(user_service, mock_repository):
	"""
    Test creating a user with valid inputs.

	Given:
		- A valid user_name, user_age, user_gender, and user_role.
		- Repository.create_a_user returns a dict with user_id.
	When:
		- user_service.create_a_user is called.
	Then:
		- It should call repository.create_a_user with the same arguments.
		- It should return the dict from the repository.
	"""
	expected_result = {'user_id': 1, 'user_name': "jozsi", 'user_role': "user"}
	mock_repository.create_a_user.return_value = expected_result
	
	result = user_service.create_a_user(user_name="jozsi", user_age=25, user_gender="Male", user_role="user")
	
	mock_repository.create_a_user.assert_called_with("jozsi", 25, "Male", "user")
	assert result == expected_result



def test_create_a_user_with_invalid_inputs(user_service):
	"""
	Test that invalid inputs to create_a_user raise ValueError.

	Cases:
	- Empty user_name
	- Negative user_age
	- Empty user_gender
	- Empty user_role
	"""
	with pytest.raises(ValueError):
		user_service.create_a_user("", 25, "Male", "user")
	with pytest.raises(ValueError):
		user_service.create_a_user("jozsi", -5, "Male", "user")
	with pytest.raises(ValueError):
		user_service.create_a_user("jozsi", 25, "", "user")
	with pytest.raises(ValueError):
		user_service.create_a_user("jozsi", 25, "Male", "")



def test_create_a_user_with_role_error(user_service, mock_repository):
	"""
	Test that create_a_user raises RoleCreationError when role creation fails.
	"""
	side_effect = RoleCreationError("Role error")
	mock_repository.create_a_user.side_effect = side_effect

	with pytest.raises(RoleCreationError):
		user_service.create_a_user("jozsi", 25, "Male", "user")



def test_update_a_user_success(user_service, mock_repository):
	"""
	Test updating an existing user with valid fields.

	Given:
		- user_name exists.
		- Valid optional fields user_age and user_role provided.
	When:
		- user_service.update_a_user is called.
	Then:
		- repository.update_a_user should be called with same args.
		- The returned count should be forwarded.
	"""
	mock_repository.update_a_user.return_value = 1
	result = user_service.update_a_user("teso", user_age=35, user_gender="Male", user_role="admin")

	mock_repository.update_a_user.assert_called_once_with("teso", 35, "Male", "admin")
	assert result == 1



def test_update_a_user_no_fields_returns_zero(user_service, mock_repository):
	"""
	Test updating a user with no fields specified.

	Given:
		- Only user_name passed, no other fields.
	When:
		- user_service.update_a_user is called.
	Then:
		- repository.update_a_user is called with None for optional fields.
		- It returns 0 indicating no update.
	"""
	mock_repository.update_a_user.return_value = 0
	result = user_service.update_a_user("kati")

	mock_repository.update_a_user.assert_called_once_with("kati", None, None, None)
	assert result == 0



def test_update_a_user_invalid_inputs(user_service):
	"""
	Test that invalid inputs to update_a_user raise ValueError.

	Cases:
	- Empty user_name
	- Age out of range
	- Invalid role
	"""
	with pytest.raises(ValueError):
		user_service.update_a_user("", user_age=40)
	with pytest.raises(ValueError):
		user_service.update_a_user("alice", user_age=200)
	with pytest.raises(ValueError):
		user_service.update_a_user("alice", user_role="superuser")


def test_update_a_user_not_found(user_service, mock_repository):
	"""
	Test that updating a non-existent user raises UserNotFoundError.

	Given:
		- repository.update_a_user raises UserNotFoundError.
	When:
		- user_service.update_a_user is called.
	Then:
		- It should propagate UserNotFoundError.
	"""
	mock_repository.update_a_user.side_effect = UserNotFoundError("alice")
	with pytest.raises(UserNotFoundError):
		user_service.update_a_user("alice", user_age=30)



def test_delete_user_success(user_service, mock_repository):
	"""
	Test deleting a user with a valid user_id.

	Given:
		- A positive integer user_id.
		- repository.delete_a_user returns number > 0.
	When:
		- user_service.delete_user is called.
	Then:
		- It should return the deletion count.
	"""
	mock_repository.delete_a_user.return_value = 1
	result = user_service.delete_user(5)

	mock_repository.delete_a_user.assert_called_once_with(5)
	assert result == 1


def test_delete_user_invalid_id(user_service):
	"""
	Test that invalid user_id values raise ValueError in delete_user.

	Invalid IDs:
	- Zero, negative, non-int, None
	"""
	for incorrect_id in [0, -1, "lol", None]:
		with pytest.raises(ValueError):
			user_service.delete_user(incorrect_id)



def test_delete_user_not_found(user_service, mock_repository):
	"""
	Test that deleting a non-existent user raises UserNotFoundError.

	Given:
		- repository.delete_a_user raises UserNotFoundError.
	When:
		- user_service.delete_user is called with that ID.
	Then:
		- It should propagate UserNotFoundError.
	"""
	mock_repository.delete_a_user.side_effect = UserNotFoundError(142)
	with pytest.raises(UserNotFoundError):
		user_service.delete_user(142)



def test_get_user_id_success(user_service, mock_repository):
	"""
	Test retrieving user_id by valid username.

	Given:
		- repository.get_user_id returns an integer.
	When:
		- user_service.get_user_id is called with a valid name.
	Then:
		- It returns that integer.
	"""
	mock_repository.get_user_id.return_value = 89
	result = user_service.get_user_id("teso")

	mock_repository.get_user_id.assert_called_once_with("teso")
	assert result == 89



def test_get_user_id_invalid_name(user_service):
	"""
	Test that invalid username inputs to get_user_id raise ValueError.

	Invalid inputs:
	- Empty string, non-str
	"""
	with pytest.raises(ValueError):
		user_service.get_user_id("")
	with pytest.raises(ValueError):
		user_service.get_user_id(333)



def test_get_user_id_not_found(user_service, mock_repository):
	"""
	Test that querying a nonexistent username raises UserNotFoundError.

	Given:
		- repository.get_user_id raises UserNotFoundError.
	When:
		- user_service.get_user_id is called.
	Then:
		- It propagates UserNotFoundError.
	"""
	mock_repository.get_user_id.side_effect = UserNotFoundError("kelemen")
	with pytest.raises(UserNotFoundError):
		user_service.get_user_id("kelemen")



def test_validate_user_by_name_success(user_service, mock_repository):
	"""
	Test validate_user_by_name returns ID for existing user.

	Given:
		- repository.validate_user_by_name returns an integer.
	When:
		- user_service.validate_user_by_name is called.
	Then:
		- It returns that integer.
	"""
	mock_repository.validate_user_by_name.return_value = 7
	assert user_service.validate_user_by_name("teve") == 7



def test_validate_user_by_name_invalid(user_service):
	"""
	Test that invalid inputs to validate_user_by_name raise ValueError.

	Invalid input: empty string
	"""
	with pytest.raises(ValueError):
		user_service.validate_user_by_name("")



def test_validate_user_by_name_not_found(user_service, mock_repository):
	"""
	Test that validate_user_by_name raises UserNotFoundError if user not in repository.

	Given:
		- repository.validate_user_by_name raises UserNotFoundError.
	When:
		- user_service.validate_user_by_name is called.
	Then:
		- It propagates UserNotFoundError.
	"""
	mock_repository.validate_user_by_name.side_effect = UserNotFoundError("eve")
	with pytest.raises(UserNotFoundError):
		user_service.validate_user_by_name("eve")



def test_validate_user_by_id_success(user_service, mock_repository):
	"""
	Test validate_user_by_id returns the same ID for existing user.

	Given:
		- repository.validate_user_by_id returns an integer.
	When:
		- user_service.validate_user_by_id is called with valid ID.
	Then:
		- It returns that integer.
	"""
	mock_repository.validate_user_by_id.return_value = 8
	assert user_service.validate_user_by_id(8) == 8



def test_validate_user_by_id_invalid(user_service):
	"""
	Test that invalid inputs to validate_user_by_id raise ValueError.

	Invalid input: non-int
	"""
	with pytest.raises(ValueError):
		user_service.validate_user_by_id("foo")



def test_validate_user_by_id_not_found(user_service, mock_repository):
	"""
	Test that validate_user_by_id raises UserNotFoundError if user ID not in repository.

	Given:
		- repository.validate_user_by_id raises UserNotFoundError.
	When:
		- user_service.validate_user_by_id is called.
	Then:
		- It propagates UserNotFoundError.
	"""
	mock_repository.validate_user_by_id.side_effect = UserNotFoundError(8)
	with pytest.raises(UserNotFoundError):
		user_service.validate_user_by_id(8)



def test_query_all_user_data_returns_list(user_service, mock_repository):
	"""
	Test query_all_user_data returns list of tuples from repository.

	Given:
		- repository.query_all_user_data returns a list of (id, name).
	When:
		- user_service.query_all_user_data is called.
	Then:
		- It returns the same list.
	"""
	sample = [(1, "k"), (2, "l")]
	mock_repository.query_all_user_data.return_value = sample
	assert user_service.query_all_user_data() == sample



def test_query_user_and_related_habits_returns_list(user_service, mock_repository):
	"""
	Test query_user_and_related_habits returns joined data from repository.

	Given:
		- repository.query_user_and_related_habits returns joined tuples.
	When:
		- user_service.query_user_and_related_habits is called.
	Then:
		- It returns the same list.
	"""
	sample = [("alice", 1, 10, "jog", "daily")]
	mock_repository.query_user_and_related_habits.return_value = sample
	assert user_service.query_user_and_related_habits() == sample