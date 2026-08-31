from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from decimal import Decimal
import json

from .models import Order, Customer, SalesExecutive, Article, ArticleOrder

User = get_user_model()


class OrderModelTest(TestCase):
    """Tests pour le modèle Order"""
    
    def setUp(self):
        self.customer = Customer.objects.create(
            name="Test Customer",
            tel="0123456789"
        )
        self.sales_executive = SalesExecutive.objects.create(
            name="Test Sales Executive",
            tel="0987654321"
        )
        self.article1 = Article.objects.create(
            name="Article 1",
            ref="ART001",
            sale_price=1000.0
        )
        self.article2 = Article.objects.create(
            name="Article 2",
            ref="ART002",
            sale_price=2000.0
        )
        
    def test_customer_str(self):
        """Test de la méthode __str__ de Customer"""
        self.assertEqual(str(self.customer), "Test Customer")
    
    def test_sales_executive_str(self):
        """Test de la méthode __str__ de SalesExecutive"""
        self.assertEqual(str(self.sales_executive), "Test Sales Executive")
    
    def test_article_str(self):
        """Test de la méthode __str__ de Article"""
        self.assertEqual(str(self.article1), "Article 1 (ART001)")
    
    def test_order_creation(self):
        """Test de création d'une commande"""
        order = Order.objects.create(
            name="Test Order",
            state="PENDING",
            total=3000.0,
            discount=0.0,
            cashed=0.0,
            json_repr=[],
            ordered_at="2025-09-30",
            customer=self.customer,
            sales_executive=self.sales_executive
        )
        self.assertEqual(order.name, "Test Order")
        self.assertEqual(order.state, "PENDING")
        self.assertEqual(order.total, 3000.0)
    
    def test_order_with_articles(self):
        """Test de commande avec articles"""
        order = Order.objects.create(
            name="Test Order with Articles",
            state="PENDING",
            total=3000.0,
            discount=0.0,
            cashed=0.0,
            json_repr=[],
            ordered_at="2025-09-30",
            customer=self.customer
        )
        
        # Ajouter des articles
        ArticleOrder.objects.create(
            article=self.article1,
            order=order,
            qty=2,
            discount=10.0
        )
        ArticleOrder.objects.create(
            article=self.article2,
            order=order,
            qty=1,
            discount=0.0
        )
        
        # Vérifier les articles
        self.assertEqual(order.articles.count(), 2)
        self.assertEqual(ArticleOrder.objects.filter(order=order).count(), 2)


class OrderViewTest(TestCase):
    """Tests pour les vues de commande"""
    
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            email='test@example.com',
            username='testuser',
            password='testpass123'
        )
        self.customer = Customer.objects.create(
            name="Test Customer",
            tel="0123456789"
        )
        self.article = Article.objects.create(
            name="Test Article",
            ref="TEST001",
            sale_price=1000.0
        )
        
    def test_list_orders_requires_login(self):
        """Test que la liste des commandes nécessite une authentification"""
        response = self.client.get(reverse('order:list_orders'))
        self.assertEqual(response.status_code, 302)  # Redirect to login
    
    def test_list_orders_authenticated(self):
        """Test de la liste des commandes avec authentification"""
        self.client.login(email='test@example.com', password='testpass123')
        response = self.client.get(reverse('order:list_orders'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'order/list.html')
    
    def test_create_order_get(self):
        """Test de l'affichage du formulaire de création"""
        response = self.client.get(reverse('order:create_order'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'order/add.html')
        self.assertIn('form', response.context)
        self.assertIn('articles', response.context)
    
    def test_create_order_post_valid(self):
        """Test de création d'une commande valide"""
        json_repr = json.dumps([
            {
                'id': self.article.id,
                'designation': self.article.name,
                'qty': 2,
                'discount': 10,
                'pu': float(self.article.sale_price)
            }
        ])
        
        response = self.client.post(reverse('order:create_order'), {
            'name': 'Test Order',
            'state': 'PENDING',
            'ordered_at': '2025-09-30',
            'customer': self.customer.id,
            'cashed': 0,
            'discount': 0,
            'json_repr': json_repr
        })
        
        self.assertEqual(response.status_code, 302)  # Redirect after success
        self.assertEqual(Order.objects.count(), 1)
        
        order = Order.objects.first()
        self.assertEqual(order.name, 'Test Order')
        # Total should be: 2 * 1000 * (1 - 0.10) = 1800
        self.assertEqual(order.total, 1800.0)
    
    def test_update_order_get(self):
        """Test de l'affichage du formulaire de mise à jour"""
        order = Order.objects.create(
            name="Test Order",
            state="PENDING",
            total=1000.0,
            discount=0.0,
            cashed=0.0,
            json_repr=[],
            ordered_at="2025-09-30",
            customer=self.customer
        )
        
        response = self.client.get(reverse('order:update_order', args=[order.id]))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'order/update.html')
        self.assertIn('form', response.context)
        self.assertIn('order', response.context)
        self.assertIn('articles', response.context)
        self.assertIn('existing_articles', response.context)


class ArticleOrderTest(TestCase):
    """Tests pour le modèle ArticleOrder"""
    
    def setUp(self):
        self.customer = Customer.objects.create(
            name="Test Customer",
            tel="0123456789"
        )
        self.article = Article.objects.create(
            name="Test Article",
            ref="TEST001",
            sale_price=1000.0
        )
        self.order = Order.objects.create(
            name="Test Order",
            state="PENDING",
            total=1000.0,
            discount=0.0,
            cashed=0.0,
            json_repr=[],
            ordered_at="2025-09-30",
            customer=self.customer
        )
    
    def test_article_order_creation(self):
        """Test de création d'un ArticleOrder"""
        article_order = ArticleOrder.objects.create(
            article=self.article,
            order=self.order,
            qty=5,
            discount=15.0
        )
        
        self.assertEqual(article_order.qty, 5)
        self.assertEqual(article_order.discount, 15.0)
        self.assertEqual(str(article_order), f"Test Article x5 - Commande #{self.order.id}")
    
    def test_article_order_relationship(self):
        """Test des relations ArticleOrder"""
        ArticleOrder.objects.create(
            article=self.article,
            order=self.order,
            qty=3,
            discount=10.0
        )
        
        # Vérifier la relation many-to-many
        self.assertIn(self.article, self.order.articles.all())
        self.assertEqual(self.order.articleorder_set.count(), 1)
