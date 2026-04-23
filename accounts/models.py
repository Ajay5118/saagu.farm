import random
import string
from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.utils import timezone
from django.conf import settings


class UserManager(BaseUserManager):
    """Custom manager for phone-based User model."""

    def create_user(self, phone, password=None, **extra_fields):
        if not phone:
            raise ValueError('Phone number is required')
        user = self.model(phone=phone, **extra_fields)
        if password:
            user.set_password(password)
        else:
            user.set_unusable_password()
        user.save(using=self._db)
        return user

    def create_superuser(self, phone, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)
        return self.create_user(phone, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    """Custom user — phone number is the primary identifier."""
    phone = models.CharField(max_length=15, unique=True, db_index=True)
    name = models.CharField(max_length=150, blank=True)
    email = models.EmailField(blank=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    date_joined = models.DateTimeField(default=timezone.now)

    objects = UserManager()

    USERNAME_FIELD = 'phone'
    REQUIRED_FIELDS = []

    class Meta:
        verbose_name = 'Customer'
        verbose_name_plural = 'Customers'

    def __str__(self):
        return self.name or self.phone

    def get_display_name(self):
        return self.name or self.phone


class OTP(models.Model):
    """Store OTPs for phone verification."""
    phone = models.CharField(max_length=15, db_index=True)
    code = models.CharField(max_length=6)
    created_at = models.DateTimeField(auto_now_add=True)
    is_used = models.BooleanField(default=False)
    attempts = models.IntegerField(default=0)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"OTP for {self.phone}"

    @classmethod
    def generate(cls, phone):
        """Generate a new OTP for the given phone number."""
        # Invalidate old OTPs
        cls.objects.filter(phone=phone, is_used=False).update(is_used=True)
        # Create new
        code = ''.join(random.choices(string.digits, k=getattr(settings, 'OTP_LENGTH', 6)))
        return cls.objects.create(phone=phone, code=code)

    def is_valid(self):
        """Check if OTP is still valid (not expired, not used, attempts < 3)."""
        if self.is_used:
            return False
        if self.attempts >= 3:
            return False
        expiry = getattr(settings, 'OTP_EXPIRY_MINUTES', 5)
        return timezone.now() < self.created_at + timezone.timedelta(minutes=expiry)

    def verify(self, code):
        """Verify the OTP code. Returns True if correct."""
        self.attempts += 1
        self.save(update_fields=['attempts'])
        if self.is_valid() and self.code == code:
            self.is_used = True
            self.save(update_fields=['is_used'])
            return True
        return False


class Address(models.Model):
    """Saved delivery addresses for a user."""
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='addresses')
    label = models.CharField(max_length=50, default='Home')  # Home, Office, etc.
    name = models.CharField(max_length=150)
    phone = models.CharField(max_length=15)
    address_line1 = models.CharField(max_length=255)
    address_line2 = models.CharField(max_length=255, blank=True)
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100, default='Telangana')
    pincode = models.CharField(max_length=10)
    is_default = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = 'Addresses'
        ordering = ['-is_default', '-created_at']

    def __str__(self):
        return f"{self.label} - {self.name}, {self.city}"

    def save(self, *args, **kwargs):
        # Ensure only one default address per user
        if self.is_default:
            Address.objects.filter(user=self.user, is_default=True).update(is_default=False)
        super().save(*args, **kwargs)
