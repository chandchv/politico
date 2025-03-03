from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import user_passes_test
from django.contrib import messages
from django.db.models import Count
from django.contrib.auth.hashers import make_password
from django.utils import timezone
from datetime import timedelta
from .models import (
    User, ClothingItem, CustomerMeasurement, ClothingMeasurements,
    SubscriptionPlan, UserSubscription, PlanCategory, PlanItem
)
from django.http import JsonResponse

def is_admin(user):
    return user.is_authenticated and user.is_staff

@user_passes_test(is_admin, login_url='login')
def subscription_plans(request):
    plans = SubscriptionPlan.objects.filter(is_active=True)
    context = {
        'plans': plans,
    }
    return render(request, 'admin_dashboard/subscription_plans.html', context)

@user_passes_test(is_admin, login_url='login')
def subscribe_plan(request, plan_type):
    if request.method == 'POST':
        try:
            customer_id = request.POST.get('customer')
            customer = User.objects.get(id=customer_id)
            plan = SubscriptionPlan.objects.get(plan_type=plan_type, is_active=True)
            
            # Calculate dates
            start_date = timezone.now().date()
            end_date = start_date + timedelta(days=365)  # 1 year subscription
            
            # Create subscription
            subscription = UserSubscription.objects.create(
                user=customer,
                plan=plan,
                start_date=start_date,
                end_date=end_date,
                amount_paid=plan.price,
                status='active'
            )
            
            # Set next assessment date based on plan type
            if plan_type == 'standard':
                subscription.next_assessment_date = start_date + timedelta(days=365)  # Annual
            elif plan_type == 'premium':
                subscription.next_assessment_date = start_date + timedelta(days=180)  # Biannual
            else:  # luxury
                subscription.next_assessment_date = start_date + timedelta(days=90)  # Quarterly
            
            subscription.save()
            
            messages.success(request, f'Successfully subscribed {customer.username} to {plan.name}!')
            return redirect('custom_admin_customers')
            
        except User.DoesNotExist:
            messages.error(request, 'Customer not found!')
        except SubscriptionPlan.DoesNotExist:
            messages.error(request, 'Invalid subscription plan!')
        except Exception as e:
            messages.error(request, f'Error creating subscription: {str(e)}')
        
        return redirect('subscription_plans')
    
    # GET request - show subscription form
    plan = get_object_or_404(SubscriptionPlan, plan_type=plan_type, is_active=True)
    customers = User.objects.filter(is_active=True).order_by('username')
    
    context = {
        'plan': plan,
        'customers': customers,
    }
    return render(request, 'admin_dashboard/subscribe_plan.html', context)

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
    return render(request, 'measurement/measurements.html', context)

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
                # Get non-numeric values separately
                fit_type = request.POST.get('fit_type')
                
                # Get numeric measurements
                measurements = {
                    'shirt_length': request.POST.get('shirt_length'),
                    'shoulder': request.POST.get('shoulder'),
                    'full_sleeve_length': request.POST.get('full_sleeve_length'),
                    'half_sleeve_length': request.POST.get('half_sleeve_length'),
                    'chest': request.POST.get('chest'),
                    'waist': request.POST.get('waist'),
                    'hip': request.POST.get('hip'),
                    'neck': request.POST.get('neck'),
                    'bicep': request.POST.get('bicep'),
                    'forearm': request.POST.get('forearm'),
                    'cuff': request.POST.get('cuff'),
                    'armhole': request.POST.get('armhole')
                }
                
                # Convert numeric values to float
                measurements = {k: float(v) for k, v in measurements.items() if v}
                
                # Add non-numeric values back
                if fit_type:
                    measurements['fit_type'] = fit_type
                    
            elif clothing_type == 'pants':
                # Get non-numeric values separately
                fit_type = request.POST.get('fit_type')
                
                # Get numeric measurements
                measurements = {
                    'length': request.POST.get('length'),
                    'waist': request.POST.get('waist'),
                    'hip': request.POST.get('hip'),
                    'thigh': request.POST.get('thigh'),
                    'knee': request.POST.get('knee'),
                    'ankle': request.POST.get('ankle'),
                    'crotch': request.POST.get('crotch')
                }
                
                # Convert numeric values to float
                measurements = {k: float(v) for k, v in measurements.items() if v}
                
                # Add non-numeric values back
                if fit_type:
                    measurements['fit_type'] = fit_type
            
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
    clothing_type_id = request.GET.get('clothing_type_id')
    clothing_type = None
    if clothing_type_id:
        clothing_type = get_object_or_404(ClothingMeasurements, id=clothing_type_id)
    
    context = {
        'customers': customers,
        'clothing_type': clothing_type,
    }
    return render(request, 'measurement/add_measurement.html', context)

@user_passes_test(is_admin, login_url='login')
def manage_plan_items(request, plan_type):
    plan = get_object_or_404(SubscriptionPlan, plan_type=plan_type)
    categories = PlanCategory.objects.all()
    
    if request.method == 'POST':
        action = request.POST.get('action')
        if action == 'add':
            try:
                category_id = request.POST.get('category')
                name = request.POST.get('name')
                quantity = int(request.POST.get('quantity'))
                description = request.POST.get('description', '')
                
                category = PlanCategory.objects.get(id=category_id)
                PlanItem.objects.create(
                    plan=plan,
                    category=category,
                    name=name,
                    quantity=quantity,
                    description=description,
                    specifications={'quantity': quantity}
                )
                messages.success(request, f'Added {quantity}x {name} to {plan.name}')
            except Exception as e:
                messages.error(request, f'Error adding item: {str(e)}')
        
        elif action == 'update':
            try:
                item_id = request.POST.get('item_id')
                quantity = int(request.POST.get('quantity'))
                item = PlanItem.objects.get(id=item_id)
                item.quantity = quantity
                item.specifications['quantity'] = quantity
                item.save()
                messages.success(request, f'Updated quantity for {item.name}')
            except Exception as e:
                messages.error(request, f'Error updating item: {str(e)}')
        
        elif action == 'delete':
            try:
                item_id = request.POST.get('item_id')
                item = PlanItem.objects.get(id=item_id)
                item_name = item.name
                item.delete()
                messages.success(request, f'Removed {item_name} from {plan.name}')
            except Exception as e:
                messages.error(request, f'Error removing item: {str(e)}')
        
        return redirect('manage_plan_items', plan_type=plan_type)
    
    # Group items by category
    items_by_category = {}
    for category in categories:
        items_by_category[category] = PlanItem.objects.filter(
            plan=plan,
            category=category
        ).order_by('name')
    
    context = {
        'plan': plan,
        'categories': categories,
        'items_by_category': items_by_category,
    }
    return render(request, 'admin_dashboard/manage_plan_items.html', context)

@user_passes_test(is_admin, login_url='login')
def get_customer_measurements(request, customer_id):
    try:
        measurements = CustomerMeasurement.objects.filter(
            user_id=customer_id
        ).select_related('clothing_type')
        
        data = {}
        for measurement in measurements:
            data[measurement.clothing_type.clothing_type] = {
                'measurements': measurement.measurements,
                'notes': measurement.notes
            }
        
        return JsonResponse(data)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400) 