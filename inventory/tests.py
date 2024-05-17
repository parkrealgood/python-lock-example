from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from inventory.models import Inventory


class InventoryUpdateAPITestCase(APITestCase):
    def setUp(self):
        self.inventory = Inventory.objects.create(product_name='상품 1', quantity=10)

    def test_inventory_update_conflict(self):
        initial_quantity = self.inventory.quantity

        # 첫 번째 요청
        response1 = self.client.post(
            reverse(
                'inventory_update', args=[self.inventory.pk]
            ),
            {'version': self.inventory.version, 'quantity': 5}
        )
        self.assertEqual(response1.status_code, status.HTTP_200_OK)
        updated_inventory1 = Inventory.objects.get(pk=self.inventory.pk)
        self.assertEqual(updated_inventory1.quantity, initial_quantity + 5)

        # 두 번째 요청 (충돌 발생)
        response2 = self.client.post(
            reverse(
                'inventory_update', args=[self.inventory.pk]
            ),
            {'version': self.inventory.version, 'quantity': 3}
        )
        self.assertEqual(response2.status_code, status.HTTP_409_CONFLICT)
        updated_inventory2 = Inventory.objects.get(pk=self.inventory.pk)
        # 재고 업데이트가 되지 않아야 함
        self.assertEqual(updated_inventory2.quantity, updated_inventory1.quantity)

    def test_inventory_update_success(self):
        initial_quantity = self.inventory.quantity
        response = self.client.post(reverse('inventory_update', args=[self.inventory.pk]), {'version': self.inventory.version, 'quantity': 7})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        updated_inventory = Inventory.objects.get(pk=self.inventory.pk)
        # 재고가 정상적으로 업데이트되었는지 확인
        self.assertEqual(updated_inventory.quantity, initial_quantity + 7)
