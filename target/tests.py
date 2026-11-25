from datetime import date
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from order.models import Article, ArticleOrder, Order, SalesExecutive
from target import services
from target.forms import TargetForm
from target.models import Target


User = get_user_model()

TODAY = date(2026, 12, 11)  # 11e jour sur 31 en décembre


def make_order(articles, state='DONE', ordered_at=date(2026, 12, 5), sales_executive=None, total=None):
    """articles : liste de (article, qty, discount%)."""
    order = Order.objects.create(
        name='Cmd', state=state, ordered_at=ordered_at, json_repr=[],
        sales_executive=sales_executive,
        total=total if total is not None else sum(a.sale_price * q * (1 - d / 100) for a, q, d in articles),
    )
    for article, qty, discount in articles:
        ArticleOrder.objects.create(order=order, article=article, qty=qty, discount=discount)
    return order


class TargetTestBase(TestCase):
    def setUp(self):
        self.mug = Article.objects.create(name='Tasse', ref='TASSE', sale_price=1000.0)
        self.tshirt = Article.objects.create(name='T-shirt', ref='TS', sale_price=5000.0)
        self.alice = SalesExecutive.objects.create(name='Alice', tel='1')
        self.bob = SalesExecutive.objects.create(name='Bob', tel='2')

    def target(self, **kwargs):
        data = dict(name='Obj', metric=Target.METRIC_QUANTITY, target_value=Decimal('100'),
                    article=self.mug, start_date=date(2026, 12, 1), end_date=date(2026, 12, 31))
        data.update(kwargs)
        return Target.objects.create(**data)


class AchievedTests(TargetTestBase):

    def test_quantity_excludes_canceled_and_splits_states(self):
        make_order([(self.mug, 10, 0)], state='DONE')
        make_order([(self.mug, 5, 0)], state='PENDING')
        make_order([(self.mug, 50, 0)], state='CANCELED')
        make_order([(self.tshirt, 7, 0)], state='DONE')                        # autre article
        make_order([(self.mug, 30, 0)], state='DONE', ordered_at=date(2026, 11, 30))  # hors période

        p = services.build_progress(self.target(), TODAY)
        self.assertEqual((p.achieved_done, p.achieved_pending, p.achieved), (10, 5, 15))
        self.assertEqual(p.remaining, 85)

    def test_sales_executive_filter(self):
        make_order([(self.mug, 10, 0)], sales_executive=self.alice)
        make_order([(self.mug, 4, 0)], sales_executive=self.bob)
        make_order([(self.mug, 3, 0)])

        self.assertEqual(services.build_progress(self.target(sales_executive=self.alice), TODAY).achieved, 10)
        self.assertEqual(services.build_progress(self.target(), TODAY).achieved, 17)

    def test_revenue_global_uses_order_totals(self):
        make_order([(self.mug, 2, 0)], total=2000.0)
        make_order([(self.tshirt, 1, 0)], state='PENDING', total=5000.0)
        make_order([(self.tshirt, 10, 0)], state='CANCELED', total=50000.0)

        p = services.build_progress(self.target(metric=Target.METRIC_REVENUE, article=None,
                                                target_value=Decimal('10000')), TODAY)
        self.assertEqual((p.achieved_done, p.achieved_pending), (2000, 5000))

    def test_revenue_per_article_applies_line_discount(self):
        make_order([(self.mug, 10, 10), (self.tshirt, 1, 0)])  # tasses : 10 × 1000 − 10 %

        p = services.build_progress(self.target(metric=Target.METRIC_REVENUE,
                                                target_value=Decimal('20000')), TODAY)
        self.assertAlmostEqual(p.achieved, 9000)

    def test_revenue_per_article_includes_order_discount(self):
        order = make_order([(self.mug, 10, 0)])  # 10 000 avant remise commande
        order.global_discount, order.global_discount_amount, order.total = 20, 2000.0, 8000.0
        order.save()
        p = services.build_progress(self.target(metric=Target.METRIC_REVENUE,
                                                target_value=Decimal('20000')), TODAY)
        self.assertAlmostEqual(p.achieved, 8000)

    def test_revenue_uses_frozen_price(self):
        make_order([(self.mug, 10, 0)])
        self.mug.sale_price = 9999.0
        self.mug.save()

        p = services.build_progress(self.target(metric=Target.METRIC_REVENUE,
                                                target_value=Decimal('20000')), TODAY)
        self.assertAlmostEqual(p.achieved, 10000)


