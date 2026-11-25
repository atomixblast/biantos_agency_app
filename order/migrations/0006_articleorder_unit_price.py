from django.db import migrations, models


def backfill(apps, schema_editor):
    """Fige le prix des lignes existantes et recalcule la remise de chaque commande.

    Les commandes passées n'avaient pas de prix figé : on reprend le prix actuel
    de l'article (meilleure information disponible). La remise de la commande
    devient la somme des remises de ses lignes.
    """
    ArticleOrder = apps.get_model('order', 'ArticleOrder')
    Order = apps.get_model('order', 'Order')

    for line in ArticleOrder.objects.select_related('article').filter(unit_price__isnull=True):
        line.unit_price = line.article.sale_price
        line.save(update_fields=['unit_price'])

    for order in Order.objects.all():
        discount = sum(
            l.qty * l.unit_price * l.discount / 100
            for l in ArticleOrder.objects.filter(order=order)
        )
        if order.discount != discount:
            order.discount = discount
            order.save(update_fields=['discount'])


class Migration(migrations.Migration):

    dependencies = [
        ('order', '0005_article_photo_customer_photo_salesexecutive_photo'),
    ]

    operations = [
        migrations.AddField(
            model_name='articleorder',
            name='unit_price',
            field=models.FloatField(blank=True, help_text='Prix unitaire au moment de la commande', null=True),
        ),
        migrations.AlterField(
            model_name='articleorder',
            name='discount',
            field=models.FloatField(default=0.0, help_text='Remise de la ligne, en %'),
        ),
        migrations.RunPython(backfill, migrations.RunPython.noop),
    ]
