"""
URL configuration for sub_app project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.contrib.auth import views as auth_views
from . import views
from . import views_admin
from . import views_appointment

urlpatterns = [
    path('', views.home, name='home'),
    path("admin/", admin.site.urls),
    path('profile/setup/', views.profile_setup, name='profile_setup'),
    path('profile/', views.profile_view, name='profile_view'),
    path('login/', auth_views.LoginView.as_view(), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('register/', views.register, name='register'),
    path('measurements/', views.measurement_dashboard, name='measurement_dashboard'),
    path('measurements/<int:clothing_type_id>/', views.view_measurement, name='view_measurement'),
    path('measurements/<int:clothing_type_id>/update/', views.update_measurement, name='update_measurement'),
    path('measurements/<int:clothing_type_id>/fields/', views.get_measurement_fields, name='get_measurement_fields'),
    
    # Custom Admin Dashboard URLs
    path('custom-admin/', views_admin.custom_admin_dashboard, name='custom_admin_dashboard'),
    path('custom-admin/customers/', views_admin.custom_admin_customers, name='custom_admin_customers'),
    path('custom-admin/customers/add/', views_admin.add_customer, name='add_customer'),
    path('custom-admin/clothing/', views_admin.custom_admin_clothing, name='custom_admin_clothing'),
    path('custom-admin/measurements/', views_admin.custom_admin_measurements, name='custom_admin_measurements'),
    path('custom-admin/measurements/add/', views_admin.add_measurement, name='add_measurement'),
    path('custom-admin/measurements/customer/<int:customer_id>/', views_admin.get_customer_measurements, name='get_customer_measurements'),
    
    # Subscription Management URLs
    path('custom-admin/plans/', views_admin.subscription_plans, name='subscription_plans'),
    path('custom-admin/plans/<str:plan_type>/subscribe/', views_admin.subscribe_plan, name='subscribe_plan'),
    path('custom-admin/plans/<str:plan_type>/items/', views_admin.manage_plan_items, name='manage_plan_items'),

    # Appointment URLs
    path('appointments/', views_appointment.appointment_list, name='appointment_list'),
    path('appointments/book/', views_appointment.book_appointment, name='book_appointment'),
    path('appointments/available-slots/', views_appointment.get_available_slots, name='get_available_slots'),
    path('appointments/<int:appointment_id>/update-status/', views_appointment.update_appointment_status, name='update_appointment_status'),
    path('appointments/<int:appointment_id>/details/', views_appointment.get_appointment_details, name='get_appointment_details'),

    # Order URLs
    path('orders/', views_appointment.order_list, name='order_list'),
    path('orders/new/', views_appointment.manage_order, name='create_order'),
    path('orders/<int:order_id>/edit/', views_appointment.manage_order, name='edit_order'),
    path('orders/<int:order_id>/payment/', views_appointment.record_payment, name='record_payment'),
    path('orders/<int:order_id>/details/', views_appointment.get_order_details, name='get_order_details'),
]
