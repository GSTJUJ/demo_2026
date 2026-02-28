from django.urls import path
from . import views

urlpatterns = [
    path('', views.guest_view, name='guest'),
    path('headsets/', views.headset_list, name='headset_list'),
    path('orders/', views.order_list, name='order_list'),
    path('headsets/create/', views.headset_create, name='headset_create'),
]