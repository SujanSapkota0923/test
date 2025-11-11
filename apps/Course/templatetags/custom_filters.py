from django import template

register = template.Library()

@register.filter
def get_display_value(obj, field_name):
    """Get the display value for a field, handling relationships"""
    if not obj:
        return None
    
    try:
        field_value = getattr(obj, field_name)
        
        # Handle None values
        if field_value is None:
            return None
        
        # Handle ManyToMany fields
        if hasattr(field_value, 'all'):
            return ', '.join([str(item) for item in field_value.all()])
        
        # Handle choice fields (like role)
        display_method = f'get_{field_name}_display'
        if hasattr(obj, display_method):
            return getattr(obj, display_method)()
        
        # Return the string representation
        return str(field_value)
    except AttributeError:
        return None

@register.filter
def attr(obj, field_name):
    """Get attribute value from object"""
    try:
        return getattr(obj, field_name)
    except (AttributeError, TypeError):
        return None

@register.filter
def get_item(dictionary, key):
    """Get an item from a dictionary by key."""
    if dictionary is None:
        return None
    return dictionary.get(key)
