from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import Group
from .models import Headset, Order


def guest_view(request):
    headsets = Headset.objects.all()
    return render(request, 'guest.html', {'headsets': headsets})


@login_required
def headset_list(request):
    headsets = Headset.objects.all()

    # поиск
    search = request.GET.get('search')
    if search:
        headsets = headsets.filter(name__icontains=search)

    return render(request, 'headset_list.html', {'headsets': headsets})


@login_required
def order_list(request):
    if request.user.groups.filter(name='Manager').exists() or request.user.is_superuser:
        orders = Order.objects.all()
        return render(request, 'order_list.html', {'orders': orders})
    else:
        return redirect('headset_list')


@login_required
def headset_create(request):
    if not request.user.is_superuser:
        return redirect('headset_list')

    if request.method == "POST":
        name = request.POST['name']
        price = request.POST['price']
        Headset.objects.create(name=name, price=price, brand='Unknown', description='')
        return redirect('headset_list')

    return render(request, 'headset_form.html')