from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from django.core.exceptions import ValidationError

from .models import Car, Order, OrderItem
from .forms import CarForm, OrderItemForm


def is_manager(user) -> bool:
    return user.groups.filter(name="Manager").exists()


def is_client(user) -> bool:
    return user.groups.filter(name="Client").exists()


def login_view(request):
    if request.user.is_authenticated:
        return redirect("car_list")

    error = None
    if request.method == "POST":
        username = request.POST.get("username", "").strip()
        password = request.POST.get("password", "")
        user = authenticate(request, username=username, password=password)
        if user:
            login(request, user)
            return redirect("car_list")
        error = "Неверный логин или пароль"

    return render(request, "login.html", {"error": error})


def logout_view(request):
    logout(request)
    return redirect("login")


def guest_view(request):
    cars = Car.objects.all().order_by("-id")
    return render(request, "guest.html", {"cars": cars})


@login_required
def car_list(request):
    cars = Car.objects.all()

    search = request.GET.get("search")
    sort = request.GET.get("sort")

    if search:
        cars = cars.filter(make__icontains=search) | cars.filter(model__icontains=search)

    if sort == "price":
        cars = cars.order_by("price")
    elif sort == "year":
        cars = cars.order_by("-year")

    return render(request, "headset_list.html", {"cars": cars})
    # (шаблон можно переименовать позже; пока используем твой файл headset_list.html)


@login_required
def car_create(request):
    if not request.user.is_superuser:
        return redirect("car_list")

    form = CarForm(request.POST or None)
    if form.is_valid():
        form.save()
        return redirect("car_list")
    return render(request, "headset_form.html", {"form": form})


@login_required
def car_update(request, pk: int):
    if not request.user.is_superuser:
        return redirect("car_list")

    car = get_object_or_404(Car, pk=pk)
    form = CarForm(request.POST or None, instance=car)
    if form.is_valid():
        form.save()
        return redirect("car_list")
    return render(request, "headset_form.html", {"form": form})


@login_required
def car_delete(request, pk: int):
    if not request.user.is_superuser:
        return redirect("car_list")
    car = get_object_or_404(Car, pk=pk)
    car.delete()
    return redirect("car_list")


@login_required
def order_list(request):
    if is_manager(request.user) or request.user.is_superuser:
        orders = Order.objects.all().order_by("-id")
    else:
        orders = Order.objects.filter(user=request.user).order_by("-id")

    return render(request, "order_list.html", {"orders": orders})


@login_required
def order_create(request):
    error = None

    if request.method == "POST":
        form = OrderItemForm(request.POST)
        if form.is_valid():
            order = Order.objects.create(user=request.user)
            item = form.save(commit=False)
            item.order = order
            try:
                item.save()
                return redirect("order_list")
            except ValidationError as e:
                error = e.messages[0] if hasattr(e, "messages") else str(e)
                order.delete()
        else:
            error = "Проверьте поля формы"
    else:
        form = OrderItemForm()

    return render(request, "order_form.html", {"form": form, "error": error})