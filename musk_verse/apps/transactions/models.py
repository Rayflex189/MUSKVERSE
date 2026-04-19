from django.db import models
from django.conf import settings

class Transaction(models.Model):
    PRODUCT_TYPES = [
        ('car', 'Car'),
        ('fancard', 'Fan Card'),
        ('membership', 'Membership Card'),
        ('stock', 'Stock'),
        ('crypto', 'Crypto'),
        ('investment', 'Investment Plan'),
    ]
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
    ]
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    product_type = models.CharField(max_length=20, choices=PRODUCT_TYPES)
    product_id = models.PositiveIntegerField()  # ID of the specific product
    amount = models.DecimalField(max_digits=16, decimal_places=2)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.email} - {self.product_type} - {self.amount}"
