from django.shortcuts import render, get_object_or_404, redirect
from .models import *
from django.contrib import messages
from .forms import *
from django.db.models import Q,Max,Min,Count,Sum
from cart.models import *
from cart.views import *
from django.core.mail import EmailMessage
from django.core.paginator import Paginator
from .filters import ProductFilter
from urllib.parse import urlencode


def home(request):
    products = Product.objects.all()
    category = Category.objects.filter(sub_cat=False)
    gallery = Gallery.objects.all()
    create = Product.objects.all().order_by('-create')[:6]
    data = 'pants'
    create2 = products.filter(Q(name__icontains=data))
    nums = Cart.objects.filter(user_id=request.user.id).aggregate(sum=Sum('quantity'))['sum']
    return render(request,'home/home.html',{'category':category,'gallery':gallery,'create':create,'create2':create2,'nums':nums})

def all_product(request,slug=None,id=None):
    products = Product.objects.all()
    # form = CompareForm()
    nums = Cart.objects.filter(user_id=request.user.id).aggregate(sum=Sum('quantity'))['sum']
    min = Product.objects.aggregate(unit_price=Min('unit_price'))
    min_price = int(min['unit_price'])
    max = Product.objects.aggregate(unit_price=Max('unit_price'))
    max_price = int(max['unit_price'])

    filter = ProductFilter(request.GET,queryset=products)
    products = filter.qs
    
    paginator = Paginator(products,12)
    page_num = request.GET.get('page')
    data = request.GET.copy()
    if 'page' in data:
        del data['page']

    page_obj = paginator.get_page(page_num)
    category = Category.objects.filter(sub_cat=False)
    if slug and id:
        data = get_object_or_404(Category,slug=slug,id=id)
        page_obj = products.filter(category=data)
        paginator = Paginator(page_obj,6)
        page_num = request.GET.get('page')
        data = request.GET.copy()
        if 'page' in data:
            del data['page']
        page_obj = paginator.get_page(page_num)
    s_form = SearchForm()
    if 'search' in request.GET:
        s_form = SearchForm(request.GET)
        if s_form.is_valid():
            info = s_form.cleaned_data['search']
            page_obj = products.filter(Q(name__icontains=info))
            paginator = Paginator(page_obj, 6)
            page_num = request.GET.get('page')
            data = request.GET.copy()
            if 'page' in data:
                del data['page']
            page_obj = paginator.get_page(page_num)
    return render(request,'home/product.html',{'products':page_obj,'category':category,'nums':nums,'s_form':s_form,'page_num':page_num,'filter':filter,'min_price':min_price,'max_price':max_price,'data':urlencode(data)})

def product_detail(request,id):
    product = get_object_or_404(Product,id=id)
    category = Category.objects.filter(sub_cat=False)
    nums = Cart.objects.filter(user_id=request.user.id).aggregate(sum=Sum('quantity'))['sum']
    images = Images.objects.filter(product_id=id)
    comment_form = CommentForm()
    reply_form = ReplyForm()
    cart_form = CartForm()
    comments = Comment.objects.filter(product_id=id,is_reply=False)
    similar = product.tags.similar_objects()[:6]
    is_like = False
    if product.like.filter(id=request.user.id).exists():
        is_like = True

    is_unlike = False
    if product.unlike.filter(id=request.user.id).exists():
        is_unlike = True

    is_favourite = False
    if product.favourite.filter(id=request.user.id).exists():
        is_favourite = True


    if product.status != 'None':
        if request.method == 'POST':
            variant = Variants.objects.filter(product_variant_id=id)
            var_id = request.POST.get('select')
            variants = Variants.objects.get(id=var_id)
            colors = Variants.objects.filter(product_variant_id=id,size_variant_id=variants.size_variant_id)
            size = Variants.objects.raw('SELECT * FROM home_variants WHERE product_variant_id=%s GROUP BY size_variant_id', [id])

        else:
            variant = Variants.objects.filter(product_variant_id=id)
            variants = Variants.objects.get(id=variant[0].id)
            colors = Variants.objects.filter(product_variant_id=id,size_variant_id=variants.size_variant_id)
            size = Variants.objects.raw('SELECT * FROM home_variants WHERE product_variant_id=%s GROUP BY size_variant_id', [id])

            
        context = {'product':product,'category':category,'nums':nums,'variant':variant,'variants':variants,'similar':similar, 'is_like':is_like, 'is_unlike':is_unlike,'comments':comments,'comment_form':comment_form,'reply_form':reply_form,'images':images,'cart_form':cart_form,'is_favourite':is_favourite,'colors':colors,'size':size}
        return render(request, 'home/detail.html',context)
    else:
        return render(request,'home/detail.html',{'product':product,'nums':nums,'similar':similar, 'is_like':is_like,'is_unlike':is_unlike,'comments':comments,'comment_form':comment_form,'reply_form':reply_form,'images':images,'cart_form':cart_form,'is_favourite':is_favourite})

