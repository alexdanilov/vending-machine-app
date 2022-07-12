from django.db import models, transaction
from rest_framework.exceptions import ValidationError

from api.validators import validate_cost
from users.models import User


class Product(models.Model):
    name = models.CharField(max_length=200)
    available = models.PositiveSmallIntegerField(default=1)
    cost = models.PositiveSmallIntegerField(default=0, validators=[validate_cost])

    seller = models.ForeignKey('users.User', on_delete=models.RESTRICT)

    def __str__(self) -> str:
        return f'Product #{self.id} {self.name} ({self.available})'

    def buy_products(self, count: int):
        self.available -= count
        self.save(update_fields=('available',))

    def buy(self, count: int, user: User):
        total_amount = self.cost * count
        if not user.has_deposit(total_amount):
            raise ValidationError('User does not have enough deposit')

        with transaction.atomic():
            self.buy_products(count)
            user.decrease_deposit(total_amount)
