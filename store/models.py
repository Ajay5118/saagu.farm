import uuid
from django.db import models
from django.conf import settings


class Product(models.Model):
    """A product like Chilli Powder, Veg Pickle, etc."""
    CATEGORY_CHOICES = [
        ('spice', 'Spice'),
        ('pickle_veg', 'Veg Pickle'),
        ('pickle_nv', 'Non-Veg Pickle'),
    ]

    name = models.CharField(max_length=200)
    slug = models.SlugField(unique=True)
    description = models.TextField(blank=True)
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES)
    image = models.ImageField(upload_to='products/', blank=True)
    badge = models.CharField(max_length=50, blank=True, help_text='e.g. PURE VEG, Non-Veg')
    is_available = models.BooleanField(default=True)
    is_featured = models.BooleanField(default=False)
    sort_order = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['sort_order', 'name']

    def __str__(self):
        return self.name

    def get_variants(self):
        return self.variants.filter(is_available=True)

    def get_default_variant(self):
        return self.variants.filter(is_available=True).first()


class ProductVariant(models.Model):
    """Weight/size variants for a product (250g, 500g, etc.)"""
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='variants')
    weight = models.CharField(max_length=20, help_text='e.g. 250g, 500g, 1kg')
    weight_grams = models.IntegerField(help_text='Weight in grams for sorting')
    price = models.DecimalField(max_digits=8, decimal_places=2)
    mrp = models.DecimalField(max_digits=8, decimal_places=2, help_text='Maximum Retail Price')
    stock = models.IntegerField(default=100)
    is_available = models.BooleanField(default=True)

    class Meta:
        ordering = ['weight_grams']
        unique_together = ['product', 'weight']

    def __str__(self):
        return f"{self.product.name} — {self.weight} @ ₹{self.price}"

    @property
    def discount_percent(self):
        if self.mrp > self.price:
            return int(((self.mrp - self.price) / self.mrp) * 100)
        return 0


class Order(models.Model):
    """Customer order."""
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('confirmed', 'Confirmed'),
        ('processing', 'Processing'),
        ('shipped', 'Shipped'),
        ('delivered', 'Delivered'),
        ('cancelled', 'Cancelled'),
    ]

    order_id = models.CharField(max_length=20, unique=True, editable=False)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name='orders')
    address = models.ForeignKey('accounts.Address', on_delete=models.SET_NULL, null=True, blank=True)

    # Snapshot address at time of order (in case address is later changed)
    delivery_name = models.CharField(max_length=150)
    delivery_phone = models.CharField(max_length=15)
    delivery_address = models.TextField()
    delivery_pincode = models.CharField(max_length=10)

    subtotal = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    delivery_charge = models.DecimalField(max_digits=6, decimal_places=2, default=0)
    total = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    PAYMENT_CHOICES = [
        ('cod',      'Cash on Delivery'),
        ('razorpay', 'Online Payment'),
    ]
    payment_method     = models.CharField(max_length=20, choices=PAYMENT_CHOICES, default='cod')
    razorpay_order_id  = models.CharField(max_length=100, blank=True)
    razorpay_payment_id = models.CharField(max_length=100, blank=True)

    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    notes = models.TextField(blank=True, help_text='Customer notes or special instructions')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Order #{self.order_id}"

    def save(self, *args, **kwargs):
        if not self.order_id:
            # Generate order ID: SF-YYYYMMDD-XXXX
            from django.utils import timezone
            import random
            today = timezone.now().strftime('%Y%m%d')
            rand = ''.join([str(random.randint(0, 9)) for _ in range(4)])
            self.order_id = f"SF-{today}-{rand}"
        super().save(*args, **kwargs)

    def get_items_count(self):
        return self.items.aggregate(total=models.Sum('quantity'))['total'] or 0


class OrderItem(models.Model):
    """Individual line item in an order."""
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True)
    variant = models.ForeignKey(ProductVariant, on_delete=models.SET_NULL, null=True)

    # Snapshot at time of purchase
    product_name = models.CharField(max_length=200)
    weight = models.CharField(max_length=20)
    price = models.DecimalField(max_digits=8, decimal_places=2)
    quantity = models.IntegerField(default=1)
    line_total = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.product_name} ({self.weight}) x{self.quantity}"

    def save(self, *args, **kwargs):
        self.line_total = self.price * self.quantity
        super().save(*args, **kwargs)
