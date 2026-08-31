from django import template

register = template.Library()

@register.filter(name='format_currency')
def format_currency(value):
    """
    Formate un nombre avec des espaces comme séparateurs de milliers
    Exemple: 1234567.89 -> 1 234 567.89
    """
    try:
        # Convertir en float si c'est une string
        if isinstance(value, str):
            value = float(value)
        
        # Séparer la partie entière et décimale
        if '.' in str(value):
            integer_part, decimal_part = str(value).split('.')
        else:
            integer_part = str(int(value))
            decimal_part = None
        
        # Ajouter les espaces pour les milliers
        integer_part = integer_part.replace(',', '')
        integer_part = '{:,}'.format(int(integer_part)).replace(',', ' ')
        
        # Reconstruire le nombre
        if decimal_part:
            return f"{integer_part}.{decimal_part}"
        else:
            return integer_part
    except (ValueError, TypeError, AttributeError):
        return value
