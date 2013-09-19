from django import template
import json

register = template.Library()

@register.filter
def get_item(d, key):
    return d.get(key)

@register.filter
def to_json(tables):
    d = {}
    for key, value in tables.iteritems():
        d[key] = [str(c.name) for c in value]
    return json.dumps(d)
