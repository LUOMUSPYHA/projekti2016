from django import template

register = template.Library()

    
@register.filter(name='replaceCommaWithSpace')
def replaceCommaWithSpace(text):
    return text.replace(',', ' ')
