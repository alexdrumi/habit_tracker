from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from apps.users.models import AppUsers
from django.db.models import UniqueConstraint

'''
CREATE TABLE kvi_types {
	kvi_type_id INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
	kvi_type_name VARCHAR(20) NOT NULL,
	kvi_description VARCHAR(50) NULL,
	kvi_multiplier DOUBLE NOT NULL,
}
'''
class KviTypes(models.Model):
	kvi_type_id = models.AutoField(primary_key=True)
	kvi_type_name = models.CharField(max_length=20, blank=False, null=False, unique=True) #if kvi name exist, we should 
	kvi_description = models.CharField(max_length=40, blank=True, null=True)
	kvi_multiplier = models.FloatField(
		validators=[MinValueValidator(0.0), MaxValueValidator(10.0)]
	)

	kvi_type_user = models.ForeignKey(
		AppUsers,
		on_delete=models.CASCADE,
		related_name = "user_kvi_type",
		null=True #temporarily nullable
	)

	class Meta:
		db_table = "kvi_types"
		constraints = [
			UniqueConstraint(fields=["kvi_type_name", "kvi_type_user"], name="unique_kvi_type_per_user")
		]

	def save(self, *args, **kwargs):
		#could write a clean function but for now this works, empty name wont get saved and throws exception
		if not self.kvi_type_name.strip():
			raise ValueError("KVI type name can not be empty, please enter maximum 20 characters long type.\nExample: mood, steps.")
		super().save(*args, **kwargs)
	
	def __str__(self):
		return f"{self.kvi_type_name} with multiplier of: {self.kvi_multiplier})"
