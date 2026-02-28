from django.db import models, transaction
from django.db.models import F
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError


class Car(models.Model):
    make = models.CharField("Марка", max_length=80)              # Toyota
    model = models.CharField("Модель", max_length=120)           # Camry
    year = models.PositiveIntegerField("Год", default=2020)
    price = models.DecimalField("Цена", max_digits=12, decimal_places=2)
    mileage_km = models.PositiveIntegerField("Пробег (км)", default=0)
    stock = models.PositiveIntegerField("В наличии (шт)", default=0)
    description = models.TextField("Описание", blank=True)
    is_new = models.BooleanField("Новый авто", default=False)

    def __str__(self) -> str:
        return f"{self.make} {self.model} ({self.year})"


class Order(models.Model):
    STATUS_CHOICES = [
        ("new", "Новый"),
        ("processing", "В обработке"),
        ("done", "Завершен"),
        ("canceled", "Отменен"),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="new")
    created_at = models.DateTimeField(auto_now_add=True)

    @property
    def total_price(self):
        return sum(item.total_price for item in self.items.all())

    def __str__(self) -> str:
        return f"Заказ #{self.id}"


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="items")
    car = models.ForeignKey(Car, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    price_at_moment = models.DecimalField(max_digits=12, decimal_places=2, blank=True, null=True)

    @property
    def total_price(self):
        return self.quantity * (self.price_at_moment or 0)

    def clean(self):
        if self.quantity <= 0:
            raise ValidationError({"quantity": "Количество должно быть >= 1"})

    def save(self, *args, **kwargs):
        creating = self._state.adding
        if creating and (self.price_at_moment is None):
            self.price_at_moment = self.car.price

        self.full_clean()

        if creating:
            # списываем склад атомарно
            with transaction.atomic():
                updated = Car.objects.filter(pk=self.car_id, stock__gte=self.quantity).update(
                    stock=F("stock") - self.quantity
                )
                if updated == 0:
                    raise ValidationError("Недостаточно автомобилей на складе для оформления позиции заказа.")
                super().save(*args, **kwargs)
        else:
            # обновление позиции без повторного списания
            super().save(*args, **kwargs)