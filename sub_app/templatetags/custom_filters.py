from django import template

register = template.Library()

@register.filter
def get_item(dictionary, key):
    """
    Template filter to get a value from a dictionary using a key.
    Usage: {{ dictionary|get_item:key }}
    """
    return dictionary.get(key, '')

@register.filter
def filter_by_type(measurements, clothing_type):
    """
    Template filter to filter measurements by clothing type.
    Usage: {{ measurements|filter_by_type:clothing_type }}
    """
    for measurement in measurements:
        if measurement.clothing_type == clothing_type:
            return measurement
    return None 