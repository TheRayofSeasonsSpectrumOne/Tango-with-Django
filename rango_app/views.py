from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.contrib.auth.models import User
from django.views import View
from django.urls import reverse
from rango_app.models import Category, Page, UserProfile
from rango_app.forms import CategoryForm, PageForm, UserProfileForm
from rango_app.google_search import google_search
from datetime import datetime
import json

# cookie managers
def get_server_side_cookie(request, cookie, default_val=None):
    val = request.session.get(cookie)
    if not val:
        val = default_val
    return val

def visitor_cookie_handler(request):
    visits = int(get_server_side_cookie(request, 'visits', '1'))

    last_visit_cookie = get_server_side_cookie(
        request, 
        'last_visit', 
        str(datetime.now())
    )
    last_visit_time = datetime.strptime(
        last_visit_cookie[:-7], '%Y-%m-%d %H:%M:%S'
    )

    if(datetime.now() - last_visit_time).days > 0:
        print("Visits Incremented")
        visits += 1
        request.session['last_visit'] = str(datetime.now())
    else:
        print("Last Visit Cookie")
        request.session['last_visit'] = last_visit_cookie

    request.session['visits'] = visits

# views
class IndexView(View):
    def view(self, request):
        category_list = Category.objects.order_by('-views')[:5]
        page_list = Page.objects.order_by('-views')[:5]
        visitor_cookie_handler(request)
        context_dict = {
            'boldmessage': 'crunchy',
            'top_categories': category_list,
            'top_pages': page_list,
            'visits': request.session['visits'],
            'last_visit': request.session['last_visit'],
        }
        return render(request, 'rango/index.html', context=context_dict)

    def get(self, request):
        return self.view(request)

    def post(self, request):
        return self.view(request)

class AboutView(View):
    def get(self, request):
        visitor_cookie_handler(request)
        return render(request, 'rango/about.html', 
            context={'visits': request.session['visits']})

class AddCategoryView(View):

    @method_decorator(login_required)
    def get(self,request):
        form = CategoryForm()
        return render(request, 'rango/add_category.html', {'form': form})
    
    @method_decorator(login_required)
    def post(self, request):
        form = CategoryForm()
        form = CategoryForm(request.POST)
        if form.is_valid():
            form.save(commit=True)
            return IndexView.as_view()(self.request)
        else:
            print(form.errors)

        return render(request, 'rango/add_category.html', {'form': form})

class ProfileView(View):
    def get_user_details(self, username):
        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            return IndexView.as_view()(self.request)

        userprofile = UserProfile.objects.get_or_create(user=user)[0]
        form = UserProfileForm({'website': userprofile.website, 
            'picture': userprofile.picture})
        return(user, userprofile, form)

    # adds ' to strings ending in "s" and 's to those not ending in "s"
    def fix_name(self, name):
        if name[-1:] == 's':
            name = name + "\'"
        else:
            name += "\'s"

        return name

    @method_decorator(login_required)
    def get(self, request, username):
        (user, userprofile, form) = self.get_user_details(username)

        context_dict = {
            'userprofile': userprofile,
            'selecteduser': user,
            'fixed_name': self.fix_name(user.username),
            'form': form
        }
        
        return render(request, 'rango/profile.html', context_dict)

    @method_decorator(login_required)
    def post(self, request, username):
        (user, userprofile, form) = self.get_user_details(username)
        form = UserProfileForm(request.POST, 
            request.FILES, instance=userprofile)

        context_dict = {
            'userprofile': userprofile,
            'selecteduser': user,
            'fixed_name': self.fix_name(user.username),
            'form': form
        }

        if form.is_valid():
            form.save(commit=True)
        else:
            print(form.errors)

        return render(request, 'rango/profile.html', context_dict)

class GetCategoriesView(View):
    def get(self, request):
        category_list = Category.objects.all()
        context_dict = { 'categories': category_list }
        return render(request, 'rango/categories.html', context_dict)

class ShowCategoryView(View):

    def insert_category_context(self, request, context, slug):
        try:
            category = Category.objects.get(slug=slug)
            pages = Page.objects.filter(category=category).order_by('-views')
            context["pages"]=pages
            context["category"]=category
        except Category.DoesNotExist:
            context["category"]= None
            context["pages"]= None

        context['query'] = category.name

    def increment_category_views(self, slug):
        try:
            category = Category.objects.get(slug=slug)
            category.views += 1
            category.save()
        except:
            category = None

    def get(self, request, category_name_slug):
        context_dict = {}

        self.insert_category_context(request, context_dict, category_name_slug)
        self.increment_category_views(category_name_slug)

        return render(request, "rango/category.html", context_dict)

    def post(self, request, category_name_slug):
        context_dict = {}
        result_list = []

        self.insert_category_context(request, context_dict, category_name_slug)
        query = request.POST['query'].strip()

        if query:
            result_list = google_search(query)
            context_dict['query'] = query
            context_dict['result_list'] = result_list
        self.increment_category_views(category_name_slug)

        return render(request, "rango/category.html", context_dict)

