from django import template
from django.contrib.auth.models import User
from rango_app.models import Category, Page, UserProfile

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

@register.inclusion_tag('rango/profile_collection.html')
def get_profile_list():
    return {
        "userprofile_list": UserProfile.objects.all()
    }