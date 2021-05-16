from django import forms
from .models import *
from django.contrib.auth.models import User

error ={
    'min_length':'حداقل باید 5 کاراکتر باشد',
    'required':'این فیلد اجباری است',
    'invalid':'ایمیل شما نامعتبر است',
}

class UserRegisterForm(forms.Form):
    user_name = forms.CharField(max_length=50,error_messages=error,widget=forms.TextInput(attrs={'placeholder':'نام کاربری', 'class':'form-control'}))
    email = forms.EmailField(error_messages=error,widget=forms.EmailInput(attrs={'placeholder':'ایمیل','class':'form-control'}))
    first_name = forms.CharField(max_length=50,min_length=5,error_messages=error,widget=forms.TextInput(attrs={'placeholder':'نام','class':'form-control'}))
    last_name = forms.CharField(max_length=50,widget=forms.TextInput(attrs={'placeholder':'فامیل','class':'form-control'}))
    password_1 = forms.CharField(max_length=50,widget=forms.PasswordInput(attrs={'placeholder':'پسورد خود را وارد کنید','class':'form-control'}))
    password_2 = forms.CharField(max_length=50,widget=forms.PasswordInput(attrs={'placeholder':'تکرار پسورد','class':'form-control'}))

    def clean_user_name(self):
        user = self.cleaned_data['user_name']
        if User.objects.filter(username=user).exists():
            raise forms.ValidationError('user exist')
        return user

    def clean_email(self):
        email = self.cleaned_data['email']
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError('email exist')
        return email

    def clean_password_2(self):
        password1 = self.cleaned_data['password_1']
        password2 = self.cleaned_data['password_2']
        if password1 != password2:
            raise forms.ValidationError('password not match')
        elif len(password2) < 5:
            raise forms.ValidationError('password to short')
        elif not any(x.isupper() for x in password2):
            raise forms.ValidationError('پسورد حداقل باید یک حرف بزرگ داشته باشد.')
        return password1

class UserLoginForm(forms.Form):
    user = forms.CharField(widget=forms.TextInput(attrs={'placeholder':'input username'}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={'placeholder':'input password'}))
    remember = forms.BooleanField(required=False,widget=forms.CheckboxInput())

class UserUpdateForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['email','first_name','last_name']

class ProfileUpdateForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['phone','address','profile_image']

class PhoneForm(forms.Form):
    phone = forms.IntegerField()

class CodeForm(forms.Form):
    code = forms.IntegerField()