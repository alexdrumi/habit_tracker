
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('goals', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='goals',
            name='kvi_type_id',
        ),
        migrations.AlterField(
            model_name='goals',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True),
        ),
        migrations.AlterField(
            model_name='goals',
            name='deleted_at',
            field=models.DateTimeField(blank=True, null=True),
        ),
    ]
