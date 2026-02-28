from django.db import models
from django.contrib.auth.models import User


class Headset(models.Model):
    name = models.CharField(max_length=150)
    brand = models.CharField(max_length=100)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    stock = models.PositiveIntegerField(default=0)
    description = models.TextField()
    is_wireless = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.brand} {self.name}"


class Order(models.Model):
    STATUS_CHOICES = [
        ('new', 'Новый'),
        ('processing', 'В обработке'),
        ('done', 'Завершен'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='new')
    created_at = models.DateTimeField(auto_now_add=True)

    def total_price(self):
        return sum(item.total_price for item in self.items.all())

    def __str__(self):
        return f"Заказ #{self.id}"


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    headset = models.ForeignKey(Headset, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()
    price_at_moment = models.DecimalField(max_digits=10, decimal_places=2)

    @property
    def total_price(self):
        return self.quantity * self.price_at_moment

    def save(self, *args, **kwargs):
        if not self.price_at_moment:
            self.price_at_moment = self.headset.price
        self.headset.stock -= self.quantity
        self.headset.save()
        super().save(*args, **kwargs)