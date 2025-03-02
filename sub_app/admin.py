from django.contrib import admin
from django.utils.html import format_html
from .models import (
    User, ClothingItem, ClothingMeasurements,
    CustomerMeasurement, UserMeasurements
)

@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('username', 'email', 'phone', 'style_quiz_completed', 'get_measurements_status')
    list_filter = ('style_quiz_completed', 'email_notifications', 'sms_notifications')
    search_fields = ('username', 'email', 'phone')
    fieldsets = (
        ('Personal Info', {
            'fields': ('username', 'email', 'phone', 'first_name', 'last_name')
        }),
        ('Address Information', {
            'fields': ('address', 'shipping_address', 'billing_address')
        }),
        ('Style Preferences', {
            'fields': ('style_quiz_completed', 'style_preferences', 'preferences')
        }),
        ('Notification Settings', {
            'fields': ('email_notifications', 'sms_notifications')
        }),
    )

    def get_measurements_status(self, obj):
        measurements = CustomerMeasurement.objects.filter(user=obj).count()
        return f"{measurements} measurements recorded"
    get_measurements_status.short_description = 'Measurements Status'

@admin.register(ClothingItem)
class ClothingItemAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'brand', 'price', 'stock', 'is_organic', 'get_image_preview')
    list_filter = ('category', 'brand', 'is_organic', 'season')
    search_fields = ('name', 'brand', 'description')
    list_editable = ('stock', 'price')
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'category', 'brand', 'description')
        }),
        ('Product Details', {
            'fields': ('fabric', 'is_organic', 'price', 'stock', 'color', 'season')
        }),
        ('Size and Image', {
            'fields': ('size_available', 'image')
        }),
    )

    def get_image_preview(self, obj):
        if obj.image:
            return format_html('<img src="{}" style="max-height: 50px;"/>', obj.image.url)
        return "No image"
    get_image_preview.short_description = 'Image Preview'

@admin.register(ClothingMeasurements)
class ClothingMeasurementsAdmin(admin.ModelAdmin):
    list_display = ('clothing_type', 'get_measurement_fields_display', 'created_at')
    search_fields = ('clothing_type', 'description')
    readonly_fields = ('created_at', 'updated_at')

    def get_measurement_fields_display(self, obj):
        return ", ".join(obj.measurement_fields.keys())
    get_measurement_fields_display.short_description = 'Required Measurements'

@admin.register(CustomerMeasurement)
class CustomerMeasurementAdmin(admin.ModelAdmin):
    list_display = ('user', 'clothing_type', 'last_updated', 'measured_by')
    list_filter = ('clothing_type', 'last_updated')
    search_fields = ('user__username', 'user__email', 'notes')
    raw_id_fields = ('user', 'measured_by')
    readonly_fields = ('last_updated',)
    fieldsets = (
        ('Customer Information', {
            'fields': ('user', 'clothing_type')
        }),
        ('Measurement Details', {
            'fields': ('measurements', 'notes', 'measured_by')
        }),
        ('Timestamp', {
            'fields': ('last_updated',)
        }),
    )

@admin.register(UserMeasurements)
class UserMeasurementsAdmin(admin.ModelAdmin):
    list_display = ('user', 'last_updated')
    search_fields = ('user__username', 'user__email', 'notes')
    raw_id_fields = ('user',)
    readonly_fields = ('last_updated',)
    fieldsets = (
        ('User Information', {
            'fields': ('user',)
        }),
        ('Measurements', {
            'fields': ('measurements', 'notes')
        }),
        ('Timestamp', {
            'fields': ('last_updated',)
        }),
    ) 