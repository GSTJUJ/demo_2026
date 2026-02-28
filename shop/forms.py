from django import forms
from .models import Car, Order, OrderItem


class CarForm(forms.ModelForm):
    class Meta:
        model = Car
        fields = "__all__"


class OrderForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ["status"]


class OrderItemForm(forms.ModelForm):
    class Meta:
        model = OrderItem
        fields = ["car", "quantity"]