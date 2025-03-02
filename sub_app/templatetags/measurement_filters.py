from django import template

register = template.Library()

@register.filter
def get_item(dictionary, key):
    """Get an item from a dictionary using bracket notation."""
    return dictionary.get(key, '')

@register.filter
def filter_by_type(measurements, clothing_type):
    """Filter measurements by clothing type."""
    return measurements.filter(clothing_type=clothing_type).first() 