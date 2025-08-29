
import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('habits', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Analytics',
            fields=[
                ('analytics_id', models.AutoField(primary_key=True, serialize=False)),
                ('times_completed', models.IntegerField(default=0)),
                ('streak_length', models.IntegerField(default=0)),
                ('last_completed_at', models.DateField(blank=True, null=True)),
                ('created_at', models.TimeField(auto_now_add=True)),
                ('habit_id', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='habit_analytics', to='habits.habits')),
            ],
            options={
                'db_table': 'analytics',
            },
        ),
    ]
