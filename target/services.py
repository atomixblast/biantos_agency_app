"""Calcul de l'avancement des objectifs et regroupement par période."""
import calendar
from dataclasses import dataclass, field
from datetime import date

from django.db.models import ExpressionWrapper, F, FloatField, Q, Sum, Value
from django.db.models.functions import NullIf

from order.models import ArticleOrder, Order


STATUS_UPCOMING = 'UPCOMING'
STATUS_ACHIEVED = 'ACHIEVED'
STATUS_ON_TRACK = 'ON_TRACK'
STATUS_LATE = 'LATE'
STATUS_MISSED = 'MISSED'

STATUS_LABELS = {
    STATUS_UPCOMING: 'À venir',
    STATUS_ACHIEVED: 'Atteint',
    STATUS_ON_TRACK: 'En bonne voie',
    STATUS_LATE: 'En retard',
    STATUS_MISSED: 'Non atteint',
}

MONTHS_FR = [
    '', 'Janvier', 'Février', 'Mars', 'Avril', 'Mai', 'Juin', 'Juillet',
    'Août', 'Septembre', 'Octobre', 'Novembre', 'Décembre',
]

TAB_CURRENT = 'current'
TAB_UPCOMING = 'upcoming'
TAB_PAST = 'past'
TABS = (TAB_CURRENT, TAB_UPCOMING, TAB_PAST)


# --------------------------------------------------------------------------- #
# Réalisé
# --------------------------------------------------------------------------- #

def compute_achieved(target):
    """Retourne (réalisé confirmé DONE, réalisé en cours PENDING).

    Les commandes annulées sont exclues. La date retenue est la date de la
    commande (``ordered_at``).
    """
    order_filter = Q(order__ordered_at__range=(target.start_date, target.end_date)) & ~Q(order__state='CANCELED')
    if target.sales_executive_id:
        order_filter &= Q(order__sales_executive_id=target.sales_executive_id)

    done = Q(order__state='DONE')
    pending = Q(order__state='PENDING')

    if target.is_quantity:
        result = ArticleOrder.objects.filter(order_filter, article_id=target.article_id).aggregate(
            done=Sum('qty', filter=done),
            pending=Sum('qty', filter=pending),
        )
    elif target.article_id:
        # CA d'un article : prix figé de la ligne, remise de ligne déduite, puis
        # remise sur la commande répartie au prorata du net des lignes.
        order_share = F('order__total') / NullIf(F('order__total') + F('order__global_discount_amount'), Value(0.0))
        line_total = ExpressionWrapper(
            F('qty') * F('unit_price') * (Value(1.0) - F('discount') / Value(100.0)) * order_share,
            output_field=FloatField(),
        )
        result = ArticleOrder.objects.filter(order_filter, article_id=target.article_id).aggregate(
            done=Sum(line_total, filter=done),
            pending=Sum(line_total, filter=pending),
        )
    else:
        # CA global : total des commandes (après remise).
        order_qs = Order.objects.filter(
            ordered_at__range=(target.start_date, target.end_date),
        ).exclude(state='CANCELED')
        if target.sales_executive_id:
            order_qs = order_qs.filter(sales_executive_id=target.sales_executive_id)
        result = order_qs.aggregate(
            done=Sum('total', filter=Q(state='DONE')),
            pending=Sum('total', filter=Q(state='PENDING')),
        )

    return float(result['done'] or 0), float(result['pending'] or 0)


# --------------------------------------------------------------------------- #
# Avancement
# --------------------------------------------------------------------------- #

