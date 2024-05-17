from datetime import datetime

from rest_framework import status
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response
from rest_framework.views import APIView
from inventory.models import Inventory
from inventory.utils import convert_str_to_datetime


class InventoryUpdateAPIView(APIView):
    def post(self, request, pk):
        try:
            updated_at_string = request.data.get('updated_at')
            updated_at = convert_str_to_datetime(updated_at_string)
            inventory = Inventory.optimistic_lock(pk, updated_at)

            quantity_change = int(request.data.get('quantity'))
            inventory.quantity = quantity_change
            inventory.save()

            return Response({'status': 'success', 'new_quantity': inventory.quantity}, status=status.HTTP_200_OK)
        except Inventory.DoesNotExist:
            return Response({'status': 'error', 'message': '재고를 찾을 수 없습니다'}, status=status.HTTP_404_NOT_FOUND)
        except ValidationError as e:
            return Response({'status': 'error', 'message': str(e)}, status=status.HTTP_409_CONFLICT)
