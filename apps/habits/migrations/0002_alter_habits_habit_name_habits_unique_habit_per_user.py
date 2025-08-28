
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('habits', '0001_initial'),
        ('users', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='habits',
            name='habit_name',
            field=models.CharField(max_length=40, unique=True),
        ),
        migrations.AddConstraint(
            model_name='habits',
            constraint=models.UniqueConstraint(fields=('habit_name', 'habit_user'), name='unique_habit_per_user'),
        ),
    ]
