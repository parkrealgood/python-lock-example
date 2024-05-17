from django.core.exceptions import ObjectDoesNotExist
from django.db import models


class Inventory(models.Model):
    product_name = models.CharField(max_length=100)
    quantity = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'inventory'
        constraints = [
            models.UniqueConstraint(fields=['product_name'], name='unique_product_name')
        ]

    def __str__(self):
        return self.product_name

    @classmethod
    def optimistic_lock(cls, inventory_id, last_updated_at):
        try:
            inventory = cls.objects.get(id=inventory_id)
            # 클라이언트가 가진 버전과 DB의 버전이 다르면 충돌이 발생한 것으로 간주
            if inventory.updated_at != last_updated_at:
                raise ObjectDoesNotExist('동시성 문제로 인한 충돌 발생')
            return inventory
        except cls.DoesNotExist:
            raise ObjectDoesNotExist('해당 제품이 존재하지 않습니다.')