@dataclass
class TargetProgress:
    target: object
    today: date
    achieved_done: float
    achieved_pending: float

    def __post_init__(self):
        t = self.target
        self.goal = float(t.target_value)
        self.achieved = self.achieved_done + self.achieved_pending
        self.remaining = max(self.goal - self.achieved, 0.0)
        self.pct = (self.achieved / self.goal * 100) if self.goal else 0.0
        self.pct_bar = min(self.pct, 100.0)

        # Temps
        self.days_total = (t.end_date - t.start_date).days + 1
        if self.today < t.start_date:
            self.days_elapsed = 0
        elif self.today > t.end_date:
            self.days_elapsed = self.days_total
        else:
            self.days_elapsed = (self.today - t.start_date).days + 1
        self.days_left = self.days_total - self.days_elapsed
        self.days_until_start = max((t.start_date - self.today).days, 0)
        self.time_pct = self.days_elapsed / self.days_total * 100

        # Rythme et projection
        self.expected_now = self.goal * self.time_pct / 100
        self.gap = self.achieved - self.expected_now        # > 0 : en avance
        self.gap_abs = abs(self.gap)
        self.surplus = max(self.achieved - self.goal, 0.0)
        self.daily_needed = (self.remaining / self.days_left) if self.days_left > 0 else None
        if self.days_elapsed > 0:
            self.projection = self.achieved / self.days_elapsed * self.days_total
            self.projection_pct = (self.projection / self.goal * 100) if self.goal else 0.0
        else:
            self.projection = None
            self.projection_pct = None

        self.status = self._status()
        self.status_label = STATUS_LABELS[self.status]

    def _status(self):
        t = self.target
        if self.today < t.start_date:
            return STATUS_UPCOMING
        if self.achieved >= self.goal:
            return STATUS_ACHIEVED
        if self.today > t.end_date:
            return STATUS_MISSED
        return STATUS_ON_TRACK if self.pct >= self.time_pct else STATUS_LATE

    @property
    def tab(self):
        t = self.target
        if self.today < t.start_date:
            return TAB_UPCOMING
        if self.today > t.end_date:
            return TAB_PAST
        return TAB_CURRENT


def build_progress(target, today=None):
    today = today or date.today()
    done, pending = compute_achieved(target)
    return TargetProgress(target=target, today=today, achieved_done=done, achieved_pending=pending)


# --------------------------------------------------------------------------- #
# Périodes
# --------------------------------------------------------------------------- #

def period_label(start, end):
    """Libellé lisible d'une période : mois, trimestre, année ou dates."""
    last_day = calendar.monthrange(end.year, end.month)[1]
    full_months = start.day == 1 and end.day == last_day
    if full_months and start.year == end.year:
        if start.month == end.month:
            return f"{MONTHS_FR[start.month]} {start.year}"
        if start.month == 1 and end.month == 12:
            return str(start.year)
        if start.month % 3 == 1 and end.month == start.month + 2:
            return f"T{(start.month - 1) // 3 + 1} {start.year}"
        return f"{MONTHS_FR[start.month]} → {MONTHS_FR[end.month]} {start.year}"
    return f"{start:%d/%m/%Y} → {end:%d/%m/%Y}"


@dataclass
class PeriodGroup:
    start_date: date
    end_date: date
    items: list = field(default_factory=list)

    @property
    def label(self):
        return period_label(self.start_date, self.end_date)

    @property
    def reference(self):
        return self.items[0]

    @property
    def achieved_count(self):
        return sum(1 for p in self.items if p.status == STATUS_ACHIEVED)

    @property
    def late_count(self):
        return sum(1 for p in self.items if p.status in (STATUS_LATE, STATUS_MISSED))


def group_by_period(progress_list, tab=TAB_CURRENT):
    groups = {}
    for p in progress_list:
        key = (p.target.start_date, p.target.end_date)
        groups.setdefault(key, PeriodGroup(start_date=key[0], end_date=key[1])).items.append(p)

    result = list(groups.values())
    if tab == TAB_PAST:
        result.sort(key=lambda g: (g.end_date, g.start_date), reverse=True)
    elif tab == TAB_UPCOMING:
        result.sort(key=lambda g: (g.start_date, g.end_date))
    else:
        # Échéance la plus proche d'abord.
        result.sort(key=lambda g: (g.end_date, g.start_date))

    # Dans chaque période : objectifs en retard d'abord, puis par avancement.
    order = {STATUS_LATE: 0, STATUS_MISSED: 0, STATUS_ON_TRACK: 1, STATUS_UPCOMING: 1, STATUS_ACHIEVED: 2}
    for g in result:
        g.items.sort(key=lambda p: (order[p.status], p.pct))
    return result


def compute_kpis(current_progress):
    """Indicateurs sur les objectifs dont la période est en cours."""
    count = len(current_progress)
    return {
        'current': count,
        'achieved': sum(1 for p in current_progress if p.status == STATUS_ACHIEVED),
        'on_track': sum(1 for p in current_progress if p.status == STATUS_ON_TRACK),
        'late': sum(1 for p in current_progress if p.status == STATUS_LATE),
        'avg_pct': (sum(p.pct_bar for p in current_progress) / count) if count else None,
    }
