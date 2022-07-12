from unittest import TestCase

from django.urls import reverse
from rest_framework import status
from rest_framework.authtoken.models import Token

from api.tests import BaseTestCase, generate_username
from users.models import ROLE_BUYER, ROLE_SELLER, User


class UsersBusinessLogicTestCase(TestCase):
    def test_change_deposit(self):
        user = User.objects.create(username=generate_username())

        user.add_deposit(10)
        user.refresh_from_db()
        self.assertTrue(user.has_deposit(10))
        self.assertFalse(user.has_deposit(11))
        self.assertEqual(user.deposit, 10)

        user.decrease_deposit(5)
        user.refresh_from_db()
        self.assertTrue(user.has_deposit(5))
        self.assertFalse(user.has_deposit(6))
        self.assertEqual(user.deposit, 5)

        user.reset_deposit()
        user.refresh_from_db()
        self.assertEqual(user.deposit, 0)


class UsersTestCase(BaseTestCase):
    def test_create_user(self):
        new_user = {
            'username': generate_username(),
            'password': generate_username(),
            'role': ROLE_BUYER,
        }

        resp = self.client.post(reverse('user-list'), new_user)
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)

    def test_add_deposit(self):
        buyer_client = self.get_client_for_role(ROLE_BUYER)

        # deposit buyer with right amount
        resp = buyer_client.post(reverse('user-add-deposit'), {'amount': 10})
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        buyer = User.objects.get(id=self.buyer.id)
        self.assertEqual(buyer.deposit, 10)

        # deposit buyer with wrong amount
        resp = buyer_client.post(reverse('user-add-deposit'), {'amount': 9})
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)
        buyer = User.objects.get(id=self.buyer.id)
        self.assertEqual(buyer.deposit, 10)

        # deposit seller with wrong amount
        seller_client = self.get_client_for_role(ROLE_SELLER)
        resp = seller_client.post(reverse('user-add-deposit'), {'amount': 10})
        self.assertEqual(resp.status_code, status.HTTP_403_FORBIDDEN)
        seller = User.objects.get(id=self.seller.id)
        self.assertEqual(seller.deposit, 0)


class UserLoginTestCase(BaseTestCase):
    def test_user_login(self):
        password = generate_username()
        user = User.objects.create(username=generate_username(), role=ROLE_SELLER)
        user.set_password(password)
        user.save(update_fields=('password',))

        data = {
            'username': user.username,
            'password': password,
        }
        resp = self.client.post(reverse('login'), data)
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        self.assertTrue('token' in resp.data)
        token = resp.data['token']

        # let's login again
        data = {
            'username': user.username,
            'password': password,
        }
        resp = self.client.post(reverse('login'), data)
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(resp.data[0], 'There is already an active session using your account')

        # let's logout from all devices

        ## set token after last successful login
        self.set_token(self.client, token)

        resp = self.client.get(reverse('logout-all'))
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertFalse(Token.objects.filter(user=user).exists())
