from django import template

register = template.Library()


@register.filter(name='format_currency')
def format_currency(value):
    """
    Formate un montant avec des espaces comme séparateurs de milliers.
    Les décimales ne sont affichées que si elles sont utiles :
    704500.0 -> « 704 500 » ; 1234.5 -> « 1 234,50 ».
    """
    try:
        value = round(float(value), 2)
    except (ValueError, TypeError):
        return value
    if value == int(value):
        return f"{int(value):,}".replace(',', ' ')
    return f"{value:,.2f}".replace(',', ' ').replace('.', ',')
