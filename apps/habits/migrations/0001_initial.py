
import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('users', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Habits',
            fields=[
                ('habit_id', models.AutoField(primary_key=True, serialize=False)),
                ('habit_name', models.CharField(max_length=40)),
                ('habit_action', models.CharField(max_length=120)),
                ('habit_streak', models.IntegerField(default=0)),
                ('habit_periodicity_type', models.CharField(choices=[('daily', 'Daily'), ('weekly', 'Weekly'), ('monthly', 'Monthly')], max_length=7)),
                ('habit_periodicity_value', models.PositiveIntegerField(blank=True, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('habit_user', models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, related_name='user_habits', to='users.appusers')),
            ],
            options={
                'db_table': 'habits',
            },
        ),
    ]
