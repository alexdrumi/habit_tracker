# Generated by Django 5.1.4 on 2025-03-10 11:09

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('progresses', '0005_alter_progresses_goal_id'),
    ]

    operations = [
        migrations.AddField(
            model_name='progresses',
            name='goal_name',
            field=models.CharField(blank=True, default=None, max_length=60, null=True),
        ),
        migrations.AddField(
            model_name='progresses',
            name='habit_name',
            field=models.CharField(blank=True, default=None, max_length=60, null=True),
        ),
    ]
