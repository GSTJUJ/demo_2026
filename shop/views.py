from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import Group
from .models import Headset, Order, OrderItem
from .forms import HeadsetForm, OrderForm, OrderItemForm


def is_manager(user):
    return user.groups.filter(name='Manager').exists()


def is_client(user):
    return user.groups.filter(name='Client').exists()


# Авторизация
def login_view(request):
    if request.method == "POST":
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)

        if user:
            login(request, user)
            return redirect('headset_list')

    return render(request, 'login.html')


def logout_view(request):
    logout(request)
    return redirect('login')


# Гость
def guest_view(request):
    headsets = Headset.objects.all()
    return render(request, 'guest.html', {'headsets': headsets})


# Список товаров
@login_required
def headset_list(request):
    headsets = Headset.objects.all()

    if is_manager(request.user) or request.user.is_superuser:
        search = request.GET.get('search')
        sort = request.GET.get('sort')

        if search:
            headsets = headsets.filter(name__icontains=search)

        if sort == 'price':
            headsets = headsets.order_by('price')

    return render(request, 'headset_list.html', {'headsets': headsets})


# CRUD товара (только админ)
@login_required
def headset_create(request):
    if not request.user.is_superuser:
        return redirect('headset_list')

    form = HeadsetForm(request.POST or None)
    if form.is_valid():
        form.save()
        return redirect('headset_list')

    return render(request, 'headset_form.html', {'form': form})


@login_required
def headset_update(request, pk):
    if not request.user.is_superuser:
        return redirect('headset_list')

    headset = get_object_or_404(Headset, pk=pk)
    form = HeadsetForm(request.POST or None, instance=headset)

    if form.is_valid():
        form.save()
        return redirect('headset_list')

    return render(request, 'headset_form.html', {'form': form})


@login_required
def headset_delete(request, pk):
    if not request.user.is_superuser:
        return redirect('headset_list')

    headset = get_object_or_404(Headset, pk=pk)
    headset.delete()
    return redirect('headset_list')


# Заказы
@login_required
def order_list(request):
    if is_manager(request.user) or request.user.is_superuser:
        orders = Order.objects.all()
    else:
        orders = Order.objects.filter(user=request.user)

    return render(request, 'order_list.html', {'orders': orders})


@login_required
def order_create(request):
    order = Order.objects.create(user=request.user)

    if request.method == "POST":
        form = OrderItemForm(request.POST)
        if form.is_valid():
            item = form.save(commit=False)
            item.order = order
            item.price_at_moment = item.headset.price
            item.save()
            return redirect('order_list')
    else:
        form = OrderItemForm()

    return render(request, 'order_form.html', {'form': form})