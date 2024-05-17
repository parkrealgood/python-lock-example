from django.urls import path
from inventory.views import InventoryUpdateAPIView

urlpatterns = [
    path('<int:pk>/', InventoryUpdateAPIView.as_view(), name='inventory_update'),
]