class StatusTests(TargetTestBase):

    def test_upcoming(self):
        p = services.build_progress(self.target(start_date=date(2027, 1, 1), end_date=date(2027, 1, 31)), TODAY)
        self.assertEqual((p.status, p.tab, p.days_elapsed), (services.STATUS_UPCOMING, services.TAB_UPCOMING, 0))

    def test_on_track_and_late(self):
        # 11/31 jours écoulés ≈ 35,5 % → 40 % = en bonne voie, 20 % = en retard
        make_order([(self.mug, 40, 0)])
        self.assertEqual(services.build_progress(self.target(), TODAY).status, services.STATUS_ON_TRACK)
        self.assertEqual(services.build_progress(self.target(target_value=Decimal('200')), TODAY).status,
                         services.STATUS_LATE)

    def test_achieved_and_missed(self):
        make_order([(self.mug, 40, 0)])
        self.assertEqual(services.build_progress(self.target(target_value=Decimal('40')), TODAY).status,
                         services.STATUS_ACHIEVED)
        p = services.build_progress(self.target(), date(2027, 1, 5))
        self.assertEqual((p.status, p.tab), (services.STATUS_MISSED, services.TAB_PAST))

    def test_pace_and_projection(self):
        make_order([(self.mug, 22, 0)])
        p = services.build_progress(self.target(), TODAY)
        self.assertEqual((p.days_total, p.days_elapsed, p.days_left), (31, 11, 20))
        self.assertAlmostEqual(p.projection, 22 / 11 * 31)
        self.assertAlmostEqual(p.daily_needed, 78 / 20)


class PeriodTests(TargetTestBase):

    def test_labels(self):
        self.assertEqual(services.period_label(date(2026, 12, 1), date(2026, 12, 31)), 'Décembre 2026')
        self.assertEqual(services.period_label(date(2026, 10, 1), date(2026, 12, 31)), 'T4 2026')
        self.assertEqual(services.period_label(date(2026, 1, 1), date(2026, 12, 31)), '2026')
        self.assertEqual(services.period_label(date(2026, 12, 1), date(2026, 12, 15)), '01/12/2026 → 15/12/2026')

    def test_grouping(self):
        a = self.target(name='A')
        b = self.target(name='B', article=self.tshirt)
        c = self.target(name='C', start_date=date(2026, 12, 1), end_date=date(2026, 12, 15))
        groups = services.group_by_period([services.build_progress(t, TODAY) for t in (a, b, c)])
        self.assertEqual([g.label for g in groups], ['01/12/2026 → 15/12/2026', 'Décembre 2026'])
        self.assertEqual(len(groups[1].items), 2)


class FormTests(TargetTestBase):

    def data(self, **kwargs):
        d = dict(name='Obj', metric='QUANTITY', target_value='100', article=self.mug.id,
                 sales_executive='', start_date='2026-12-01', end_date='2026-12-31')
        d.update(kwargs)
        return d

    def test_valid(self):
        self.assertTrue(TargetForm(self.data()).is_valid())

    def test_end_before_start(self):
        form = TargetForm(self.data(start_date='2026-12-31', end_date='2026-12-01'))
        self.assertFalse(form.is_valid())
        self.assertIn('end_date', form.errors)

    def test_quantity_requires_article_but_revenue_does_not(self):
        self.assertIn('article', TargetForm(self.data(article='')).errors)
        self.assertTrue(TargetForm(self.data(article='', metric='REVENUE')).is_valid())

    def test_positive_value(self):
        self.assertIn('target_value', TargetForm(self.data(target_value='0')).errors)


class ViewTests(TargetTestBase):

    def setUp(self):
        super().setUp()
        self.obj = self.target()
        self.user = User.objects.create_user(username='u', email='u@example.com', password='pass12345!')

    def test_anonymous_redirected_to_login(self):
        urls = [
            reverse('target:list_targets'),
            reverse('target:create_target'),
            reverse('target:update_target', args=[self.obj.id]),
            reverse('target:delete_target', args=[self.obj.id]),
        ]
        for url in urls:
            response = self.client.get(url)
            self.assertEqual(response.status_code, 302, url)
            self.assertIn('/auth/login/', response['Location'])

    def test_list_renders_all_tabs(self):
        self.client.force_login(self.user)
        for tab in ('current', 'upcoming', 'past', 'bogus'):
            response = self.client.get(reverse('target:list_targets'), {'tab': tab})
            self.assertEqual(response.status_code, 200)

    def test_update_missing_returns_404(self):
        self.client.force_login(self.user)
        self.assertEqual(self.client.get(reverse('target:update_target', args=[999])).status_code, 404)

    def test_delete_requires_post(self):
        self.client.force_login(self.user)
        url = reverse('target:delete_target', args=[self.obj.id])
        self.assertEqual(self.client.get(url).status_code, 405)
        self.client.post(url)
        self.assertFalse(Target.objects.filter(id=self.obj.id).exists())
