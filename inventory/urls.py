from django.urls import path
from inventory.views import InventoryUpdateAPIView, InventoryPurchaseAPIView

urlpatterns = [
    path('<int:pk>/', InventoryUpdateAPIView.as_view(), name='inventory_update'),
    path('<int:pk>/purchase/', InventoryPurchaseAPIView.as_view(), name='inventory_purchase'),
]
