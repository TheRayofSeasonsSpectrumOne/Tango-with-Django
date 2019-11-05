from django import forms
from django.core import validators
from rango_app.models import Category, Page, UserProfile, Theme

class CategoryForm(forms.ModelForm):
    name = forms.CharField(max_length=128, 
                           help_text="Please enter the category name")
    views = forms.IntegerField(widget=forms.HiddenInput(), initial=0)
    likes = forms.IntegerField(widget=forms.HiddenInput(), initial=0)
    slug = forms.CharField(widget=forms.HiddenInput(), required=False)

    class Meta:
        model = Category
        fields = ('name',)

class CustomURLField(forms.fields.URLField):
    default_validators = [validators.URLValidator(schemes=['https'])]

class PageForm(forms.ModelForm):
    title = forms.CharField(max_length=128,
                            help_text="Please enter the title of the page")
    url = CustomURLField(max_length=128,
                          help_text="Please enter the URL of the page")
    views = forms.IntegerField(widget=forms.HiddenInput(), initial=0)

    class Meta:
        model = Page
        fields = ('title', 'url', 'views')

    def clean(self):
        cleaned_data = self.cleaned_data
        url = cleaned_data.get('url')

        if url and not url.startswith('http://'):
            url = 'http://' + url
            cleaned_data['url'] = url

            return cleaned_data

class UserProfileForm(forms.ModelForm):
    website = forms.URLField(required=False)
    picture = forms.ImageField(required=False)
    
    class Meta:
        model = UserProfile
        exclude = ('user',)

    def clean(self):
        print('wow')

class ThemeForm(forms.ModelForm):
    background_image = forms.ImageField(required=False, 
        help_text="Background Image")
    dark_mode = forms.BooleanField(required=False, initial=False, 
        help_text="Dark Mode")

    class Meta:
        model = Theme
        fields = ('background_image', 'dark_mode',)
        exclude = ('user',)
