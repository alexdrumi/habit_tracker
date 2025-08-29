import django.core.validators
import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('goals', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Progresses',
            fields=[
                ('progress_id', models.AutoField(primary_key=True, serialize=False)),
                ('current_kvi_value', models.FloatField(validators=[django.core.validators.MinValueValidator(0.0)])),
                ('progress_description', models.CharField(blank=True, max_length=30, null=True)),
                ('occurence_date', models.DateField(auto_now_add=True)),
                ('goal_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='goal_progresses', to='goals.goals')),
            ],
            options={
                'db_table': 'progresses',
            },
        ),
    ]
