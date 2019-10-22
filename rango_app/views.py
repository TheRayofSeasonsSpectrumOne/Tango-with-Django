from django.shortcuts import render
from django.http import HttpResponse
from rango_app.models import Category

# Create your views here.
def index(request):
    return HttpResponse("You are now in Categories!")

def getTemplate(request):
    context_dict = {'boldmessage': 'crunchy'}
    return render(request, 'rango/index.html', context=context_dict)

def getCategories(request):
    category_list = Category.objects.order_by('-likes')[:5]
    context_dict = { 'categories': category_list }
    return render(request, 'rango/index.html', context_dict)

