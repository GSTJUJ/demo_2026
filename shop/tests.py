from django.test import TestCase
from django.contrib.auth.models import User
from django.urls import reverse

from .models import Car, Order, OrderItem


class CarModelTest(TestCase):
    """Тестирование модели Car"""

    def setUp(self):
        self.car = Car.objects.create(
            make="Toyota",
            model="Camry",
            year=2022,
            price=2500000.00,
            mileage_km=45000,
            description="Седан в отличном состоянии",
            is_new=False,
            stock=15,
        )

    def test_car_creation(self):
        """Проверка создания автомобиля"""
        self.assertEqual(self.car.make, "Toyota")
        self.assertEqual(self.car.model, "Camry")
        self.assertEqual(self.car.year, 2022)
        self.assertEqual(float(self.car.price), 2500000.00)
        self.assertEqual(self.car.mileage_km, 45000)
        self.assertFalse(self.car.is_new)
        self.assertEqual(self.car.stock, 15)


class OrderTest(TestCase):
    """Тестирование создания заказа и списания склада"""

    def setUp(self):
        self.user = User.objects.create_user(username="testuser", password="12345")

        self.car = Car.objects.create(
            make="BMW",
            model="X5",
            year=2021,
            price=6000000.00,
            mileage_km=70000,
            description="Тестовый автомобиль",
            is_new=False,
            stock=10,
        )

    def test_order_total_price_and_stock_decrease(self):
        """Проверка расчёта общей суммы заказа и уменьшения stock"""
        order = Order.objects.create(user=self.user)

        OrderItem.objects.create(
            order=order,
            car=self.car,
            quantity=3
        )

        order.refresh_from_db()

        # Проверяем сумму через property total_price (использует items + price_at_moment)
        self.assertEqual(float(order.total_price), 18000000.00)

        # Проверяем уменьшение остатка товара
        self.car.refresh_from_db()
        self.assertEqual(self.car.stock, 7)


class ViewTest(TestCase):
    """Тестирование представлений"""

    def setUp(self):
        self.user = User.objects.create_user(username="client", password="12345")

        Car.objects.create(
            make="Kia",
            model="Rio",
            year=2020,
            price=1200000.00,
            mileage_km=80000,
            description="Городской автомобиль",
            is_new=False,
            stock=20,
        )

    def test_guest_page_status_code(self):
        """Проверка доступности страницы для гостей"""
        # У нас guest_view привязан к path("", ...) => главная "/"
        response = self.client.get(reverse("guest"))
        self.assertEqual(response.status_code, 200)

    def test_login(self):
        """Проверка авторизации пользователя"""
        ok = self.client.login(username="client", password="12345")
        self.assertTrue(ok)

    def test_car_list_requires_login(self):
        """Проверка что каталог авто требует авторизацию"""
        response = self.client.get(reverse("car_list"))
        # Django redirect на login
        self.assertEqual(response.status_code, 302)

        self.client.login(username="client", password="12345")
        response2 = self.client.get(reverse("car_list"))
        self.assertEqual(response2.status_code, 200)