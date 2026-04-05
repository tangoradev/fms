from django import template

register = template.Library()

@register.filter
def get_item(dictionary, key):
    """
    Filtre pour accéder aux éléments d'un dictionnaire par clé dans un template Django
    Exemple d'utilisation: {{ mydict|get_item:key }}
    """
    return dictionary.get(key, None)

@register.filter
def multiply(value, arg):
    """
    Multiplie la valeur par l'argument
    Exemple d'utilisation: {{ value|multiply:10 }}
    """
    try:
        return float(value) * float(arg)
    except (ValueError, TypeError):
        return None
