import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('goals', '0002_remove_goals_kvi_type_id_alter_goals_created_at_and_more'),
        ('progresses', '0004_progresses_current_streak'),
    ]

    operations = [
        migrations.AlterField(
            model_name='progresses',
            name='goal_id',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='goal_progresses', to='goals.goals'),
        ),
    ]
