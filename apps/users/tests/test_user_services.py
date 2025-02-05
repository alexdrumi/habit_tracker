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
	"""Test user service user creation"""
	expected_result = {'user_id': 1, 'user_name': "jozsi", 'user_role': "user"}
	mock_repository.create_a_user.return_value = expected_result
	
	result = user_service.create_a_user("jozsi", 25, "Male", "user")
	
	mock_repository.create_a_user.assert_called_with("jozsi", 25, "Male", "user")
	assert result == {'user_id': 1, 'user_name': "jozsi", 'user_role': "user"}



def test_create_a_user_with_role_error(user_service, mock_repository):
	side_effect = RoleCreationError('Role error')
	mock_repository.create_a_user.side_effect = side_effect

	with pytest.raises(RoleCreationError): #this should raise a role creation error
		user_service.create_a_user("jozsi", 25, "Male", "user")
