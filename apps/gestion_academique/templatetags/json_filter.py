# apps/gestion_academique/templatetags/json_filter.py
from django import template
import json

register = template.Library()

@register.filter
def json_length(value):
    try:
        if not value:
            return 0
        data = json.loads(value)
        return len(data) if isinstance(data, list) else 0
    except:
        return 0

@register.filter
def json_parse(value):
    try:
        if not value:
            return []
        return json.loads(value)
    except:
        return []