from django.conf import settings
from django.conf.urls import url
from django.conf.urls.static import static
from . import views

urlpatterns = [
    url('home/', views.index, name="Index"),
    url(r'category/(?P<category_name_slug>[\w\-]+)/$', 
        views.show_category, name='show_category'),
    url('add_category/', views.add_category, name="add_category"),
    url(r'add_page/(?P<category_name_slug>[\w\-]+)/$', 
        views.add_page, name="add_page")
]