from django.urls import reverse
from rest_framework import status

from api.tests import BaseTestCase
from products.models import Product
from users.models import ROLE_BUYER, ROLE_SELLER, User


class ProductsBusinessLogicTestCase(BaseTestCase):
    def test_change_availability(self):
        product = Product.objects.create(name='test', seller=self.seller, cost=10, available=5)

        product.buy_products(2)
        product.refresh_from_db()
        self.assertEqual(product.available, 3)

    def test_buy(self):
        product = Product.objects.create(name='test', seller=self.seller, cost=10, available=5)
        initial_amount = 100
        self.buyer.add_deposit(initial_amount)

        products_count = 4
        product.buy(products_count, self.buyer)
        product.refresh_from_db()
        self.buyer.refresh_from_db()
        self.assertEqual(product.available, 1)
        self.assertEqual(self.buyer.deposit, initial_amount - products_count * product.cost)


class ProductsTestCase(BaseTestCase):
    def test_buy_product(self):
        product = Product.objects.create(name='Test 2', seller=self.seller, available=3, cost=10)
        buyer_client = self.get_client_for_role(ROLE_BUYER)

        buyer_amount = product.cost * product.available + 10
        self.buyer.add_deposit(buyer_amount)

        data = {'product_id': product.id, 'count': 2}
        resp = buyer_client.post(reverse('product-buy'), data=data)
        self.assertEqual(resp.status_code, status.HTTP_200_OK)

        # check we changed available count
        changed_product = Product.objects.get(id=product.id)
        self.assertEqual(changed_product.available, product.available - data['count'])

        # check we withdraw some money
        buyer = User.objects.get(id=self.buyer.id)
        self.assertEqual(buyer.deposit, buyer_amount - product.cost * data['count'])

        # check we can't buy more than available products
        data = {'product_id': product.id, 'count': 5}
        resp = buyer_client.post(reverse('product-buy'), data=data)
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(resp.data['non_field_errors'][0], 'Not enough available count of product')

        # check seller can't perform a call
        seller_client = self.get_client_for_role(ROLE_SELLER)
        resp = seller_client.post(reverse('product-buy'), data=data)
        self.assertEqual(resp.status_code, status.HTTP_403_FORBIDDEN)

    def test_get_product(self):
        seller_client = self.get_client_for_role(ROLE_SELLER)
        product = Product.objects.create(name='Test 2', seller=self.seller, available=1, cost=10)

        resp = seller_client.get(reverse('product-detail', kwargs={'pk': product.id}))
        self.assertEqual(resp.status_code, status.HTTP_200_OK)

        self.assertEqual(resp.data['name'], product.name)
        self.assertEqual(resp.data['available'], product.available)

        # test buyer can't perform a call
        buyer_client = self.get_client_for_role(ROLE_BUYER)
        resp = buyer_client.get(reverse('product-detail', kwargs={'pk': product.id}))
        self.assertEqual(resp.status_code, status.HTTP_403_FORBIDDEN)

    def test_create_product(self):
        seller_client = self.get_client_for_role(ROLE_SELLER)

        data = {
            'name': 'Test',
            'count': 10,
            'available': 3,
        }
        resp = seller_client.post(reverse('product-list'), data)
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)

    def test_change_product(self):
        seller_client = self.get_client_for_role(ROLE_SELLER)
        product = Product.objects.create(name='Test 2', seller=self.seller, available=1, cost=10)

        data = {
            'name': 'Test',
            'available': 3,
        }
        resp = seller_client.patch(reverse('product-detail', kwargs={'pk': product.id}), data)
        self.assertEqual(resp.status_code, status.HTTP_200_OK)

        changed_product = Product.objects.get(id=product.id)
        self.assertEqual(changed_product.name, data['name'])
        self.assertEqual(changed_product.available, data['available'])

        # test buyer can't perform a call
        buyer_client = self.get_client_for_role(ROLE_BUYER)
        resp = buyer_client.patch(reverse('product-detail', kwargs={'pk': product.id}), data)
        self.assertEqual(resp.status_code, status.HTTP_403_FORBIDDEN)

    def test_delete_product(self):
        seller_client = self.get_client_for_role(ROLE_SELLER)
        product = Product.objects.create(name='Test 2', seller=self.seller, available=1, cost=10)

        resp = seller_client.delete(reverse('product-detail', kwargs={'pk': product.id}))
        self.assertEqual(resp.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Product.objects.filter(id=product.id).exists())

        # test buyer can't perform a call
        buyer_client = self.get_client_for_role(ROLE_BUYER)
        product = Product.objects.create(name='Test 2', seller=self.seller, available=1, cost=10)
        resp = buyer_client.delete(reverse('product-detail', kwargs={'pk': product.id}))
        self.assertEqual(resp.status_code, status.HTTP_403_FORBIDDEN)
