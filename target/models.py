from django.db import models

from order.models import ArticleOrder

# Create your models here.
class Target(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    article = models.ForeignKey('order.Article', on_delete=models.CASCADE, related_name='targets')
    quantity = models.FloatField(default=0.0)
    start_date = models.DateField()
    end_date = models.DateField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name


    def get_article_count_for_target(self):
        return ArticleOrder.objects.filter(article=self.article, order__ordered_at__range=(self.start_date, self.end_date)).aggregate(total_quantity=models.Sum('qty'))['total_quantity'] or 0

    
    def get_article_subcount_for_target(self):
        return self.quantity - self.get_article_count_for_target()