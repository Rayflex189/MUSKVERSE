from django.db import models

class Car(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    price = models.DecimalField(max_digits=12, decimal_places=2)
    image = models.ImageField(upload_to='cars/', blank=True, null=True)
    availability = models.BooleanField(default=True)

    def __str__(self):
        return self.name

class FanCard(models.Model):
    name = models.CharField(max_length=100)
    benefits = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    image = models.ImageField(upload_to='fancards/', blank=True, null=True)

class MembershipCard(models.Model):
    TIER_CHOICES = [('bronze', 'Bronze'), ('silver', 'Silver'), ('gold', 'Gold'), ('platinum', 'Platinum')]
    name = models.CharField(max_length=100)
    tier = models.CharField(max_length=20, choices=TIER_CHOICES)
    benefits = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)

class Stock(models.Model):
    name = models.CharField(max_length=100)
    symbol = models.CharField(max_length=10, unique=True)
    price = models.DecimalField(max_digits=12, decimal_places=2)
    available_quantity = models.PositiveIntegerField()

class CryptoAsset(models.Model):
    name = models.CharField(max_length=100)
    symbol = models.CharField(max_length=10, unique=True)
    price = models.DecimalField(max_digits=16, decimal_places=8)
    fractional_allowed = models.BooleanField(default=True)

class InvestmentPlan(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    roi_percentage = models.DecimalField(max_digits=5, decimal_places=2)
    duration = models.PositiveIntegerField(help_text="Duration in days")
    minimum_amount = models.DecimalField(max_digits=12, decimal_places=2)
