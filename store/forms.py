from django.contrib.auth.forms import UserCreationForm
from .models import *
from django.contrib.auth.models import User
from django.forms import ModelForm


class UserRegisterForm(UserCreationForm):
    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']


class ProductForm(ModelForm):
    class Meta:
        model = Product
        fields = '__all__'
