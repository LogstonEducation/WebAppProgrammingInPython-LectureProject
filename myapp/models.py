from django.contrib.auth.models import User
from django.db import models


class Currency(models.Model):
    iso = models.CharField(max_length=3)
    long_name = models.CharField(max_length=50)

    def __str__(self):
        return f'{self.iso} {self.long_name}'


class Holding(models.Model):
    currency = models.ForeignKey(
        Currency,
        # When the related Currency is deleted, delete this Holding as well.
        on_delete=models.CASCADE,
    )
    value = models.FloatField(default=0.0)
    buy_date = models.DateField()

    def __str__(self):
        return f'{self.currency.iso}  {self.value} {self.buy_date}'


class Rates(models.Model):
    currency_one = models.ForeignKey(
        Currency,
        # When the related Currency is deleted, delete this Rate as well.
        on_delete=models.CASCADE,
        related_name='currency_one_rate_set',
    )
    currency_two = models.ForeignKey(
        Currency,
        # When the related Currency is deleted, delete this Rate as well.
        on_delete=models.CASCADE,
        related_name='currency_two_rate_set',
    )
    rate = models.FloatField(default=1.0)
    last_update_time = models.DateTimeField()

    def __str__(self):
        return f'{self.currency_one.iso} {self.currency_two.iso} {self.rate}'


class AccountHolder(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    date_of_birth = models.DateField()
    currencies_visited = models.ManyToManyField(Currency)

    def __str__(self):
        return f'{self.user.username}'


class City(models.Model):
    name = models.CharField(max_length=256)
    latitude = models.FloatField()
    longitude = models.FloatField()

    def __str__(self):
        return f'{self.name}'
