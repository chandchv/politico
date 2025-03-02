print("Loading models.py")
from django.db import models
from django.contrib.auth.models import AbstractUser

print("Defining User model")
class User(AbstractUser):
    print("Setting up User model fields")
    phone = models.CharField(max_length=15, unique=True)
    address = models.TextField()
    preferences = models.TextField(blank=True, null=True)  # Style preferences
    measurements = models.JSONField(default=dict)  # Store measurements in JSON format
    stylist = models.ForeignKey('Stylist', on_delete=models.SET_NULL, null=True, blank=True, related_name='client_users')
    
    # Add style quiz responses
    style_quiz_completed = models.BooleanField(default=False)
    style_preferences = models.JSONField(default=dict)  # Store detailed style quiz responses
    
    # Add more detailed address fields
    shipping_address = models.TextField()
    billing_address = models.TextField(blank=True, null=True)
    
    # Add notification preferences
    email_notifications = models.BooleanField(default=True)
    sms_notifications = models.BooleanField(default=True)

class SubscriptionPlan(models.Model):
    name = models.CharField(max_length=50)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    features = models.TextField()
    clothing_items = models.ManyToManyField('ClothingItem', blank=True)
    is_organic = models.BooleanField(default=False)
    
    PLAN_CHOICES = [
        ('basic', '₹3L Annual Plan'),
        ('premium', '₹5L Annual Plan'),
        ('luxury', '₹7L Annual Plan'),
    ]
    plan_type = models.CharField(max_length=20, choices=PLAN_CHOICES)
    delivery_frequency = models.IntegerField(help_text='Delivery frequency in days')
    items_per_delivery = models.IntegerField()

class Subscription(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    plan = models.ForeignKey(SubscriptionPlan, on_delete=models.SET_NULL, null=True)
    start_date = models.DateField(auto_now_add=True)
    renewal_date = models.DateField()

class ClothingItem(models.Model):
    CATEGORY_CHOICES = [
        ('shirt', 'Shirt'), ('trousers', 'Trousers'), ('casual', 'Casual Wear'),
        ('ethnic', 'Ethnic Wear'), ('beachwear', 'Beachwear'), ('accessory', 'Accessory'),
        ('sleepwear', 'Sleepwear')
    ]
    name = models.CharField(max_length=100)
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES)
    fabric = models.CharField(max_length=50)
    is_organic = models.BooleanField(default=False)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    
    # Add more detailed product information
    description = models.TextField()
    size_available = models.JSONField(default=list)  # List of available sizes
    color = models.CharField(max_length=50)
    brand = models.CharField(max_length=100)
    season = models.CharField(max_length=20, choices=[
        ('summer', 'Summer'),
        ('winter', 'Winter'),
        ('all', 'All Season')
    ])
    stock = models.IntegerField(default=0)
    image = models.ImageField(upload_to='clothing_items/', null=True, blank=True)

class Stylist(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="stylist_profile")
    experience = models.IntegerField()
    assigned_clients = models.ManyToManyField(User, related_name="assigned_stylists")
    
    specialization = models.CharField(max_length=100)
    bio = models.TextField()
    availability = models.BooleanField(default=True)
    rating = models.DecimalField(max_digits=3, decimal_places=2, default=5.00)
    profile_image = models.ImageField(upload_to='stylist_profiles/', null=True, blank=True)

class Order(models.Model):
    subscription = models.ForeignKey(Subscription, on_delete=models.CASCADE)
    clothing_items = models.ManyToManyField(ClothingItem)
    delivery_address = models.TextField()
    tracking_number = models.CharField(max_length=100, null=True, blank=True)
    estimated_delivery = models.DateField(null=True)
    feedback = models.TextField(null=True, blank=True)
    rating = models.IntegerField(null=True, blank=True)
    
    # Add more detailed status choices
    STATUS_CHOICES = [
        ('processing', 'Processing'),
        ('styling', 'Styling in Progress'),
        ('confirmed', 'Confirmed'),
        ('packed', 'Packed'),
        ('shipped', 'Shipped'),
        ('delivered', 'Delivered'),
        ('returned', 'Returned')
    ]
    status = models.CharField(max_length=20, choices=STATUS_CHOICES)
    order_date = models.DateField(auto_now_add=True)

class Payment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    payment_status = models.CharField(max_length=20, choices=[('pending', 'Pending'), ('completed', 'Completed')])
    transaction_id = models.CharField(max_length=100, unique=True)

# New model for style feedback
class StyleFeedback(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    clothing_item = models.ForeignKey(ClothingItem, on_delete=models.CASCADE)
    feedback = models.TextField()
    rating = models.IntegerField(choices=[(i, i) for i in range(1, 6)])
    created_at = models.DateTimeField(auto_now_add=True)

# New model for size measurements
class UserMeasurements(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    measurements = models.JSONField(default=dict)  # Detailed body measurements
    last_updated = models.DateTimeField(auto_now=True)
    notes = models.TextField(blank=True, null=True)

class ClothingMeasurements(models.Model):
    CLOTHING_TYPE_CHOICES = [
        ('shirt', 'Shirt'),
        ('pants', 'Pants'),
        ('suit', 'Suit'),
        ('kurta', 'Kurta'),
        ('blazer', 'Blazer'),
        ('sherwani', 'Sherwani'),
    ]
    
    clothing_type = models.CharField(max_length=20, choices=CLOTHING_TYPE_CHOICES)
    measurement_fields = models.JSONField(
        default=dict,
        help_text='Dictionary of required measurements for this clothing type'
    )
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ['clothing_type']

    def __str__(self):
        return f"{self.clothing_type} Measurements Template"

class CustomerMeasurement(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='customer_measurements')
    clothing_type = models.ForeignKey(ClothingMeasurements, on_delete=models.CASCADE)
    measurements = models.JSONField(default=dict)
    notes = models.TextField(blank=True)
    last_updated = models.DateTimeField(auto_now=True)
    measured_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='measurements_taken')

    class Meta:
        unique_together = ['user', 'clothing_type']

    def __str__(self):
        return f"{self.user.username}'s {self.clothing_type.clothing_type} Measurements"

print("Models loaded successfully")
