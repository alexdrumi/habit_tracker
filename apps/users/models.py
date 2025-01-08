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
	user_role = models.CharField(max_length=10, primary_key=True) #no specific enum in django tho

	class Meta:
		db_table = "app_users_role" #the explicit name of the table
	
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
	user_name = models.CharField(max_length=100, blank=False, unique=True)
	user_role = models.ForeignKey(
		AppUsersRoles,
		on_delete=models.CASCADE, #delete app_users if the role is deleted
		related_name="users" #not sure what this does just yet
	)
	user_age = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(110)])
	user_gender = models.CharField(max_length=100, null=True, blank=True)
	created_at = models.DateTimeField(auto_now_add=True)

	class Meta:
		db_table = "app_users"

	def __str__(self):
		return f"{self.user_name} (ID={self.user_id})" #prob we should go about ids?

