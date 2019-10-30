from django import template
from rango_app.models import Category, Page

register = template.Library()

@register.inclusion_tag('rango/category_list.html')
def get_category_list(category=None):
    return { 
        "categories": Category.objects.all(),
        "act_cat": category 
    }

@register.inclusion_tag('rango/page_list.html')
def get_page_list(category=None):
    return {
        "pages": Page.objects.filter(category=category).order_by('-views')
    }