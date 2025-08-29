from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('progresses', '0003_alter_progresses_occurence_date'),
    ]

    operations = [
        migrations.AddField(
            model_name='progresses',
            name='current_streak',
            field=models.IntegerField(default=0),
        ),
    ]
