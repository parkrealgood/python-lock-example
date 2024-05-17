from rest_framework import status
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response
from rest_framework.views import APIView
from inventory.models import Inventory


class InventoryUpdateAPIView(APIView):
    def post(self, request, pk):
        try:
            inventory = Inventory.objects.get(pk=pk)
            last_updated_at = request.data.get('updated_at')
            if inventory.updated_at != last_updated_at:
                raise ValidationError('이미 다른 사용자가 수정했습니다. 다시 시도해주세요')

            quantity_change = int(request.data.get('quantity'))
            inventory.quantity += quantity_change
            inventory.save()

            return Response({'status': 'success', 'new_quantity': inventory.quantity}, status=status.HTTP_200_OK)
        except Inventory.DoesNotExist:
            return Response({'status': 'error', 'message': '재고를 찾을 수 없습니다'}, status=status.HTTP_404_NOT_FOUND)
