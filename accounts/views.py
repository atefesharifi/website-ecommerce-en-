from django.shortcuts import render,redirect
from .forms import *
from .models import *
from order.models import *
from home.models import *
from cart.models import *
from django.db.models import Sum
from django.contrib.auth.models import User
from django.contrib.auth import authenticate,login,logout
from django.contrib import messages
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.decorators import login_required
from random import randint
import ghasedak
from django.http import HttpResponse 

def user_register(request):
    category = Category.objects.filter(sub_cat=False)
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            data = form.cleaned_data
            user = User.objects.create_user(username=data['user_name'],email=data['email'],first_name=data['first_name'],last_name=data['last_name'],password=data['password_1'])
            user.save()

            return redirect('home:home')

            messages.success(request,'حساب کاربری با موفقیت ساخته شد','success')
            
    else:
        form = UserRegisterForm()
    context = {'form':form,'category':category}
    return render(request, 'accounts/register.html', context)

def user_login(request):
    url = request.META.get('HTTP_REFERER')
    category = Category.objects.filter(sub_cat=False)
    if request.method == 'POST':
        form = UserLoginForm(request.POST)
        if form.is_valid():
            data = form.cleaned_data
            remember = data['remember']
            try:
                user = authenticate(request, username=User.objects.get(email=data['user']), password=data['password'])
            except:
                user = authenticate(request, username=data['user'], password=data['password'])

            if user is not None:
                login(request,user)
                if not remember:
                    request.session.set_expiry(0)
                else:
                    request.session.set_expiry(10000)
                # messages.success(request,'welcome my site','primary')
                return redirect('home:home')  
            else:
                print ( "invalid login details ")
                return redirect(url)
    else:
        form = UserLoginForm()
    context ={'form':form,'category':category}
    return render(request, 'accounts/login.html', context)
    

def user_logout(request):
    # url = request.META.get('HTTP_REFERER')
    logout(request)
    return redirect('home:home')


@login_required(login_url='accounts:login')
def user_profile(request):
    profile = Profile.objects.get(user_id=request.user.id)
    category = Category.objects.filter(sub_cat=False)
    nums = Cart.objects.filter(user_id=request.user.id).aggregate(sum=Sum('quantity'))['sum']
    context = {'category':category,'profile':profile,'nums':nums}
    return render(request,'accounts/profile.html',context)

@login_required(login_url='accounts:login')
def user_update(request):
    profile = Profile.objects.get(user_id=request.user.id)
    category = Category.objects.filter(sub_cat=False)
    nums = Cart.objects.filter(user_id=request.user.id).aggregate(sum=Sum('quantity'))['sum']
    if request.method == 'POST':
        user_form = UserUpdateForm(request.POST,instance=request.user)
        profile_form = ProfileUpdateForm(request.POST,request.FILES,instance=request.user.profile)
        if user_form and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            messages.success(request,'update successfully','success')
            return redirect('accounts:profile')
    else:
        user_form = UserUpdateForm(instance=request.user)
        profile_form = ProfileUpdateForm(instance=request.user.profile)

    context = {'user_form':user_form,'profile_form':profile_form,'category':category,'profile':profile,'nums':nums}
    return render(request,'accounts/update.html',context)


def change_password(request):
    profile = Profile.objects.get(user_id=request.user.id)
    category = Category.objects.filter(sub_cat=False)
    nums = Cart.objects.filter(user_id=request.user.id).aggregate(sum=Sum('quantity'))['sum']
    if request.method == 'POST':
        form = PasswordChangeForm(request.user,request.POST)
        if form.is_valid():
            form.save()
            update_session_auth_hash(request,form.user)
            messages.success(request,'passwor successfully changed','success')
            return redirect('accounts:profile')
        else:
            messages.error(request,'password not correct','danger')
            return redirect('accounts:change')
    else:
        form = PasswordChangeForm(request.user)

    return render(request,'accounts/change.html',{'form':form,'category':category,'profile':profile,'nums':nums})

def phone(request):
    if request.method == 'POST':
        form = PhoneForm(request.POST)
        if form.is_valid():
            global random_code,phone
            data = form.cleaned_data
            phone = f"0{data['phone']}"
            random_code = randint(100,1000)
            sms = ghasedak.Ghasedak("3f269a0a1b77f8f09813f2476e8105367d612c824154b3acc221030ae5ef05f9")
            sms.send({'message':random_code,'receptor':phone,'linenumber':"10008566"})
            return redirect('accounts:verify')
    else:
        form = PhoneForm()
    return render(request,'phone.html',{'form':form})

def verify(request):
    if request.method == 'POST':
        form = CodeForm(request.POST)
        if form.is_valid():
            if random_code == form.cleaned_data['code']:
                profile = Profile.objects.get(phone=phone)
                user = User.objects.get(profile__id=profile.id)
                login(request,user)
                messages.success(request,'hi user')
                return redirect('home:home')
            else:
                messages.error(request,'error code')
    else:
        form = CodeForm()
    return render(request,'accounts/code.html',{'form':form})

def favourite(request):
    profile = Profile.objects.get(user_id=request.user.id)
    category = Category.objects.filter(sub_cat=False)
    nums = Cart.objects.filter(user_id=request.user.id).aggregate(sum=Sum('quantity'))['sum']
    product = request.user.fa_user.all()
    return render(request,'accounts/favourite.html',{'product':product,'category':category,'profile':profile,'nums':nums})

def history(request):
    profile = Profile.objects.get(user_id=request.user.id)
    category = Category.objects.filter(sub_cat=False)
    nums = Cart.objects.filter(user_id=request.user.id).aggregate(sum=Sum('quantity'))['sum']
    data = ItemOrder.objects.filter(user_id = request.user.id)
    return render(request,'accounts/history.html',{'data':data,'category':category,'profile':profile,'nums':nums})
