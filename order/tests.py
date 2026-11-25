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
        self.client.force_login(self.user)
        response = self.client.get(reverse('order:create_order'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'order/add.html')
        self.assertIn('form', response.context)
        self.assertIn('articles', response.context)
    
    def test_create_order_post_valid(self):
        """Test de création d'une commande valide"""
        self.client.force_login(self.user)
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
        self.client.force_login(self.user)
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



class FrozenPriceAndDiscountTest(TestCase):
    """Prix figé à la commande et remise par article"""

    def setUp(self):
        self.user = User.objects.create_user(email='p@example.com', username='p', password='testpass123')
        self.client.force_login(self.user)
        self.mug = Article.objects.create(name="Tasse", ref="T1", sale_price=1000.0)
        self.cap = Article.objects.create(name="Casquette", ref="C1", sale_price=2000.0)

    def post_order(self, url, lines):
        return self.client.post(url, {
            'name': 'Cmd', 'state': 'PENDING', 'ordered_at': '2026-12-01',
            'json_repr': json.dumps(lines),
        })

    def test_create_freezes_price_and_sums_line_discounts(self):
        self.post_order(reverse('order:create_order'), [
            {'id': self.mug.id, 'qty': 2, 'discount': 10, 'pu': 1},  # prix client ignoré
            {'id': self.cap.id, 'qty': 1, 'discount': 0},
        ])
        order = Order.objects.get()
        self.assertEqual(order.total, 3800.0)       # 2000 - 10 % + 2000
        self.assertEqual(order.discount, 200.0)     # somme des remises de lignes
        self.assertEqual(order.get_total_without_discount(), 4000.0)
        self.assertEqual(ArticleOrder.objects.get(article=self.mug).unit_price, 1000.0)

    def test_price_change_does_not_affect_existing_order(self):
        self.post_order(reverse('order:create_order'), [{'id': self.mug.id, 'qty': 2, 'discount': 0}])
        order = Order.objects.get()

        self.mug.sale_price = 1500.0
        self.mug.save()

        # Modification de la commande : la tasse garde son prix, le nouvel article prend le prix actuel.
        self.post_order(reverse('order:update_order', args=[order.id]), [
            {'id': self.mug.id, 'qty': 3, 'discount': 0},
            {'id': self.cap.id, 'qty': 1, 'discount': 50},
        ])
        order.refresh_from_db()
        self.assertEqual(ArticleOrder.objects.get(order=order, article=self.mug).unit_price, 1000.0)
        self.assertEqual(order.total, 3 * 1000.0 + 1000.0)

        # Le détail et la facture utilisent le prix figé.
        response = self.client.get(reverse('order:order_detail', args=[order.id]))
        mug_line = next(l for l in response.context['articles_details'] if l['article'] == self.mug)
        self.assertEqual(mug_line['unit_price'], 1000.0)

    def test_invalid_discount_rejected(self):
        self.post_order(reverse('order:create_order'), [{'id': self.mug.id, 'qty': 1, 'discount': 150}])
        self.assertEqual(Order.objects.count(), 0)

    def test_create_requires_login(self):
        self.client.logout()
        response = self.client.get(reverse('order:create_order'))
        self.assertEqual(response.status_code, 302)


class GlobalDiscountTest(TestCase):
    """Remise sur toute la commande, en plus des remises par article"""

    def setUp(self):
        self.user = User.objects.create_user(email='g@example.com', username='g', password='testpass123')
        self.client.force_login(self.user)
        self.mug = Article.objects.create(name="Tasse", ref="T1", sale_price=1000.0)

    def post(self, url, global_discount, lines):
        return self.client.post(url, {
            'name': 'Cmd', 'state': 'PENDING', 'ordered_at': '2026-12-01',
            'global_discount': global_discount, 'json_repr': json.dumps(lines),
        })

    def test_global_discount_applied_after_line_discounts(self):
        # 10 × 1000 = 10 000 ; −10 % par article = 9 000 ; −5 % sur la commande = 8 550
        self.post(reverse('order:create_order'), 5, [{'id': self.mug.id, 'qty': 10, 'discount': 10}])
        order = Order.objects.get()
        self.assertEqual(order.total, 8550.0)
        self.assertEqual(order.discount, 1450.0)
        self.assertEqual(order.get_lines_discount(), 1000.0)
        self.assertEqual(order.get_global_discount_amount(), 450.0)
        self.assertEqual(order.get_total_without_discount(), 10000.0)

    def test_update_changes_global_discount(self):
        self.post(reverse('order:create_order'), 0, [{'id': self.mug.id, 'qty': 2, 'discount': 0}])
        order = Order.objects.get()
        self.post(reverse('order:update_order', args=[order.id]), 50, [{'id': self.mug.id, 'qty': 2, 'discount': 0}])
        order.refresh_from_db()
        self.assertEqual(order.total, 1000.0)

        response = self.client.get(reverse('order:generate_invoice', args=[order.id]))
        self.assertContains(response, 'Remise sur la commande (50 %)')

    def test_global_discount_over_100_rejected(self):
        self.post(reverse('order:create_order'), 150, [{'id': self.mug.id, 'qty': 1, 'discount': 0}])
        self.assertEqual(Order.objects.count(), 0)


class GlobalDiscountAmountAndReportTest(TestCase):
    """Remise sur la commande en montant FCFA, et remises dans le bilan"""

    def setUp(self):
        self.user = User.objects.create_user(email='a@example.com', username='a', password='testpass123')
        self.client.force_login(self.user)
        self.mug = Article.objects.create(name="Tasse", ref="T1", sale_price=1000.0)

    def post(self, value, kind, lines):
        return self.client.post(reverse('order:create_order'), {
            'name': 'Cmd', 'state': 'PENDING', 'ordered_at': '2026-12-01',
            'global_discount': value, 'global_discount_type': kind, 'json_repr': json.dumps(lines),
        })

    def test_amount_discount(self):
        # 10 000 − 10 % par article = 9 000 ; − 1 500 FCFA sur la commande = 7 500
        self.post(1500, 'AMOUNT', [{'id': self.mug.id, 'qty': 10, 'discount': 10}])
        order = Order.objects.get()
        self.assertEqual(order.total, 7500.0)
        self.assertEqual(order.global_discount_amount, 1500.0)
        self.assertEqual(order.get_lines_discount_amount(), 1000.0)
        self.assertEqual(order.get_global_discount_label(), 'Remise sur la commande')

    def test_amount_greater_than_total_rejected(self):
        self.post(5000, 'AMOUNT', [{'id': self.mug.id, 'qty': 2, 'discount': 0}])
        self.assertEqual(Order.objects.count(), 0)

    def test_amount_above_100_allowed_but_percent_not(self):
        self.post(150, 'AMOUNT', [{'id': self.mug.id, 'qty': 1, 'discount': 0}])
        self.assertEqual(Order.objects.get().total, 850.0)
        self.post(150, 'PERCENT', [{'id': self.mug.id, 'qty': 1, 'discount': 0}])
        self.assertEqual(Order.objects.count(), 1)

    def test_report_discount_stats_and_csv(self):
        self.post(1500, 'AMOUNT', [{'id': self.mug.id, 'qty': 10, 'discount': 10}])
        self.post(0, 'PERCENT', [{'id': self.mug.id, 'qty': 1, 'discount': 0}])
        Order.objects.filter(total=1000.0).update(state='CANCELED')

        ctx = self.client.get(reverse('order:report_orders')).context
        self.assertEqual(ctx['total_gross'], 11000.0)
        self.assertEqual(ctx['total_lines_discount'], 1000.0)
        self.assertEqual(ctx['total_global_discount'], 1500.0)
        self.assertEqual(ctx['orders_with_discount'], 1)
        self.assertEqual(ctx['orders_cancelled'], 1)

        filtered = self.client.get(reverse('order:report_orders'), {'state': 'CANCELED'}).context
        self.assertEqual(filtered['total_orders'], 1)

        csv_text = self.client.get(reverse('order:export_report_excel')).content.decode('utf-8-sig')
        self.assertIn('Remise commande (FCFA)', csv_text)
        self.assertIn('1 500.00', csv_text)


class HomePageTest(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(email='h@example.com', username='h', password='testpass123')

    def test_home_redirects_to_targets(self):
        self.client.force_login(self.user)
        self.assertRedirects(self.client.get('/'), reverse('target:list_targets'))

    def test_login_redirects_to_targets_and_ignores_external_next(self):
        response = self.client.post(reverse('authentication:login') + '?next=https://evil.example.com/',
                                    {'username': 'h@example.com', 'password': 'testpass123'})
        self.assertRedirects(response, reverse('target:list_targets'))
