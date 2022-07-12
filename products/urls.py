from django.urls import path
from rest_framework.routers import SimpleRouter

from .views import BuyProductView, ProductsAPI

router = SimpleRouter()
router.register('products', ProductsAPI, basename='product')

urlpatterns = [
    path('buy', BuyProductView.as_view(), name='product-buy'),
] + router.urls

