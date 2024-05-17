from django.test import TestCase
from django.utils.timezone import localtime

from inventory.models import Inventory


class InventoryUpdateTestCase(TestCase):

    def setUp(self):
        self.inventory = Inventory.objects.create(product_name='상품 1', quantity=10)

    def test_인벤토리_수정에_성공하다(self):
        now = localtime()
        response = self.client.post(
            f'/inventory/{self.inventory.id}/', {'quantity': 5, 'updated_at': now}
        )
        self.assertEqual(response.status_code, 200)
        self.inventory.refresh_from_db()
        self.assertEqual(self.inventory.quantity, 5)

    def test_인벤토리_수정에_실패하다(self):
        now = localtime()
        response = self.client.post(
            f'/inventory/{self.inventory.id}/', {'quantity': 5, 'updated_at': now}
        )
        self.assertEqual(response.status_code, 200)
        self.inventory.refresh_from_db()
        self.assertEqual(self.inventory.quantity, 5)

        response = self.client.post(
            f'/inventory/{self.inventory.id}/', {'quantity': 7, 'updated_at': now}
        )
        self.assertEqual(response.status_code, 409)

    def test_인벤토리_수정실패후_재수정하다(self):
        now = localtime()
        response = self.client.post(
            f'/inventory/{self.inventory.id}/', {'quantity': 5, 'updated_at': now}
        )
        self.assertEqual(response.status_code, 200)

        response = self.client.post(
            f'/inventory/{self.inventory.id}/', {'quantity': 7, 'updated_at': now}
        )
        self.assertEqual(response.status_code, 409)

        now = localtime()
        response = self.client.post(
            f'/inventory/{self.inventory.id}/', {'quantity': 7, 'updated_at': now}
        )
        self.assertEqual(response.status_code, 200)
        self.inventory.refresh_from_db()
        self.assertEqual(self.inventory.quantity, 7)