class AddPageView(View):
    def get(self, request, category_name_slug):
        try:
            category = Category.objects.get(slug=category_name_slug)
        except Category.DoesNotExist:
            category = None

        form = PageForm()

        context_dict = { 'form': form, 'category': category }
        return render(request, 'rango/add_page.html', context_dict)

    def post(self, request, category_name_slug):
        try:
            category = Category.objects.get(slug=category_name_slug)
        except Category.DoesNotExist:
            category = None

        form = PageForm()
        if request.method == "POST":
            form = PageForm(request.POST)
            print(form.is_valid())
            if form.is_valid():
                if category:
                    page = form.save(commit=False)
                    page.category = category
                    page.views = 0
                    page.save()
                    return ShowCategoryView(request, category_name_slug)
                else:
                    print(form.errors)

        context_dict = { 'form': form, 'category': category }
        return render(request, 'rango/add_page.html', context_dict)

class AutoAddPageView(View):
    @method_decorator(login_required)
    def get(self, request):
        cat_id = None
        url = None
        title = None
        context_dict = {}

        cat_id = request.GET['category_id']
        url = request.GET['url']
        title = request.GET['title']

        if cat_id:
            category = Category.objects.get(id=int(cat_id))
            p = Page.objects.get_or_create(
                category=category,
                url=url,
                title=title
            )

            pages = Page.objects.filter(category=category).order_by('-views')
            context_dict['pages'] = pages

        return render(request, 'rango/page_list.html', context_dict)

class SearchView(View):
    def post(self, request):
        search_term = request.POST['search_term']
        context_dict = {
            'search_term': search_term,
            'results': google_search(search_term)
        }

        return render(request, "rango/search.html", context_dict)

# if error occurs in goto, reinitialize url for post
class Goto_Url(View):
    def get(self, request):
        page_id = None

        if 'page_id' in request.GET:
            page_id = request.GET['page_id']

            try:
                page = Page.objects.get(id=page_id)
                page.views += 1
                page.save()
                return redirect(page.url)
            except:
                pass

        return IndexView.as_view()(self.request)

    def post(self, request):
        return IndexView.as_view()(self.request)

class RegisterProfile(View):

    @method_decorator(login_required)
    def get(self, request):
        form = UserProfileForm()
        context_dict = { 'form': form }

        return render(request, 'rango/profile_registration.html', context_dict)

    @method_decorator(login_required)
    def post(self, request):
        form = UserProfileForm()

        form = UserProfileForm(request.POST, request.FILES)
        if form.is_valid():
            user_profile = form.save(commit=False)
            user_profile.user = request.user
            user_profile.save()

            return IndexView.as_view()(self.request)
        else:
            print(form.errors)
        
        context_dict = { 'form': form }

        return render(request, 'rango/profile_registration.html', context_dict)

class ListProfiles(View):
    @method_decorator(login_required)
    def get(self, request):
        userprofile_list = UserProfile.objects.all()
        return render(request, 'rango/list_profiles.html', 
            {'userprofile_list': userprofile_list})

class LikeCategory(View):
    @method_decorator(login_required)
    def get(self, request):
        cat_id = None
        cat_id = request.GET['category_id']
        likes = 0

        if cat_id:
            cat = Category.objects.get(id=int(cat_id))
            if cat:
                likes = cat.likes + 1
                cat.likes = likes
                cat.save()
        
        return HttpResponse(likes)

class SuggestCategoryView(View):
    def get_category_list(self, max_results=0, starts_with=''):
        cat_list = []
        if starts_with:
            cat_list = Category.objects.filter(name__istartswith=starts_with)

        if max_results > 0:
            if len(cat_list) > max_results:
                cat_list = cat_list[:max_results]

        return cat_list

    def get(self, request):
        cat_list = []
        starts_with = ''

        if request.method == 'GET':
            starts_with = request.GET['suggestion']  

        cat_list = self.get_category_list(8, starts_with)
        if len(cat_list) == 0:
            cat_list = Category.objects.order_by('-likes')

        context_dict = {
            'categories': cat_list
        }

        return render(request, 'rango/category_list.html', context_dict)
