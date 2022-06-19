from django.shortcuts import render, redirect
from .models import *
from cart.models import *
from .forms import CouponForm
from django.views.decorators.http import require_POST
from django.utils import timezone
import jdatetime
from django.contrib import messages
from django.test import Client
from django.http import HttpResponse
from django.utils.crypto import get_random_string
from django.db.models import Sum

def order_detail(request,id):
    cart = Cart.objects.filter(user_id=request.user.id)
    order = Order.objects.get(id=id)
    category = Category.objects.filter(sub_cat=False)
    nums = Cart.objects.filter(user_id=request.user.id).aggregate(sum=Sum('quantity'))['sum']
    form = CouponForm()
    total = 0
    for p in cart:
        if p.product.status != 'None':
            total += p.variant.total_price * p.quantity
        else:
            total += p.product.total_price * p.quantity
            
    context = {'order':order,'category':category,'nums':nums,'form':form,'total':total}
    return render(request,'order/order.html',context)

def order_create(request):
    if request.method == 'POST':
        form = OrderForm(request.POST)
        if form.is_valid():
            data = form.cleaned_data
            code = get_random_string(length=8)
            order = Order.objects.create(user_id=request.user.id,email=data['email'],f_name=data['f_name'],l_name=data['l_name'],address=data['address'], code=code)
            cart = Cart.objects.filter(user_id=request.user.id)
            for c in cart:
                ItemOrder.objects.create(order_id=order.id,user_id=request.user.id,product_id=c.product_id,variant_id=c.variant_id,quantity=c.quantity)
            return redirect('order:order_detail',order.id)

@require_POST
def coupon_order(request,order_id):
    form = CouponForm(request.POST)
    time = jdatetime.datetime.now()
    if form.is_valid():
        code = form.cleaned_data['code']
        try:
            coupon = Coupon.objects.get(code__iexact=code,start__lte=time,end__gte=time,active=True)
        except Coupon.DoesNotExist:
            messages.error(request,'this code wrong','danger')
            return redirect('order:order_detail',order_id)
        order = Order.objects.get(id=order_id)
        order.discount = coupon.discount
        order.save()
    return redirect('order:order_detail',order_id)

MERCHANT = 'XXXXXXXX-XXXX-XXXX-XXXX-XXXXXXXXXXXX'
client = Client('https://www.zarinpal.com/pg/services/WebGate/wsdl')
description = "توضیحات مربوط به تراکنش را در این قسمت وارد کنید"  # Required
mobile = '09123456789'  # Optional
CallbackURL = 'http://localhost:8000/verify/' # Important: need to edit for realy server.

def send_request(request,price,order_id):
    global amount
    amount = price
    result = client.service.PaymentRequest(MERCHANT, amount, description, request.user.email, mobile, CallbackURL)
    if result.Status == 100:
        return redirect('https://www.zarinpal.com/pg/StartPay/' + str(result.Authority))
    else:
        order = Order.objects.get(id=order_id)
        order.paid = True
        order.save()
        cart = ItemOrder.objects.filter(order_id = order_id)
        for c in cart:
            product = Product.objects.get(id=c.product.id)
            product.sell += c.quantity
            product.save()

        return HttpResponse('Error code: ' + str(result.Status))

def verify(request):
    if request.GET.get('Status') == 'OK':
        result = client.service.PaymentVerification(MERCHANT, request.GET['Authority'], amount)
        if result.Status == 100:
            return HttpResponse('Transaction success.')
        elif result.Status == 101:
            return HttpResponse('Transaction submitted : ' + str(result.Status))
        else:
            return HttpResponse('Transaction failed. ' + str(result.Status))
    else:
        return HttpResponse('Transaction failed or canceled by user')

    # if c.product.status == 'None':
    #         product = Product.objects.get(id=c.product.id)
    #         product.amount -= c.quantity
    #         product.save()
    #     else:
    #         variant = Variants.objects.get(id=c.variant.id)
    #         variant.amount -= c.quantity
    #         variant.save()
