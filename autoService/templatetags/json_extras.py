from django import template
import json
from django.utils.safestring import mark_safe

register = template.Library()

@register.filter
def to_json(value):
    return mark_safe(json.dumps(value))