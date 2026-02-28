from django import forms
from .models import Headset, Order, OrderItem


class HeadsetForm(forms.ModelForm):
    class Meta:
        model = Headset
        fields = '__all__'


class OrderForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ['status']


class OrderItemForm(forms.ModelForm):
    class Meta:
        model = OrderItem
        fields = ['headset', 'quantity']