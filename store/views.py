import json
import datetime
from django.shortcuts import render, redirect
from .models import *
from django.http import JsonResponse
from .utils import cookieCart, cartData, guestOrder
from django.forms import ModelForm
from .forms import UserRegisterForm, ProductForm
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from .decorators import unauthenticated_user, staff_only
from django.contrib.auth.decorators import login_required
# Create your views here.


@unauthenticated_user
def registerUser(request):
    form = UserRegisterForm()

    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            user = form.save()

            username = form.cleaned_data.get('username')
            messages.success(request, "Account created for " + username)

            return redirect('login')

    context = {'form': form}

    return render(request, 'store/register.html', context)


@unauthenticated_user
def loginUser(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('store')
        else:
            messages.info(request, "Invalid Username or Password")

    context = {}
    return render(request, 'store/login.html', context)


@login_required(login_url='login')
def logoutUser(request):
    logout(request)
    messages.success(request, "You have been successfully logged-out")
    return redirect('store')


@staff_only
def allProducts(request):
    products = Product.objects.all()
    context = {'products': products, 'cartItems': 0}
    return render(request, 'store/products.html', context)


@staff_only
def createProduct(request):
    form = ProductForm()
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('products')
    context = {'form': form, 'cartItems': 0}
    return render(request, 'store/new_product.html', context)


def store(request):
    data = cartData(request)
    items = data['items']
    order = data['order']
    cartItems = data["cartItems"]

    products = Product.objects.all()
    context = {"products": products, "cartItems": cartItems}

    return render(request, 'store/store.html', context)


def cart(request):
    data = cartData(request)
    items = data['items']
    order = data['order']
    cartItems = data["cartItems"]

    context = {"items": items, "order": order, "cartItems": cartItems}
    return render(request, 'store/cart.html', context)


def checkout(request):
    data = cartData(request)
    items = data['items']
    order = data['order']
    cartItems = data["cartItems"]

    context = {"items": items, "order": order, "cartItems": cartItems}
    return render(request, 'store/checkout.html', context)


def updateItem(request):
    data = json.loads(request.body)
    productId = data['productId']
    action = data['action']

    customer = request.user.customer
    product = Product.objects.get(id=productId)
    order, created = Order.objects.get_or_create(
        customer=customer, complete=False)
    orderItem, created = OrderItem.objects.get_or_create(
        order=order, product=product)

    if action == 'add':
        orderItem.quantity += 1
    elif action == 'remove':
        orderItem.quantity -= 1

    orderItem.save()

    if orderItem.quantity <= 0:
        orderItem.delete()

    return JsonResponse('item added', safe=False)


def processOrder(request):
    transaction_id = datetime.datetime.now().timestamp()
    data = json.loads(request.body)

    if request.user.is_authenticated:
        customer = request.user.customer
        order, created = Order.objects.get_or_create(
            customer=customer, complete=False)

    else:
        print('User not logged in')

        print("COOKIES:", request.COOKIES)

        customer, order = guestOrder(request, data)

    total = float(data['userFormData']['total'])
    order.transaction_id = transaction_id

    if total == float(order.get_cart_total):
        order.complete = True
    order.save()

    if order.shipping == True:
        ShippingAddress.objects.create(
            customer=customer,
            order=order,
            address=data['userShippingData']['address'],
            city=data['userShippingData']['city'],
            state=data['userShippingData']['state'],
            zipcode=data['userShippingData']['zipcode']
        )

    return JsonResponse('Payment Done', safe=False)
