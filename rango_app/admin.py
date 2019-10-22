from django.contrib import admin
from rango_app.models import Category, Page

class CategoryAdmin(admin.ModelAdmin):
    prepopulated_fields = ['slug': ('name',)]

# Register your models here.
admin.site.register(Category)
admin.site.register(Page)


