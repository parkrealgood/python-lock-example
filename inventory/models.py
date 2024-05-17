from django.core.exceptions import ObjectDoesNotExist
from django.db import models
from rest_framework.exceptions import ValidationError


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
    def optimistic_lock(cls, inventory_id, updated_at):
        inventory = cls.objects.get(id=inventory_id)
        # 업데이트 하고자 하는 데이터의 updated_at이 현재 데이터의 updated_at보다 작다면 다른 사용자가 수정한 것이므로 에러 발생
        if inventory.updated_at > updated_at:
            raise ValidationError('이미 다른 사용자가 수정했습니다. 다시 시도해주세요')
        return inventory
