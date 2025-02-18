from django import template
from core.utils import papelaria_aberta

register = template.Library()

@register.simple_tag
def is_papelaria_aberta():
    return papelaria_aberta()