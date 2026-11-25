from django import template

register = template.Library()


@register.filter(name='num')
def num(value, decimals=0):
    """Formate un nombre à la française : 1250000.5 -> « 1 250 000,5 ».

    Les décimales nulles sont supprimées (9.0 -> « 9 »).
    """
    if value is None or value == '':
        return '—'
    try:
        value = float(value)
        decimals = int(decimals)
    except (TypeError, ValueError):
        return value
    text = f"{value:,.{decimals}f}"
    if decimals:
        text = text.rstrip('0').rstrip('.')
    # Espace insécable fine pour les milliers, virgule pour les décimales.
    return text.replace(',', ' ').replace('.', ',')


@register.filter(name='css_pct')
def css_pct(value):
    """Pourcentage pour un style CSS (jamais localisé), borné à [0, 100]."""
    try:
        value = max(0.0, min(float(value), 100.0))
    except (TypeError, ValueError):
        return '0'
    return f"{value:.2f}"
