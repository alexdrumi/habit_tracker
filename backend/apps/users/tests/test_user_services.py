import pytest
from unittest.mock import MagicMock
from apps.users.services.user_service import UserService, RoleCreationError

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
	mock_repository.create_a_user.return_value = expected_result
	
	result = user_service.create_a_user(user_name="jozsi", user_age=25, user_gender="Male", user_role="user")
	
	mock_repository.create_a_user.assert_called_with("jozsi", 25, "Male", "user")
	assert result == expected_result



def test_create_a_user_with_invalid_inputs(user_service):
	'''Test that creating a user raises ValueError for invalid inputs.'''
	#eempty name
	with pytest.raises(ValueError):
		user_service.create_a_user("", 25, "Male", "user")
	#invalid age
	with pytest.raises(ValueError):
		user_service.create_a_user("jozsi", -5, "Male", "user")
	# empty gender
	with pytest.raises(ValueError):
		user_service.create_a_user("jozsi", 25, "", "user")
	#empty role
	with pytest.raises(ValueError):
		user_service.create_a_user("jozsi", 25, "Male", "")



def test_create_a_user_with_role_error(user_service, mock_repository):
	'''Test that a RoleCreationError is correctly raised.'''
	side_effect = RoleCreationError("Role error")
	mock_repository.create_a_user.side_effect = side_effect

	with pytest.raises(RoleCreationError):
		user_service.create_a_user("jozsi", 25, "Male", "user")
