from django import template
from django.utils.safestring import mark_safe
register = template.Library()

@register.filter
def highlight(text, search_word):
    highlighted_text = text.replace(
        search_word,
        '<span style="background-color: RGB(25, 135, 84, 0.7);">{}</span>'.format(search_word)
    )
    return mark_safe(highlighted_text)