from rest_framework.permissions import IsAuthenticated

from users.models import ROLE_BUYER, ROLE_SELLER


class IsBuyerPermission(IsAuthenticated):
    def has_permission(self, request, view):
        return super().has_permission(request, view) and request.user.role == ROLE_BUYER


class IsSellerPermission(IsAuthenticated):
    def has_permission(self, request, view):
        return super().has_permission(request, view) and request.user.role == ROLE_SELLER
