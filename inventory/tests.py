from concurrent.futures import ThreadPoolExecutor, as_completed

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


class InventoryPurchaseTestCase(TestCase):

    def setUp(self):
        self.inventory = Inventory.objects.create(product_name='상품 1', quantity=10)

    def test_상품구매에_성공하다(self):
        response = self.client.post(
            f'/inventory/{self.inventory.id}/purchase/'
        )
        self.assertEqual(response.status_code, 200)
        response_json = response.json()

        self.inventory.refresh_from_db()
        self.assertEqual(self.inventory.quantity, 9)
        self.assertEqual(response_json['quantity'], 9)

    def test_동시에_상품구매에_성공하다(self):
        response = self.client.post(
            f'/inventory/{self.inventory.id}/purchase/'
        )
        self.assertEqual(response.status_code, 200)
        response_json = response.json()
        self.inventory.refresh_from_db()
        self.assertEqual(self.inventory.quantity, 9)
        self.assertEqual(response_json['quantity'], 9)

        response = self.client.post(
            f'/inventory/{self.inventory.id}/purchase/'
        )
        self.assertEqual(response.status_code, 200)
        response_json = response.json()
        self.inventory.refresh_from_db()
        self.assertEqual(self.inventory.quantity, 8)
        self.assertEqual(response_json['quantity'], 8)

    def test_상품_재고가소진되어_구매에_실패하다(self):
        self.inventory.quantity = 1
        self.inventory.save()
        self.inventory.refresh_from_db()

        response = self.client.post(
            f'/inventory/{self.inventory.id}/purchase/'
        )
        self.assertEqual(response.status_code, 200)
        response_json = response.json()
        self.inventory.refresh_from_db()
        self.assertEqual(self.inventory.quantity, 0)
        self.assertEqual(response_json['quantity'], 0)

        response = self.client.post(
            f'/inventory/{self.inventory.id}/purchase/'
        )
        response_json = response.json()
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response_json['message'], '재고가 없습니다.')

    def test_동시_상품구매(self):
        def purchase_inventory():
            response = self.client.post(
                f'/inventory/{self.inventory.pk}/purchase/'
            )
            return response.status_code == 200

        success_count, fail_count = 0, 0

        with ThreadPoolExecutor(max_workers=2) as executor:
            futures = [executor.submit(purchase_inventory) for _ in range(2)]

            results = []
            for future in as_completed(futures):
                result = future.result()
                results.append(result)
                if result:
                    success_count += 1
                else:
                    fail_count += 1

        self.assertEqual(success_count, 1)
        self.assertEqual(fail_count, 1)
