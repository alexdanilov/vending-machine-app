from django.urls import path
from rest_framework.routers import SimpleRouter

from .views import AddUserDepositView, AuthToken, LogoutAllView, ResetUserDepositView, UsersAPI

router = SimpleRouter()
router.register('users', UsersAPI, basename='user')

urlpatterns = [
    path('login', AuthToken.as_view(), name='login'),
    path('logout/all', LogoutAllView.as_view(), name='logout-all'),
    path('deposit', AddUserDepositView.as_view(), name='user-add-deposit'),
    path('reset', ResetUserDepositView.as_view(), name='user-reset-deposit'),
] + router.urls

