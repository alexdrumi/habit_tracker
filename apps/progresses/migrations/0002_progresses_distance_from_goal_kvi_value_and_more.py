import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('progresses', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='progresses',
            name='distance_from_goal_kvi_value',
            field=models.FloatField(default=0.0, validators=[django.core.validators.MinValueValidator(0.0)]),
        ),
        migrations.AlterField(
            model_name='progresses',
            name='current_kvi_value',
            field=models.FloatField(default=0.0, validators=[django.core.validators.MinValueValidator(0.0)]),
        ),
    ]
