from django.contrib.auth.base_user import AbstractBaseUser, BaseUserManager
from django.db import models


ROLE_BUYER = 'b'
ROLE_SELLER = 's'

ROLES = (
    (ROLE_BUYER, 'Buyer'),
    (ROLE_SELLER, 'Seller'),
)

class User(AbstractBaseUser):
    username = models.CharField(max_length=30, unique=True)

    deposit = models.IntegerField(default=0)
    role = models.CharField(max_length=1, choices=ROLES)

    USERNAME_FIELD = 'username'

    objects = BaseUserManager()

    def __str__(self) -> str:
        return f'User #{self.id} {self.username} ({self.role_name})'

    def add_deposit(self, value: int) -> None:
        self.deposit += value
        self.save(update_fields=('deposit',))

    def has_deposit(self, value) -> bool:
        return self.deposit >= value

    def decrease_deposit(self, value) -> None:
        self.add_deposit(value * -1)

    def role_name(self) -> str:
        return dict(ROLES).get(self.role, '')

    def reset_deposit(self) -> None:
        self.deposit = 0
        self.save(update_fields=('deposit',))

    def is_buyer(self) -> bool:
        return self.role == ROLE_BUYER
