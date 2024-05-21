from django.db.models import F
from rest_framework import status
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response
from rest_framework.views import APIView
from django.db import transaction

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
        except Exception as e:
            return Response({'status': 'error', 'message': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class InventoryPurchaseAPIView(APIView):
    def post(self, request, pk):
        try:
            with transaction.atomic():
                # 비관적인 락 설정
                inventory = Inventory.objects.select_for_update().get(pk=pk)

                if inventory.quantity > 0:
                    # 상품 재고 감소
                    inventory.quantity = F('quantity') - 1
                    inventory.save()
                    inventory.refresh_from_db()
                    return Response({'status': 'success', 'quantity': inventory.quantity}, status=status.HTTP_200_OK)
                else:
                    return Response({'status': 'error', 'message': '재고가 없습니다.'}, status=status.HTTP_400_BAD_REQUEST)
        except Inventory.DoesNotExist:
            return Response({'status': 'error', 'message': '재고를 찾을 수 없습니다'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({'status': 'error', 'message': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
