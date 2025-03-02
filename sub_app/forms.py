from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import User, UserMeasurements

class UserPreferencesForm(forms.ModelForm):
    STYLE_CHOICES = [
        ('casual', 'Casual'),
        ('formal', 'Formal'),
        ('bohemian', 'Bohemian'),
        ('vintage', 'Vintage'),
        ('minimalist', 'Minimalist'),
    ]
    
    COLOR_PREFERENCES = [
        ('warm', 'Warm Colors'),
        ('cool', 'Cool Colors'),
        ('neutral', 'Neutral Colors'),
        ('bright', 'Bright Colors'),
    ]
    
    preferred_style = forms.MultipleChoiceField(
        choices=STYLE_CHOICES,
        widget=forms.CheckboxSelectMultiple
    )
    
    color_preference = forms.ChoiceField(
        choices=COLOR_PREFERENCES,
        widget=forms.RadioSelect
    )
    
    budget_range = forms.ChoiceField(
        choices=[
            ('3L', '₹3L Annual'),
            ('5L', '₹5L Annual'),
            ('7L', '₹7L Annual'),
        ]
    )
    
    class Meta:
        model = User
        fields = ['phone', 'shipping_address', 'billing_address', 
                 'email_notifications', 'sms_notifications']

class UserMeasurementsForm(forms.ModelForm):
    chest = forms.IntegerField(min_value=20, max_value=200)
    waist = forms.IntegerField(min_value=20, max_value=200)
    hips = forms.IntegerField(min_value=20, max_value=200)
    shoulder = forms.IntegerField(min_value=20, max_value=200)
    inseam = forms.IntegerField(min_value=20, max_value=200)
    
    class Meta:
        model = UserMeasurements
        fields = ['notes']
        
    def save(self, commit=True):
        instance = super().save(commit=False)
        measurements = {
            'chest': self.cleaned_data['chest'],
            'waist': self.cleaned_data['waist'],
            'hips': self.cleaned_data['hips'],
            'shoulder': self.cleaned_data['shoulder'],
            'inseam': self.cleaned_data['inseam'],
        }
        instance.measurements = measurements
        if commit:
            instance.save()
        return instance 

class UserRegistrationForm(UserCreationForm):
    phone = forms.CharField(max_length=15)
    address = forms.CharField(widget=forms.Textarea)
    
    class Meta:
        model = User
        fields = ['username', 'email', 'phone', 'address', 'password1', 'password2'] 