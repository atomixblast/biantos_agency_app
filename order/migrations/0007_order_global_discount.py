import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('order', '0006_articleorder_unit_price'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='global_discount',
            field=models.FloatField(
                default=0.0, help_text='Remise sur toute la commande, en %',
                validators=[django.core.validators.MinValueValidator(0), django.core.validators.MaxValueValidator(100)],
            ),
        ),
    ]
