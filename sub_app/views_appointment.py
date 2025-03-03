from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.utils import timezone
from django.http import JsonResponse
from django.db.models import Sum, Q
from .models import Appointment, Order, OrderItem, Payment, User
from datetime import datetime, timedelta

def is_staff_or_admin(user):
    return user.is_authenticated and (user.is_staff or user.is_superuser)

@login_required
def book_appointment(request):
    if request.method == 'POST':
        try:
            customer_id = request.POST.get('customer')
            stage = request.POST.get('stage')
            date = request.POST.get('date')
            time = request.POST.get('time')
            notes = request.POST.get('notes', '')

            # Combine date and time
            date_time = datetime.strptime(f"{date} {time}", "%Y-%m-%d %H:%M")

            # Check if slot is available
            if Appointment.objects.filter(date_time=date_time).exists():
                messages.error(request, 'This time slot is already booked. Please choose another time.')
                return redirect('book_appointment')

            customer = User.objects.get(id=customer_id)
            
            # Create appointment
            appointment = Appointment.objects.create(
                customer=customer,
                stage=stage,
                date_time=date_time,
                notes=notes,
                created_by=request.user
            )

            messages.success(request, f'Appointment scheduled for {appointment.get_stage_display()} on {date_time}')
            return redirect('appointment_list')

        except Exception as e:
            messages.error(request, f'Error scheduling appointment: {str(e)}')
            return redirect('book_appointment')

    # GET request
    context = {
        'customers': User.objects.filter(is_active=True).order_by('username'),
        'stages': Appointment.STAGE_CHOICES,
        'min_date': timezone.now().date(),
        'max_date': timezone.now().date() + timedelta(days=30),  # Allow booking up to 30 days in advance
    }
    return render(request, 'appointments/book_appointment.html', context)

@login_required
def appointment_list(request):
    # Staff can see all appointments, customers can only see their own
    if request.user.is_staff:
        appointments = Appointment.objects.all()
    else:
        appointments = Appointment.objects.filter(customer=request.user)

    # Filter by date range if provided
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')
    if start_date and end_date:
        appointments = appointments.filter(
            date_time__date__range=[start_date, end_date]
        )

    # Filter by status if provided
    status = request.GET.get('status')
    if status:
        appointments = appointments.filter(status=status)

    context = {
        'appointments': appointments,
        'statuses': Appointment.STATUS_CHOICES,
    }
    return render(request, 'appointments/appointment_list.html', context)

@user_passes_test(is_staff_or_admin)
def manage_order(request, order_id=None):
    if request.method == 'POST':
        try:
            customer_id = request.POST.get('customer')
            items = request.POST.getlist('items[]')
            quantities = request.POST.getlist('quantities[]')
            prices = request.POST.getlist('prices[]')
            measurements = request.POST.getlist('measurements[]')
            
            # Calculate total amount
            total_amount = sum(float(p) * int(q) for p, q in zip(prices, quantities))
            
            # Create or update order
            if order_id:
                order = Order.objects.get(id=order_id)
                order.total_amount = total_amount
                order.save()
                order.items.all().delete()  # Remove existing items
            else:
                order = Order.objects.create(
                    customer_id=customer_id,
                    total_amount=total_amount,
                    created_by=request.user
                )

            # Add items to order
            for item, qty, price, measurement in zip(items, quantities, prices, measurements):
                OrderItem.objects.create(
                    order=order,
                    clothing_item_id=item,
                    quantity=qty,
                    price=price,
                    measurement_id=measurement if measurement else None
                )

            messages.success(request, 'Order saved successfully!')
            return redirect('order_list')

        except Exception as e:
            messages.error(request, f'Error saving order: {str(e)}')
            return redirect('manage_order')

    # GET request
    order = None
    if order_id:
        order = get_object_or_404(Order, id=order_id)

    context = {
        'order': order,
        'customers': User.objects.filter(is_active=True),
        'clothing_items': ClothingItem.objects.all(),
    }
    return render(request, 'orders/manage_order.html', context)

@login_required
def order_list(request):
    # Staff can see all orders, customers can only see their own
    if request.user.is_staff:
        orders = Order.objects.all()
    else:
        orders = Order.objects.filter(customer=request.user)

    # Filter by status if provided
    status = request.GET.get('status')
    if status:
        orders = orders.filter(status=status)

    context = {
        'orders': orders,
        'statuses': Order.STATUS_CHOICES,
    }
    return render(request, 'orders/order_list.html', context)

