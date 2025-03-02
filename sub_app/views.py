from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import UserPreferencesForm, UserMeasurementsForm, UserRegistrationForm
from .models import UserMeasurements, ClothingMeasurements, CustomerMeasurement
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods

def home(request):
    return render(request, 'home.html')

@login_required
def profile_setup(request):
    try:
        measurements = request.user.usermeasurements
    except UserMeasurements.DoesNotExist:
        measurements = None

    if request.method == 'POST':
        preferences_form = UserPreferencesForm(request.POST, instance=request.user)
        measurements_form = UserMeasurementsForm(request.POST, instance=measurements)
        
        if preferences_form.is_valid() and measurements_form.is_valid():
            # Save preferences
            user = preferences_form.save(commit=False)
            style_prefs = {
                'preferred_style': preferences_form.cleaned_data['preferred_style'],
                'color_preference': preferences_form.cleaned_data['color_preference'],
                'budget_range': preferences_form.cleaned_data['budget_range'],
            }
            user.style_preferences = style_prefs
            user.style_quiz_completed = True
            user.save()
            
            # Save measurements
            measurements = measurements_form.save(commit=False)
            measurements.user = request.user
            measurements.save()
            
            messages.success(request, 'Profile updated successfully!')
            return redirect('profile_view')
    else:
        preferences_form = UserPreferencesForm(instance=request.user)
        measurements_form = UserMeasurementsForm(instance=measurements)
    
    return render(request, 'profile_setup.html', {
        'preferences_form': preferences_form,
        'measurements_form': measurements_form,
    })

@login_required
def profile_view(request):
    try:
        measurements = request.user.usermeasurements
    except UserMeasurements.DoesNotExist:
        measurements = None
        
    return render(request, 'profile_view.html', {
        'user': request.user,
        'measurements': measurements,
    })

def register(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            messages.success(request, f'Account created for {username}! You can now log in.')
            return redirect('login')
    else:
        form = UserRegistrationForm()
    return render(request, 'registration/register.html', {'form': form})

@login_required
def measurement_dashboard(request):
    clothing_types = ClothingMeasurements.objects.all()
    customer_measurements = CustomerMeasurement.objects.filter(user=request.user)
    
    context = {
        'clothing_types': clothing_types,
        'customer_measurements': customer_measurements,
    }
    return render(request, 'measurements/dashboard.html', context)

@login_required
def view_measurement(request, clothing_type_id):
    clothing_type = get_object_or_404(ClothingMeasurements, id=clothing_type_id)
    measurement = CustomerMeasurement.objects.filter(
        user=request.user,
        clothing_type=clothing_type
    ).first()
    
    context = {
        'clothing_type': clothing_type,
        'measurement': measurement,
    }
    return render(request, 'measurements/view_measurement.html', context)

@login_required
@require_http_methods(["POST"])
def update_measurement(request, clothing_type_id):
    clothing_type = get_object_or_404(ClothingMeasurements, id=clothing_type_id)
    
    measurement, created = CustomerMeasurement.objects.get_or_create(
        user=request.user,
        clothing_type=clothing_type,
    )
    
    # Update measurements from form data
    new_measurements = {}
    for field in clothing_type.measurement_fields.keys():
        value = request.POST.get(field)
        if value:
            new_measurements[field] = float(value)
    
    measurement.measurements = new_measurements
    measurement.notes = request.POST.get('notes', '')
    measurement.save()
    
    messages.success(request, f'Measurements for {clothing_type.clothing_type} updated successfully!')
    return redirect('measurement_dashboard')

@login_required
@require_http_methods(["GET"])
def get_measurement_fields(request, clothing_type_id):
    clothing_type = get_object_or_404(ClothingMeasurements, id=clothing_type_id)
    return JsonResponse({
        'fields': clothing_type.measurement_fields,
        'description': clothing_type.description
    }) 