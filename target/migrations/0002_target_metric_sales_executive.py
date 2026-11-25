import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('order', '0005_article_photo_customer_photo_salesexecutive_photo'),
        ('target', '0001_initial'),
    ]

    operations = [
        migrations.RenameField(
            model_name='target',
            old_name='quantity',
            new_name='target_value',
        ),
        migrations.AlterField(
            model_name='target',
            name='target_value',
            field=models.DecimalField(decimal_places=2, max_digits=14),
        ),
        migrations.AddField(
            model_name='target',
            name='metric',
            field=models.CharField(
                choices=[('QUANTITY', 'Quantité'), ('REVENUE', "Chiffre d'affaires")],
                default='QUANTITY', max_length=20,
            ),
        ),
        migrations.AlterField(
            model_name='target',
            name='article',
            field=models.ForeignKey(
                blank=True, null=True, on_delete=django.db.models.deletion.CASCADE,
                related_name='targets', to='order.article',
            ),
        ),
        migrations.AddField(
            model_name='target',
            name='sales_executive',
            field=models.ForeignKey(
                blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL,
                related_name='targets', to='order.salesexecutive',
            ),
        ),
        migrations.AlterModelOptions(
            name='target',
            options={'ordering': ['-start_date', 'name'], 'verbose_name': 'Objectif', 'verbose_name_plural': 'Objectifs'},
        ),
    ]
