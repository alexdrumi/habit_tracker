
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('kvi_types', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='kvitypes',
            name='kvi_type_name',
            field=models.CharField(max_length=20, unique=True),
        ),
    ]
