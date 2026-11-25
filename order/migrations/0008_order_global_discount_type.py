import django.core.validators
from django.db import migrations, models


def backfill_amount(apps, schema_editor):
    """Montant de la remise commande = remises totales − remises par article."""
    Order = apps.get_model('order', 'Order')
    ArticleOrder = apps.get_model('order', 'ArticleOrder')
    for order in Order.objects.filter(global_discount__gt=0):
        lines = sum(l.qty * l.unit_price * l.discount / 100 for l in ArticleOrder.objects.filter(order=order))
        order.global_discount_amount = round(order.discount - lines, 2)
        order.save(update_fields=['global_discount_amount'])


class Migration(migrations.Migration):

    dependencies = [
        ('order', '0007_order_global_discount'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='global_discount_type',
            field=models.CharField(choices=[('PERCENT', '%'), ('AMOUNT', 'FCFA')], default='PERCENT', max_length=10),
        ),
        migrations.AddField(
            model_name='order',
            name='global_discount_amount',
            field=models.FloatField(default=0.0),
        ),
        migrations.AlterField(
            model_name='order',
            name='global_discount',
            field=models.FloatField(
                default=0.0, help_text='Remise sur toute la commande (en % ou en FCFA selon le type)',
                validators=[django.core.validators.MinValueValidator(0)],
            ),
        ),
        migrations.RunPython(backfill_amount, migrations.RunPython.noop),
    ]
