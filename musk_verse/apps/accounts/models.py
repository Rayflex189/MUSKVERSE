from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models
from django.utils import timezone
import random
import string

from cloudinary.models import CloudinaryField

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    full_name = models.CharField(max_length=150)
    profile_image = CloudinaryField('image', blank=True, null=True)
    phone = models.CharField(max_length=20)
    address = models.TextField()
    country = models.CharField(max_length=100)
    currency = models.CharField(max_length=10)
    date_of_birth = models.DateField()

    def __str__(self):
        return self.full_name

def generate_otp():
    return ''.join(random.choices(string.digits, k=6))

class UserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('Email is required')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_verified', True)
        return self.create_user(email, password, **extra_fields)

class User(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(unique=True)
    is_verified = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    date_joined = models.DateTimeField(default=timezone.now)

    otp_code = models.CharField(max_length=6, blank=True, null=True)
    otp_created_at = models.DateTimeField(blank=True, null=True)

    objects = UserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    def __str__(self):
        return self.email

    def set_otp(self):
        self.otp_code = generate_otp()
        self.otp_created_at = timezone.now()
        self.save(update_fields=['otp_code', 'otp_created_at'])
        return self.otp_code

    def verify_otp(self, code):
        if self.otp_code == code and self.otp_created_at:
            expiry_minutes = 10
            if (timezone.now() - self.otp_created_at).total_seconds() <= expiry_minutes * 60:
                self.is_verified = True
                self.otp_code = None
                self.save(update_fields=['is_verified', 'otp_code'])
                return True
        return False
