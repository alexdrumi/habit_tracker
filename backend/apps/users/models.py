from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils.translation import gettext_lazy as _  #marks strings for translation


class ValidRoles(models.TextChoices):
	USER = 'user', _('User')
	ADMIN = 'admin', _('Admin')
	BOT = 'bot', _('Bot')



class AppUsersRoles(models.Model):
	user_role = models.CharField(
		max_length=10,
		primary_key=True,
		unique=True,
		choices=ValidRoles.choices,
		verbose_name="User Role"
	)

	class Meta:
		db_table = "app_users_role"

	def save(self, *args, **kwargs):
		role_values = [role.value for role in ValidRoles]
		if self.user_role not in role_values:
			raise ValueError(
				f"Invalid role: {self.user_role}. Must be one of {role_values}."
			)
		super().save(*args, **kwargs)

	def __str__(self):
		return self.user_role



class AppUsers(models.Model):
	user_id = models.AutoField(primary_key=True)
	user_name = models.CharField(max_length=100, unique=True)
	user_password = models.CharField(max_length=25, blank=True, null=True)
	user_role = models.ForeignKey(
		AppUsersRoles,
		on_delete=models.PROTECT,
		related_name="users",
		verbose_name="User Role"
	)
	user_age = models.IntegerField(
		validators=[MinValueValidator(1), MaxValueValidator(110)],
		verbose_name="User Age"
	)
	user_gender = models.CharField(max_length=20, blank=True, null=True)
	created_at = models.DateTimeField(auto_now_add=True)

	class Meta:
		db_table = "app_users"

	def save(self, *args, **kwargs):
		if not self.user_name.strip():
			raise ValueError("User name cannot be empty or whitespace.")
		if self.user_password:
			if not self.user_password.strip():
				raise ValueError("Password cannot be empty or whitespace.")
			if not (5 <= len(self.user_password) <= 25):
				raise ValueError("Password must be between 5 and 25 characters.")
		super().save(*args, **kwargs)

	def __str__(self):
		return f"{self.user_name} (ID={self.user_id})"
