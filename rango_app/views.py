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
        visits += 1
        request.session['last_visit'] = str(datetime.now())
    else:
        request.session['last_visit'] = last_visit_cookie

    request.session['visits'] = visits

# views
class IndexView(View):
    def view(self, request):
        top_viewed_categories = Category.objects.order_by('-views')[:5]
        top_viewed_pages = Page.objects.order_by('-views')[:5]
        visitor_cookie_handler(request)
        context = {
            'top_viewed_categories': top_viewed_categories,
            'top_viewed_pages': top_viewed_pages,
            'visits': request.session['visits'],
            'last_visit': request.session['last_visit'],
        }

        return render(request, 'rango/index.html', context)

    def get(self, request):
        return self.view(request)

    def post(self, request):
        return self.view(request)

class AboutView(View):
    def get(self, request):
        visitor_cookie_handler(request)
        context = {
            'visits': request.session['visits'],
            'description': """Rango is a site where you 'rango' links into so
             that other people may see. Basically, a link sharing site.
            """
        }

        return render(request, 'rango/about.html', context)

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
        context = {
            'userprofile': userprofile,
            'selecteduser': user,
            'fixed_name': self.fix_name(user.username),
            'form': form
        }
        
        return render(request, 'rango/profile.html', context)

    @method_decorator(login_required)
    def post(self, request, username):
        (user, userprofile, form) = self.get_user_details(username)
        form = UserProfileForm(request.POST, 
            request.FILES, instance=userprofile)
        context = {
            'userprofile': userprofile,
            'selecteduser': user,
            'fixed_name': self.fix_name(user.username),
            'form': form
        }

        if form.is_valid():
            form.save(commit=True)
        else:
            print(form.errors)

        return render(request, 'rango/profile.html', context)

class GetCategoriesView(View):
    def get(self, request):
        category_list = Category.objects.all()
        context = { 'categories': category_list }
        return render(request, 'rango/categories.html', context)

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
        context = {}

        self.insert_category_context(request, context, category_name_slug)
        self.increment_category_views(category_name_slug)

        return render(request, "rango/category.html", context)

    def post(self, request, category_name_slug):
        context = {}
        result_list = []

        self.insert_category_context(request, context, category_name_slug)
        query = request.POST['query'].strip()

        if query:
            result_list = google_search(query)
            context['query'] = query
            context['result_list'] = result_list
        self.increment_category_views(category_name_slug)

        return render(request, "rango/category.html", context)

class AddPageView(View):
    def get(self, request, category_name_slug):
        try:
            category = Category.objects.get(slug=category_name_slug)
        except Category.DoesNotExist:
            category = None

        form = PageForm()

        context = { 'form': form, 'category': category }
        return render(request, 'rango/add_page.html', context)

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

        context = { 'form': form, 'category': category }
        return render(request, 'rango/add_page.html', context)

class AutoAddPageView(View):
    @method_decorator(login_required)
    def get(self, request):
        cat_id = None
        url = None
        title = None
        context = {}

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
            context['pages'] = pages

        return render(request, 'rango/page_list.html', context)

class SearchView(View):
    def post(self, request):
        search_term = request.POST['search_term']
        context = {
            'search_term': search_term,
            'results': google_search(search_term)
        }

        return render(request, "rango/search.html", context)

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
        context = { 'form': form }

        return render(request, 'rango/profile_registration.html', context)

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
        
        context = { 'form': form }

        return render(request, 'rango/profile_registration.html', context)

class ListProfiles(View):
    @method_decorator(login_required)
    def get(self, request):
        userprofile_list = UserProfile.objects.all()
        context = {'userprofile_list': userprofile_list}
        return render(request, 'rango/list_profiles.html', context)

class SearchProfiles(View):
    def get(self, request):
        print('searching profiles')
        context = {}
        starts_with = request.GET['search']
        print(starts_with)

        if len(starts_with) == 0:
            context['userprofile_list'] = UserProfile.objects.all()
        else:
            users = UserProfile.objects.all()
            filtered = []
            for user in users:
                if str(user).lower().startswith(starts_with.lower()):
                    filtered.append(user)

            context['userprofile_list'] = filtered

        return render(request, 'rango/profile_collection.html', context)

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
        starts_with = request.GET['suggestion']  

        cat_list = self.get_category_list(8, starts_with)
        if len(cat_list) == 0:
            cat_list = Category.objects.order_by('-likes')

        context = {
            'categories': cat_list
        }

        return render(request, 'rango/category_list.html', context)
