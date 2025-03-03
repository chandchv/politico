print("Loading models.py")
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone

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
    PLAN_CHOICES = [
        ('standard', '₹3L Annual Plan'),
        ('premium', '₹5L Annual Plan'),
        ('luxury', '₹7L Annual Plan'),
    ]

    name = models.CharField(max_length=50, null=True, blank=True)
    plan_type = models.CharField(max_length=20, choices=PLAN_CHOICES, null=True, blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    description = models.TextField(null=True, blank=True)
    best_for = models.TextField(null=True, blank=True)
    features = models.JSONField(default=dict, null=True, blank=True)  # Store detailed features
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True, null=True, blank=True)

    def __str__(self):
        return f"{self.get_plan_type_display()} - {self.name}"

class PlanCategory(models.Model):
    CATEGORY_CHOICES = [
        ('formal', 'Formal & Business Wear'),
        ('casual', 'Casual & Seasonal Wear'),
        ('ethnic', 'Ethnic & Occasion Wear'),
        ('accessories', 'Accessories & Footwear'),
        ('sleepwear', 'Sleepwear & Undergarments'),
    ]

    name = models.CharField(max_length=50)
    category_type = models.CharField(max_length=20, choices=CATEGORY_CHOICES)
    description = models.TextField(blank=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = "Plan Categories"

class PlanItem(models.Model):
    plan = models.ForeignKey(SubscriptionPlan, on_delete=models.CASCADE, related_name='items')
    category = models.ForeignKey(PlanCategory, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    quantity = models.IntegerField()
    description = models.TextField(blank=True)
    specifications = models.JSONField(default=dict)  # Store detailed specifications

    def __str__(self):
        return f"{self.quantity} x {self.name} ({self.plan.name})"

class UserSubscription(models.Model):
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('pending', 'Pending'),
        ('expired', 'Expired'),
        ('cancelled', 'Cancelled'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='subscriptions')
    plan = models.ForeignKey(SubscriptionPlan, on_delete=models.PROTECT)
    start_date = models.DateField()
    end_date = models.DateField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    amount_paid = models.DecimalField(max_digits=10, decimal_places=2)
    payment_date = models.DateTimeField(auto_now_add=True)
    last_assessment_date = models.DateField(null=True, blank=True)
    next_assessment_date = models.DateField(null=True, blank=True)
    stylist_notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.username}'s {self.plan.name} Subscription"

class DeliverySchedule(models.Model):
    STATUS_CHOICES = [
        ('scheduled', 'Scheduled'),
        ('processing', 'Processing'),
        ('shipped', 'Shipped'),
        ('delivered', 'Delivered'),
        ('cancelled', 'Cancelled'),
    ]

    subscription = models.ForeignKey(UserSubscription, on_delete=models.CASCADE, related_name='deliveries')
    scheduled_date = models.DateField()
    actual_delivery_date = models.DateField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='scheduled')
    items = models.JSONField(default=list)  # Store list of items to be delivered
    delivery_notes = models.TextField(blank=True)
    tracking_number = models.CharField(max_length=100, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Delivery for {self.subscription.user.username} on {self.scheduled_date}"

class StylistAppointment(models.Model):
    STATUS_CHOICES = [
        ('scheduled', 'Scheduled'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ]

    subscription = models.ForeignKey(UserSubscription, on_delete=models.CASCADE, related_name='appointments')
    appointment_date = models.DateTimeField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='scheduled')
    notes = models.TextField(blank=True)
    recommendations = models.JSONField(default=list)  # Store stylist recommendations
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Styling appointment for {self.subscription.user.username} on {self.appointment_date}"

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

class Appointment(models.Model):
    STAGE_CHOICES = [
        ('measurement', 'Initial Measurement'),
        ('trial_fit', 'Trial Fitting'),
        ('final_fit', 'Final Fitting'),
        ('delivery', 'Delivery'),
    ]

    STATUS_CHOICES = [
        ('scheduled', 'Scheduled'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
        ('rescheduled', 'Rescheduled'),
    ]

    customer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='appointments', null=True, blank=True)
    stage = models.CharField(max_length=20, choices=STAGE_CHOICES)
    date_time = models.DateTimeField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='scheduled')
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='created_appointments')

    def __str__(self):
        return f"{self.customer.get_full_name()} - {self.get_stage_display()} - {self.date_time}"

    class Meta:
        ordering = ['-date_time']

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

class Order(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('in_progress', 'In Progress'),
        ('ready', 'Ready for Delivery'),
        ('delivered', 'Delivered'),
        ('cancelled', 'Cancelled'),
    ]

    customer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='orders', null=True, blank=True)
    order_date = models.DateTimeField(auto_now_add=True)
    delivery_date = models.DateTimeField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    notes = models.TextField(blank=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='created_orders')

    def __str__(self):
        return f"Order #{self.id} - {self.customer.get_full_name()}"

    @property
    def amount_paid(self):
        return sum(payment.amount for payment in self.payments.all())

    @property
    def balance_due(self):
        return self.total_amount - self.amount_paid

class OrderItem(models.Model):
    order = models.ForeignKey('Order', on_delete=models.CASCADE, related_name='items')
    clothing_item = models.ForeignKey('ClothingItem', on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    measurement = models.ForeignKey('CustomerMeasurement', on_delete=models.SET_NULL, null=True)
    notes = models.TextField(blank=True)

    def __str__(self):
        return f"{self.clothing_item.name} x {self.quantity}"

    @property
    def total_price(self):
        return self.quantity * self.price

class Payment(models.Model):
    PAYMENT_TYPE_CHOICES = [
        ('advance', 'Advance Payment'),
        ('partial', 'Partial Payment'),
        ('final', 'Final Payment'),
    ]

    PAYMENT_METHOD_CHOICES = [
        ('cash', 'Cash'),
        ('card', 'Card'),
        ('upi', 'UPI'),
        ('bank_transfer', 'Bank Transfer'),
    ]

    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='payments', null=True, blank=True)
    payment_type = models.CharField(max_length=20, choices=PAYMENT_TYPE_CHOICES, null=True, blank=True)
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHOD_CHOICES, null=True, blank=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    payment_date = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    transaction_id = models.CharField(max_length=100, blank=True, null=True)
    notes = models.TextField(blank=True, null=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return f"{self.get_payment_type_display()} - {self.amount}"

    class Meta:
        ordering = ['-payment_date']

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

print("Models loaded successfully")