@user_passes_test(is_staff_or_admin)
def record_payment(request, order_id):
    if request.method == 'POST':
        try:
            order = Order.objects.get(id=order_id)
            payment_type = request.POST.get('payment_type')
            payment_method = request.POST.get('payment_method')
            amount = float(request.POST.get('amount'))
            transaction_id = request.POST.get('transaction_id', '')
            notes = request.POST.get('notes', '')

            # Validate payment amount
            if amount > order.balance_due:
                messages.error(request, 'Payment amount cannot exceed balance due.')
                return redirect('record_payment', order_id=order_id)

            # Create payment
            Payment.objects.create(
                order=order,
                payment_type=payment_type,
                payment_method=payment_method,
                amount=amount,
                transaction_id=transaction_id,
                notes=notes,
                created_by=request.user
            )

            # Update order status if fully paid
            if order.balance_due == 0:
                order.status = 'ready'
                order.save()

            messages.success(request, f'Payment of {amount} recorded successfully!')
            return redirect('order_list')

        except Exception as e:
            messages.error(request, f'Error recording payment: {str(e)}')
            return redirect('record_payment', order_id=order_id)

    # GET request
    order = get_object_or_404(Order, id=order_id)
    context = {
        'order': order,
        'payment_types': Payment.PAYMENT_TYPE_CHOICES,
        'payment_methods': Payment.PAYMENT_METHOD_CHOICES,
    }
    return render(request, 'orders/record_payment.html', context)

@login_required
def get_available_slots(request):
    date = request.GET.get('date')
    if not date:
        return JsonResponse({'error': 'Date is required'}, status=400)

    # Get all appointments for the selected date
    date_obj = datetime.strptime(date, '%Y-%m-%d').date()
    booked_slots = Appointment.objects.filter(
        date_time__date=date_obj
    ).values_list('date_time__time', flat=True)

    # Generate available slots (9 AM to 6 PM, 1-hour intervals)
    all_slots = []
    start_time = datetime.strptime('09:00', '%H:%M').time()
    end_time = datetime.strptime('18:00', '%H:%M').time()
    current_time = start_time

    while current_time <= end_time:
        if current_time not in booked_slots:
            all_slots.append(current_time.strftime('%H:%M'))
        current_time = (datetime.combine(date_obj, current_time) + timedelta(hours=1)).time()

    return JsonResponse({'available_slots': all_slots})

@user_passes_test(is_staff_or_admin)
def update_appointment_status(request, appointment_id):
    if request.method == 'POST':
        try:
            import json
            data = json.loads(request.body)
            status = data.get('status')
            
            appointment = get_object_or_404(Appointment, id=appointment_id)
            appointment.status = status
            appointment.save()
            
            return JsonResponse({'success': True})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)}, status=400)
    return JsonResponse({'error': 'Invalid request method'}, status=405)

@login_required
def get_appointment_details(request, appointment_id):
    try:
        appointment = get_object_or_404(Appointment, id=appointment_id)
        
        # Check if user has permission to view this appointment
        if not request.user.is_staff and appointment.customer != request.user:
            return JsonResponse({'error': 'Permission denied'}, status=403)
        
        data = {
            'customer_name': appointment.customer.get_full_name() or appointment.customer.username,
            'stage': appointment.get_stage_display(),
            'date_time': appointment.date_time.strftime('%B %d, %Y %I:%M %p'),
            'status': appointment.get_status_display(),
            'notes': appointment.notes,
            'created_by': appointment.created_by.get_full_name() if appointment.created_by else 'System',
            'created_at': appointment.created_at.strftime('%B %d, %Y %I:%M %p')
        }
        
        return JsonResponse(data)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)

@login_required
def get_order_details(request, order_id):
    try:
        order = get_object_or_404(Order, id=order_id)
        
        # Check if user has permission to view this order
        if not request.user.is_staff and order.customer != request.user:
            return JsonResponse({'error': 'Permission denied'}, status=403)
        
        # Get order items
        items = [{
            'name': item.clothing_item.name,
            'quantity': item.quantity,
            'price': float(item.price),
            'total': float(item.total_price),
            'notes': item.notes
        } for item in order.items.all()]
        
        # Get payments
        payments = [{
            'type': payment.get_payment_type_display(),
            'method': payment.get_payment_method_display(),
            'amount': float(payment.amount),
            'date': payment.payment_date.strftime('%B %d, %Y %I:%M %p'),
            'transaction_id': payment.transaction_id,
            'notes': payment.notes
        } for payment in order.payments.all()]
        
        data = {
            'order_id': order.id,
            'customer_name': order.customer.get_full_name() or order.customer.username,
            'status': order.get_status_display(),
            'order_date': order.order_date.strftime('%B %d, %Y %I:%M %p'),
            'delivery_date': order.delivery_date.strftime('%B %d, %Y %I:%M %p') if order.delivery_date else None,
            'total_amount': float(order.total_amount),
            'amount_paid': float(order.amount_paid),
            'balance_due': float(order.balance_due),
            'notes': order.notes,
            'items': items,
            'payments': payments,
            'created_by': order.created_by.get_full_name() if order.created_by else 'System'
        }
        
        return JsonResponse(data)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400) 