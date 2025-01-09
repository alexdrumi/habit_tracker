from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator


'''
CREATE TABLE app_users_roles {
	user_role VARCHAR(10) PRIMARY KEY,
}

INSERT INTO app_users_roles(user_role) VALUES
('user'),
('admin'),
('bot');
'''
class AppUsersRoles(models.Model):

	'''
	Validation logic next to the ForeignKey in AppUsers
	'''
	VALID_ROLES = ['user', 'admin', 'bot']
	user_role = models.CharField(max_length=10, primary_key=True) #no specific enum in django tho

	class Meta:
		db_table = "app_users_role" #the explicit name of the table
	
	def save(self, *args, **kwargs):
		if self.user_role not in self.VALID_ROLES:
			raise ValueError(f"Invalid role: {self.user_role}, user_role must be one of {self.VALID_ROLES}.")
		super().save(*args, **kwargs)
	
	def __str__(self):
		return self.user_role





'''
CREATE TABLE app_users {
	user_id INT AUTO_INCREMENT PRIMARY KEY,
	user_name VARCHAR(100) NOT NULL UNIQUE,
	user_role ENUM('user', 'admin', 'bot') NOT NULL,
	user_age INT CHECK (user_age BETWEEN 1 AND 110), 
	user_gender VARCHAR(100) NULL 
}
'''
# Create your models here.
class AppUsers(models.Model):
	user_id = models.AutoField(primary_key=True)
	user_name = models.CharField(max_length=100, blank=False, null=False, unique=True)
	user_role = models.ForeignKey(
		AppUsersRoles,
		on_delete=models.PROTECT, #dont delete the models in case the role is gone
		related_name="users" #not sure what this does just yet
	)
	user_age = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(110)])
	user_gender = models.CharField(max_length=100, null=True, blank=True)
	created_at = models.DateTimeField(auto_now_add=True)

	class Meta:
		db_table = "app_users"

	def save(self, *args, **kwargs):
		if not self.user_name.strip():  # Check for empty or whitespace-only names
			raise ValueError("User name cannot be empty or whitespace.")
		super().save(*args, **kwargs)

	def __str__(self):
		return f"{self.user_name} (ID={self.user_id})" #prob we should go about ids?

