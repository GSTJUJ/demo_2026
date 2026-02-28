from django.test import TestCase
from django.contrib.auth.models import User
from .models import Headset, Order, OrderItem


class HeadsetModelTest(TestCase):
    """Тестирование модели Headset"""

    def setUp(self):
        self.headset = Headset.objects.create(
            name="G Pro X",
            brand="Logitech",
            price=5000.00,
            description="Игровая гарнитура",
            is_wireless=False,
            stock=15
        )

    def test_headset_creation(self):
        """Проверка создания гарнитуры"""
        self.assertEqual(self.headset.name, "G Pro X")
        self.assertEqual(self.headset.brand, "Logitech")
        self.assertEqual(self.headset.price, 5000.00)
        self.assertFalse(self.headset.is_wireless)
        self.assertEqual(self.headset.stock, 15)


class OrderTest(TestCase):
    """Тестирование создания заказа и расчёта суммы"""

    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser",
            password="12345"
        )

        self.headset = Headset.objects.create(
            name="Cloud II",
            brand="HyperX",
            price=3000.00,
            description="Тестовая гарнитура",
            is_wireless=True,
            stock=10
        )

    def test_order_total_price(self):
        """Проверка расчёта общей суммы заказа"""

        order = Order.objects.create(user=self.user)

        OrderItem.objects.create(
            order=order,
            headset=self.headset,
            quantity=3
        )

        # Получаем элементы заказа напрямую
        items = OrderItem.objects.filter(order=order)

        total = sum(
            item.headset.price * item.quantity
            for item in items
        )

        self.assertEqual(total, 9000.00)

        # Проверяем уменьшение остатка товара
        self.headset.refresh_from_db()
        self.assertEqual(self.headset.stock, 7)


class ViewTest(TestCase):
    """Тестирование представлений"""

    def setUp(self):
        self.user = User.objects.create_user(
            username="client",
            password="12345"
        )

        Headset.objects.create(
            name="Arctis 7",
            brand="SteelSeries",
            price=7000.00,
            description="Беспроводная гарнитура",
            is_wireless=True,
            stock=20
        )

    def test_guest_page_status_code(self):
        """Проверка доступности страницы для гостей"""
        response = self.client.get('/shop/guest/')
        self.assertEqual(response.status_code, 200)

    def test_login(self):
        """Проверка авторизации пользователя"""
        login = self.client.login(username="client", password="12345")
        self.assertTrue(login)