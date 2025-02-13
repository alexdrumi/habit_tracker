import pytest
from unittest.mock import MagicMock
from apps.users.services.user_service import UserService, UserNotFoundError, RoleCreationError


#https://docs.python.org/3/library/unittest.mock.html
@pytest.fixture
def mock_repository():
	mock_repo = MagicMock()
	return mock_repo



@pytest.fixture
def user_service(mock_repository):
	return UserService(repository=mock_repository)



def test_create_a_user(user_service, mock_repository):
	'''Test user service user creation'''
	expected_result = {'user_id': 1, 'user_name': "jozsi", 'user_role': "user"}
	#assign the expected results to the mock repo return value
	mock_repository.create_a_user.return_value = expected_result
	
	#create user with the same info
	result = user_service.create_a_user("jozsi", 25, "Male", "user")
	
	#This method is a convenient way of asserting that the last call has been made in a particular way: (from the docs, https://docs.python.org/3/library/unittest.mock.html)
	mock_repository.create_a_user.assert_called_with("jozsi", 25, "Male", "user")

	#just call an assert, if this fails would throw an error
	assert result == {'user_id': 1, 'user_name': "jozsi", 'user_role': "user"}



def test_create_a_user_with_invalid_inputs(user_service):
	'''Test that creating user raises ValueError for invalid input values.'''

	#all of the tests below pass if it throws an error in cases which they are expected to fail
	#empty name
	with pytest.raises(ValueError):
		user_service.create_a_user("", 25, "Male", "user")
	#invalid age
	with pytest.raises(ValueError):
		user_service.create_a_user("jozsi", -5, "Male", "user")
	#empty gender
	with pytest.raises(ValueError):
		user_service.create_a_user("jozsi", 25, "", "user")
	#empty role
	with pytest.raises(ValueError):
		user_service.create_a_user("jozsi", 25, "Male", "")



#from docs: An example of a mock that raises an exception (to test exception handling of an API):
def test_create_a_user_with_role_error(user_service, mock_repository):
	'''Test that a RoleCreationError is correctly implemented.'''
	side_effect = RoleCreationError("Role error")
	mock_repository.create_a_user.side_effect = side_effect

	with pytest.raises(RoleCreationError):
		user_service.create_a_user("jozsi", 25, "Male", "user")