def product_like(request,id):
    url = request.META.get('HTTP_REFERER')
    product = get_object_or_404(Product,id=id)
    is_like = False
    if product.like.filter(id=request.user.id).exists():
        product.like.remove(request.user)
        is_like = False
        messages.success(request,'remove','success')
    else:
        product.like.add(request.user)
        is_like = True
        messages.success(request,'add','success')
    return redirect(url)

def product_unlike(request,id):
    url = request.META.get('HTTP_REFERER')
    product = get_object_or_404(Product,id=id)
    product.unlike.add(request.user)
    messages.success(request,'add like','dark')
    return redirect(url)

def product_comment(request,id):
    url = request.META.get('HTTP_REFERER')
    if request.method == 'POST':
        comment_form = CommentForm(request.POST)
        if comment_form.is_valid():
            data = comment_form.cleaned_data
            Comment.objects.create(comment=data['comment'],rate=data['rate'],user_id=request.user.id,product_id =id)
            return redirect(url)


def product_reply(request,id,comment_id):
    url = request.META.get('HTTP_REFERER')
    if request.method == 'POST':
        reply_form = ReplyForm(request.POST)
        if reply_form.is_valid():
            data = reply_form.cleaned_data
            Comment.objects.create(comment=data['comment'],user_id=request.user.id,product_id =id,reply_id=comment_id,is_reply=True)
            messages.success(request,'tnx for reply','primary')
            return redirect(url)

def comment_like(request,id):
    url = request.META.get('HTTP_REFERER')
    comment = Comment.objects.get(id=id)
    if comment.comment_like.filter(id=request.user.id).exists():
        comment.comment_like.remove(request.user)
    else:
        comment.comment_like.add(request.user)
        messages.success(request,'tnx for like comment','warning')
    return redirect(url)

# def product_search(request):
#     products = Product.objects.all()
#     if request.method == 'POST':
#         form = SearchForm(request.POST)
#         if form.is_valid():
#             data = form.cleaned_data['search']
#             if data.is_digit():
#                 products = products.filter(Q(discount__exact=data)|Q(unit_price__exact=data))
#             else:
#                 products = products.filter(Q(name__contains=data))
#             return render(request,'home/product.html',{'products':products,'form':form})

def favourite_product(request,id):
    url = request.META.get('HTTP_REFERER')
    product = Product.objects.get(id=id)
    is_favourite = False
    if product.favourite.filter(id=request.user.id).exists():
        product.favourite.remove(request.user)
        product.total_favourite -= 1
        product.save()
        is_favourite = False
    else:
        product.favourite.add(request.user)
        product.total_favourite += 1
        product.save()
        is_favourite = True

    return redirect(url)

def favourite_remove(request,id):
    url = request.META.get('HTTP_REFERER')
    product = Product.objects.get(id=id)
    product.favourite.remove(request.user)
    return redirect(url)

def contact(request):
    # if request.method == 'POST':
    #     subject = request.POST['subject']
    #     email = request.POST['email']
    #     msg = request.POST['message']
    #     body = subject + '\n' + email + '\n' + msg
    #     form = EmailMessage(
    #         'contact form',
    #         body,
    #         'test',
    #         ('villolin68@gmail.com',),
    #     )
    #     form.send(fail_silently=False)
    return render(request,'home/contact.html')

