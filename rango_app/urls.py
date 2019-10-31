from django.conf import settings
from django.conf.urls import url
from django.conf.urls.static import static
from rango_app.views import (
    IndexView,
    AboutView, 
    AddCategoryView, 
    GetCategoriesView,
    ShowCategoryView,
    AddPageView,
    AutoAddPageView,
    SearchView,
    Goto_Url,
    RegisterProfile,
    ProfileView, 
    ListProfiles,
    SearchProfiles,
    LikeCategory,
    SuggestCategoryView,
) 
from . import views

app_name='rango'

urlpatterns = [
    url('home/', IndexView.as_view(), name="index"),
    url('about/', AboutView.as_view(), name="about"),
    url('add_category/', AddCategoryView.as_view(), name="add_category"),
    url('categories/', GetCategoriesView.as_view(), name="categories"),
    url(r'category/(?P<category_name_slug>[\w\-]+)/$', 
        ShowCategoryView.as_view(), name='show_category'),
    url(r'add_page/(?P<category_name_slug>[\w\-]+)/$', 
        AddPageView.as_view(), name="add_page"),
    url('add/', AutoAddPageView.as_view(), name="auto_add_page"),
    url('search/', SearchView.as_view(), name="search"),
    url('goto/', Goto_Url.as_view(), name='goto'),
    url('register_profile/', RegisterProfile.as_view(), name="register_profile"),
    url(r'profile/(?P<username>[\w\-]+)/$', ProfileView.as_view(), name="profile"),
    url('profiles/', ListProfiles.as_view(), name="list_profiles"),
    url('search_profile/$', SearchProfiles.as_view(), name="search_profile"),
    url('like/$', LikeCategory.as_view(), name="like_category"),
    url('suggest/$', SuggestCategoryView.as_view(), name="suggest_category"),
]