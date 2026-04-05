from django import template
register = template.Library()

@register.simple_tag
def get_plan(planning_dict, heure, vehicule_id):
    return planning_dict.get((heure, vehicule_id))