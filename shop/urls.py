from django.urls import path
from . import views

urlpatterns = [
    path("", views.guest_view, name="guest"),

    path("login/", views.login_view, name="login"),
    path("logout/", views.logout_view, name="logout"),

    path("cars/", views.car_list, name="car_list"),
    path("cars/create/", views.car_create, name="car_create"),
    path("cars/update/<int:pk>/", views.car_update, name="car_update"),
    path("cars/delete/<int:pk>/", views.car_delete, name="car_delete"),

    path("orders/", views.order_list, name="order_list"),
    path("orders/create/", views.order_create, name="order_create"),
]