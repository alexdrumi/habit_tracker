from apps.users.repositories.user_repository import UserRepository


class UserService:
	def __init__(self):
		self._repository = UserRepository()

	def create_a_user(self, user_name, user_age, user_gender, user_role):
		user = self._repository.create_a_user(user_name, user_age, user_gender, user_role)
	
	def delete_a_user(self, user_id):
		deleted = self._repository.delete_a_user(user_id)

	def update_a_user(self, user_name, user_age=None, user_gender=None, user_role=None):
		updated = self._repository.update_a_user(user_name, user_age, user_gender, user_role)