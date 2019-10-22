from django.conf.urls import url
from . import views

urlpatterns = [
    url('a/', views.index, name="Index"),
    url('apage/', views.getTemplate, name="template"),
    url('categories/', views.getCategories, name="categories")
]