from uuid import uuid4

from django.test import TestCase
from rest_framework.authtoken.models import Token
from rest_framework.test import APIClient

from users.models import ROLE_BUYER, ROLE_SELLER, User


def generate_username():
    return str(uuid4())[:10]

class BaseTestCase(TestCase):
    def setUp(self) -> None:
        self.client = APIClient()

        self.buyer = User.objects.create(role=ROLE_BUYER, username=generate_username())
        self.seller = User.objects.create(role=ROLE_SELLER, username=generate_username())

    def set_token(self, client: APIClient, token: str):
        client.credentials(HTTP_AUTHORIZATION='Token ' + token)

    def get_client_for_role(self, role: str) -> APIClient:
        user = self.buyer if role == ROLE_BUYER else self.seller
        self.token = Token.objects.create(user=user)

        client = APIClient()
        self.set_token(client, str(self.token.key))
        return client
