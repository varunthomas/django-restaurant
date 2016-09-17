from django import forms
from django_countries.widgets import CountrySelectWidget
from .models import Register,Restaurant,FoodItems, Category
from django.utils.translation import ugettext_lazy as _

class CategoryModelChoiceField(forms.ModelChoiceField):
    def label_from_instance(self, obj):
        return obj.category

class TimeModelChoiceField(forms.ModelChoiceField):
    def label_from_instance(self, obj):
        return obj.time

class PreparationModelChoiceField(forms.ModelChoiceField):
    def label_from_instance(self, obj):
        return obj.preparation

class ContentModelChoiceField(forms.ModelChoiceField):
    def label_from_instance(self, obj):
        return obj.content

class RegForm(forms.ModelForm):
    typeofuser = forms.TypedChoiceField(
                   coerce=int,
                   choices=((0, 'Customer'), (1, 'Owner')),
                   widget=forms.RadioSelect
    )



    class Meta:
        model = Register

        fields = ('username', 'email', 'password', 'firstname', 'lastname', 'mobilenumber','typeofuser', )
        widgets = {
            'password': forms.PasswordInput(),
        }
        labels = {
            'firstname': _('First Name'),
            'lastname': _('Last Name'),
            'mobilenumber': _('Contact Number'),
        }
class LogForm(forms.Form):
    uname= forms.CharField(max_length=30, label='Username')
    passw= forms.CharField(widget=forms.PasswordInput(), max_length=30, label='Password')

class RestaurantForm(forms.ModelForm):
    class Meta:
        model = Restaurant
        fields = ('name', 'owner', 'city', 'state', 'country',)
        widgets={'country': CountrySelectWidget()}
        labels = {
            'name': _('Name of restaurant'),
            'owner': _('Owner name'),
        }

class FoodForm(forms.ModelForm):
    image = forms.FileField(
        label='Select a file',
        help_text='max. 42 megabytes'
    )

    category = CategoryModelChoiceField(queryset=Category.objects.all())
    time = TimeModelChoiceField(queryset=Category.objects.all().exclude(time__isnull=True))
    preparation = PreparationModelChoiceField(queryset=Category.objects.all().exclude(preparation__isnull=True))
    content = ContentModelChoiceField(queryset=Category.objects.all().exclude(content__isnull=True))
    class Meta:
        model = FoodItems
        fields = ('name','time', 'category', 'content', 'preparation', 'comment', 'price','image',)
