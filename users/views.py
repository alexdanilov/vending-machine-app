from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.exceptions import ValidationError
from rest_framework.fields import IntegerField
from rest_framework.response import Response
from rest_framework.serializers import ModelSerializer, Serializer
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet

from api.validators import validate_cost
from .models import User
from .permissions import IsBuyerPermission, IsSellerPermission


class UserSerializer(ModelSerializer):
    class Meta:
        model = User
        exclude = ()


class UsersAPI(ModelViewSet):
    '''
    CRUD endpoints for user
    '''
    model = User
    serializer_class = UserSerializer
    permission_classes = (IsSellerPermission,)

    def get_permissions(self) -> list:
        # allow anonymous users create profiles
        if self.action == 'create':
            return []

        # only sellers can change/delete profile
        return super().get_permissions()

    def get_queryset(self):
        return self.model.objects.get(id=self.request.user)


class DepositSerializer(Serializer):
    amount = IntegerField(validators=[validate_cost])


class AddUserDepositView(APIView):
    '''
    Endpoint for adding user deposit
    '''
    permission_classes = (IsBuyerPermission,)

    def post(self, request, *args, **kwargs):
        serializer = DepositSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        self.request.user.add_deposit(serializer.data['amount'])

        return Response({'success': True})


class ResetUserDepositView(APIView):
    '''
    Endpoint for resetting user deposit to 0.
    '''
    permission_classes = (IsBuyerPermission,)

    def post(self, request, *args, **kwargs):
        self.request.user.reset_deposit()
        return Response({'success': True})


class AuthToken(ObtainAuthToken):
    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)

        user = serializer.validated_data['user']

        message = ''
        # check other sessions
        if Token.objects.filter(user=user).exists():
            raise ValidationError('There is already an active session using your account')

        token = Token.objects.create(user=user)
        return Response({
            'token': token.key,
            'user': UserSerializer(user).data,
        }, status=status.HTTP_201_CREATED)


class LogoutAllView(APIView):
    def get(self, request, *args, **kwargs):
        Token.objects.filter(user=request.user).delete()
        return Response({'success': True})
