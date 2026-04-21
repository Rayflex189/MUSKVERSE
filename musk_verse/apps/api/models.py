from django.db import models
from django.conf import settings
from django.utils import timezone
import secrets
import json

class APIKey(models.Model):
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('inactive', 'Inactive'),
        ('revoked', 'Revoked'),
    ]
    
    name = models.CharField(max_length=100, help_text="Name to identify this API key")
    key = models.CharField(max_length=64, unique=True, editable=False)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    permissions = models.JSONField(default=dict, help_text="JSON object with permission scopes")
    allowed_ips = models.JSONField(default=list, help_text="List of allowed IP addresses")
    rate_limit_per_minute = models.IntegerField(default=60)
    rate_limit_per_hour = models.IntegerField(default=1000)
    rate_limit_per_day = models.IntegerField(default=10000)
    expires_at = models.DateTimeField(null=True, blank=True)
    last_used = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def save(self, *args, **kwargs):
        if not self.key:
            self.key = secrets.token_urlsafe(32)
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"{self.name} - {self.status}"
    
    class Meta:
        ordering = ['-created_at']
        app_label = 'api'


class APIUsageLog(models.Model):
    api_key = models.ForeignKey(APIKey, on_delete=models.SET_NULL, null=True)
    endpoint = models.CharField(max_length=500)
    method = models.CharField(max_length=10)
    status_code = models.IntegerField()
    response_time = models.IntegerField(help_text="Response time in milliseconds")
    response_size = models.IntegerField(help_text="Response size in bytes", null=True, blank=True)
    ip_address = models.GenericIPAddressField()
    user_agent = models.TextField(blank=True)
    request_data = models.TextField(blank=True, help_text="JSON string of request data")
    response_data = models.TextField(blank=True, help_text="JSON string of response data")
    timestamp = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['timestamp']),
            models.Index(fields=['api_key', 'timestamp']),
            models.Index(fields=['status_code']),
        ]
        app_label = 'api'

    
    def __str__(self):
        return f"{self.method} {self.endpoint} - {self.status_code} ({self.response_time}ms)"

class APIRateLimit(models.Model):
    api_key = models.ForeignKey(APIKey, on_delete=models.CASCADE, null=True, blank=True)
    endpoint_pattern = models.CharField(max_length=200, default="*")
    method = models.CharField(max_length=10, default="*")
    limit_per_minute = models.IntegerField(default=60)
    limit_per_hour = models.IntegerField(default=1000)
    limit_per_day = models.IntegerField(default=10000)
    current_usage = models.JSONField(default=dict)
    last_reset = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ['api_key', 'endpoint_pattern', 'method']
        app_label = 'api'

    
    def __str__(self):
        key_name = self.api_key.name if self.api_key else "Global"
        return f"{key_name} - {self.method} {self.endpoint_pattern}"

class APIWebhook(models.Model):
    EVENT_TYPES = [
        ('user_registered', 'User Registered'),
        ('purchase_completed', 'Purchase Completed'),
        ('investment_matured', 'Investment Matured'),
        ('api_key_created', 'API Key Created'),
        ('transaction_failed', 'Transaction Failed'),
    ]
    
    name = models.CharField(max_length=100)
    url = models.URLField()
    secret = models.CharField(max_length=256, blank=True, help_text="Webhook secret for signature verification")
    event_type = models.CharField(max_length=50, choices=EVENT_TYPES)
    status = models.CharField(max_length=20, choices=[('active', 'Active'), ('inactive', 'Inactive')], default='active')
    retry_count = models.IntegerField(default=3, help_text="Number of retry attempts on failure")
    timeout_seconds = models.IntegerField(default=10)
    last_triggered = models.DateTimeField(null=True, blank=True)
    last_response = models.JSONField(null=True, blank=True)
    success_count = models.IntegerField(default=0)
    failure_count = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.name} - {self.event_type}"

    class Meta:
        app_label = 'api'

