from django.db import models

from authentication.models import User

# Create your models here.


class Customer(models.Model):
    name = models.CharField(max_length=255)
    tel = models.CharField(max_length=255)
    photo = models.ImageField(upload_to='customers/', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Client"
        verbose_name_plural = "Clients"


class SalesExecutive(models.Model):
    name = models.CharField(max_length=255)
    tel = models.CharField(max_length=255)
    photo = models.ImageField(upload_to='sales_executives/', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Apporteur d'affaire"
        verbose_name_plural = "Apporteurs d'affaires"


class Article(models.Model):
    name = models.CharField(max_length=255)
    ref = models.CharField(max_length=255, unique=True)
    sale_price = models.FloatField(default=0.0)
    photo = models.ImageField(upload_to='articles/', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name} ({self.ref})"

    class Meta:
        verbose_name = "Article"
        verbose_name_plural = "Articles"


class Order(models.Model):

    STATES = (
        ('PENDING', 'Réalisation en cours'),
        ('DONE', 'Fait'),
        ('CANCELED', 'Annulé'),
    )    

    name = models.CharField(max_length=255)
    state = models.CharField(max_length=255, choices=STATES)
    description = models.TextField(blank=True, null=True)
    total = models.FloatField(default=0.0)
    discount = models.FloatField(default=0.0)
    cashed = models.FloatField(default=0.0)
    json_repr = models.JSONField()

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    ordered_at = models.DateField()
    state_date = models.DateField(blank=True, null=True)

    # user = models.ForeignKey(User, on_delete=models.CASCADE)
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, null=True, blank=True)
    sales_executive = models.ForeignKey(SalesExecutive, on_delete=models.CASCADE, null=True, blank=True)
    articles = models.ManyToManyField(Article, through='ArticleOrder')


    def get_total_without_discount(self):
        return self.total + self.discount
    
    def get_total_with_discount(self):
        return self.total
    
    def get_total_paid(self):
        """Retourne le total des paiements effectués"""
        return sum(payment.amount for payment in self.payments.all())
    
    def get_remaining_amount(self):
        """Retourne le montant restant à payer"""
        return self.total - self.get_total_paid()
    
    def is_fully_paid(self):
        """Vérifie si la commande est entièrement payée"""
        return self.get_remaining_amount() <= 0
    
    def is_partially_paid(self):
        """Vérifie si la commande est partiellement payée"""
        total_paid = self.get_total_paid()
        return total_paid > 0 and total_paid < self.total
    
    def get_payment_status(self):
        """Retourne le statut de paiement"""
        if self.is_fully_paid():
            return 'PAID'
        elif self.is_partially_paid():
            return 'PARTIAL'
        else:
            return 'UNPAID'

    def __str__(self):
        return f"{self.name} - {self.get_state_display()}"

    class Meta:
        verbose_name = "Commande"
        verbose_name_plural = "Commandes"
        ordering = ['-created_at']


class ArticleOrder(models.Model):
    article = models.ForeignKey(Article, on_delete=models.CASCADE)
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    discount = models.FloatField(default=0.0)
    qty = models.PositiveIntegerField(default=0)

    def __str__(self):
        return f"{self.article.name} x{self.qty} - Commande #{self.order.id}"

    class Meta:
        verbose_name = "Article de commande"
        verbose_name_plural = "Articles de commande"


class Payment(models.Model):
    """Modèle pour gérer les paiements en plusieurs fois"""
    
    PAYMENT_METHODS = (
        ('CASH', 'Espèces'),
        ('BANK_TRANSFER', 'Virement bancaire'),
        ('CHECK', 'Chèque'),
        ('MOBILE_MONEY', 'Mobile Money'),
        ('CARD', 'Carte bancaire'),
        ('OTHER', 'Autre'),
    )
    
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='payments')
    amount = models.FloatField(help_text="Montant du paiement")
    payment_date = models.DateField(help_text="Date du paiement")
    payment_method = models.CharField(max_length=50, choices=PAYMENT_METHODS, default='CASH')
    reference = models.CharField(max_length=255, blank=True, null=True, help_text="Référence du paiement (numéro de chèque, transaction, etc.)")
    notes = models.TextField(blank=True, null=True, help_text="Notes ou commentaires sur le paiement")
    
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"Paiement de {self.amount} FCFA - Commande #{self.order.id} - {self.get_payment_method_display()}"
    
    class Meta:
        verbose_name = "Paiement"
        verbose_name_plural = "Paiements"
        ordering = ['-payment_date', '-created_at']

