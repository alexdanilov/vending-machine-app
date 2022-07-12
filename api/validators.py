from django.core.exceptions import ValidationError


def validate_cost(value):
    if value % 5 != 0:
        raise ValidationError('Cost can be in multiples of 5', params={'value': value})
