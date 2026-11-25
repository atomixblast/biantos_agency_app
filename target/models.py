from decimal import Decimal

from django.core.exceptions import ValidationError
from django.db import models


class Target(models.Model):
    """Objectif de vente sur une période, en quantité ou en chiffre d'affaires."""

    METRIC_QUANTITY = 'QUANTITY'
    METRIC_REVENUE = 'REVENUE'
    METRICS = (
        (METRIC_QUANTITY, 'Quantité'),
        (METRIC_REVENUE, "Chiffre d'affaires"),
    )

    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    metric = models.CharField(max_length=20, choices=METRICS, default=METRIC_QUANTITY)
    target_value = models.DecimalField(max_digits=14, decimal_places=2)
    article = models.ForeignKey(
        'order.Article', on_delete=models.CASCADE, related_name='targets',
        null=True, blank=True,
    )
    sales_executive = models.ForeignKey(
        'order.SalesExecutive', on_delete=models.SET_NULL, related_name='targets',
        null=True, blank=True,
    )
    start_date = models.DateField()
    end_date = models.DateField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Objectif"
        verbose_name_plural = "Objectifs"
        ordering = ['-start_date', 'name']

    def __str__(self):
        return self.name

    @property
    def is_quantity(self):
        return self.metric == self.METRIC_QUANTITY

    @property
    def unit(self):
        return 'unités' if self.is_quantity else 'FCFA'

    def clean(self):
        errors = {}
        if self.start_date and self.end_date and self.start_date > self.end_date:
            errors['end_date'] = "La date de fin doit être postérieure ou égale à la date de début."
        if self.target_value is not None and self.target_value <= Decimal('0'):
            errors['target_value'] = "L'objectif doit être supérieur à zéro."
        if self.metric == self.METRIC_QUANTITY and not self.article_id:
            errors['article'] = "Un article est obligatoire pour un objectif en quantité."
        if errors:
            raise ValidationError(errors)
