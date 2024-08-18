from django import template
from django.utils.html import format_html

register = template.Library()

@register.filter(name='add_class')
def add_class(value, css_class):
    if isinstance(value, str):
        return format_html('<input type="text" class="{}" value="{}" />', css_class, value)
    if hasattr(value, 'field') and hasattr(value.field.widget, 'attrs'):
        attrs = value.field.widget.attrs.copy()
        attrs.update({'class': css_class})
        return value.field.widget.__class__(attrs=attrs)
    return value

@register.filter(name='add_class_and_placeholder')
def add_class_and_placeholder(field, args):
    css_class, placeholder = args.split('|', 1)
    widget = field.field.widget
    attrs = widget.attrs.copy()
    attrs.update({
        'class': css_class,
        'placeholder': placeholder
    })
    widget = widget.__class__(attrs=attrs)
    return format_html('<input type="{}" name="{}" id="{}" class="{}" placeholder="{}" value="{}">',
                       widget.input_type,
                       field.name,
                       field.id_for_label,
                       css_class,
                       placeholder,
                       field.value() or '')
