from rest_framework.exceptions import ValidationError
from rest_framework.fields import IntegerField
from rest_framework.response import Response
from rest_framework.serializers import ModelSerializer, Serializer
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet

from users.permissions import IsBuyerPermission, IsSellerPermission
from .models import Product


class ProductSerializer(ModelSerializer):
    class Meta:
        model = Product
        exclude = ('seller',)


class ProductsAPI(ModelViewSet):
    '''
    CRUD endpoints for product
    '''
    model = Product
    permission_classes = (IsSellerPermission,)
    serializer_class = ProductSerializer

    def get_queryset(self):
        return self.model.objects.filter(seller=self.request.user)

    def perform_create(self, serializer):
        serializer.save(seller=self.request.user)


class BuyProductSerializer(Serializer):
    product_id = IntegerField()
    count = IntegerField()

    product = None

    def validate(self, attrs):
        self.product = Product.objects.get(id=attrs['product_id'])
        if self.product.available < attrs['count']:
            raise ValidationError('Not enough available count of product')

        return attrs


class BuyProductView(APIView):
    '''
    Endpoint for buy product
    '''
    permission_classes = (IsBuyerPermission,)

    def post(self, request, *args, **kwargs):
        serializer = BuyProductSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.product.buy(serializer.data['count'], self.request.user)

        return Response({'success': True})