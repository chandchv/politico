from django.shortcuts import render, redirect
from django.contrib.auth.decorators import user_passes_test
from django.contrib import messages
from django.db.models import Count
from django.contrib.auth.hashers import make_password
from .models import User, ClothingItem, CustomerMeasurement, ClothingMeasurements

def is_admin(user):
    return user.is_authenticated and user.is_staff

@user_passes_test(is_admin, login_url='login')
def custom_admin_dashboard(request):
    # Get statistics
    total_customers = User.objects.count()
    total_clothing_items = ClothingItem.objects.count()
    total_measurements = CustomerMeasurement.objects.count()
    low_stock_threshold = 10
    low_stock_items = ClothingItem.objects.filter(stock__lt=low_stock_threshold).count()
    
    # Get recent customers
    recent_customers = User.objects.order_by('-date_joined')[:5]
    
    # Get low stock items
    low_stock_items_list = ClothingItem.objects.filter(
        stock__lt=low_stock_threshold
    ).order_by('stock')[:5]
    
    context = {
        'total_customers': total_customers,
        'total_clothing_items': total_clothing_items,
        'total_measurements': total_measurements,
        'low_stock_items': low_stock_items,
        'recent_customers': recent_customers,
        'low_stock_items_list': low_stock_items_list,
    }
    return render(request, 'admin_dashboard/dashboard.html', context)

@user_passes_test(is_admin, login_url='login')
def custom_admin_customers(request):
    customers = User.objects.annotate(
        measurement_count=Count('customer_measurements')
    ).order_by('-date_joined')
    
    context = {
        'customers': customers,
    }
    return render(request, 'admin_dashboard/customers.html', context)

@user_passes_test(is_admin, login_url='login')
def add_customer(request):
    if request.method == 'POST':
        try:
            # Get form data
            username = request.POST.get('username')
            email = request.POST.get('email')
            password = request.POST.get('password1')
            first_name = request.POST.get('first_name')
            last_name = request.POST.get('last_name')
            phone = request.POST.get('phone')
            shipping_address = request.POST.get('shipping_address')
            billing_address = request.POST.get('billing_address')
            same_as_shipping = request.POST.get('same_as_shipping')
            preferences = request.POST.get('preferences')
            email_notifications = request.POST.get('email_notifications') == 'on'
            sms_notifications = request.POST.get('sms_notifications') == 'on'

            # Use shipping address for billing if checkbox is checked
            if same_as_shipping:
                billing_address = shipping_address

            # Create user
            user = User.objects.create(
                username=username,
                email=email,
                password=make_password(password),
                first_name=first_name,
                last_name=last_name,
                phone=phone,
                shipping_address=shipping_address,
                billing_address=billing_address,
                preferences=preferences,
                email_notifications=email_notifications,
                sms_notifications=sms_notifications,
                is_active=True
            )

            messages.success(request, f'Customer {username} created successfully!')
            return redirect('custom_admin_customers')

        except Exception as e:
            messages.error(request, f'Error creating customer: {str(e)}')
            return redirect('add_customer')

    return render(request, 'admin_dashboard/add_customer.html')

@user_passes_test(is_admin, login_url='login')
def custom_admin_clothing(request):
    clothing_items = ClothingItem.objects.all().order_by('category', 'name')
    
    context = {
        'clothing_items': clothing_items,
    }
    return render(request, 'admin_dashboard/clothing.html', context)

@user_passes_test(is_admin, login_url='login')
def custom_admin_measurements(request):
    measurements = CustomerMeasurement.objects.select_related(
        'user', 'clothing_type'
    ).order_by('-last_updated')
    
    context = {
        'measurements': measurements,
    }
    return render(request, 'admin_dashboard/measurements.html', context)

@user_passes_test(is_admin, login_url='login')
def add_measurement(request):
    if request.method == 'POST':
        customer_id = request.POST.get('customer')
        clothing_type = request.POST.get('clothing_type')
        notes = request.POST.get('notes')
        
        try:
            customer = User.objects.get(id=customer_id)
            
            # Get or create clothing type template
            clothing_type_obj, _ = ClothingMeasurements.objects.get_or_create(
                clothing_type=clothing_type
            )
            
            # Prepare measurements dictionary based on clothing type
            measurements = {}
            if clothing_type == 'shirt':
                measurements = {
                    'shirt_length': request.POST.get('shirt_length'),
                    'shoulder': request.POST.get('shoulder'),
                    'sleeve_length': request.POST.get('sleeve_length'),
                    'sleeve_type': request.POST.get('sleeve_type'),
                    'chest': request.POST.get('chest'),
                    'waist': request.POST.get('waist'),
                    'hip': request.POST.get('hip'),
                    'neck': request.POST.get('neck'),
                    'bicep': request.POST.get('bicep'),
                    'forearm': request.POST.get('forearm'),
                    'cuff': request.POST.get('cuff'),
                    'armhole': request.POST.get('armhole'),
                    'fit_type': request.POST.get('fit_type')
                }
            elif clothing_type == 'pants':
                measurements = {
                    'length': request.POST.get('length'),
                    'waist': request.POST.get('waist'),
                    'hip': request.POST.get('hip'),
                    'thigh': request.POST.get('thigh'),
                    'knee': request.POST.get('knee'),
                    'ankle': request.POST.get('ankle'),
                    'crotch': request.POST.get('crotch')
                }
            
            # Remove empty values
            measurements = {k: float(v) for k, v in measurements.items() if v}
            
            # Create or update measurement
            CustomerMeasurement.objects.update_or_create(
                user=customer,
                clothing_type=clothing_type_obj,
                defaults={
                    'measurements': measurements,
                    'notes': notes,
                    'measured_by': request.user
                }
            )
            
            messages.success(request, 'Measurements saved successfully!')
            return redirect('custom_admin_measurements')
            
        except User.DoesNotExist:
            messages.error(request, 'Customer not found!')
        except ValueError as e:
            messages.error(request, f'Invalid measurement value: {str(e)}')
        except Exception as e:
            messages.error(request, f'Error saving measurements: {str(e)}')
        
        return redirect('add_measurement')
    
    # GET request
    customers = User.objects.all().order_by('username')
    context = {
        'customers': customers,
    }
    return render(request, 'admin_dashboard/add_measurement.html', context) 