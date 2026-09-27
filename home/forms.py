from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Profile

class UserAddForm(UserCreationForm):
    phone_number = forms.CharField(
        max_length=10, 
        min_length=10, 
        required=True,
        label="Phone Number",
        widget=forms.TextInput(attrs={'placeholder': 'Enter 10-digit mobile number'})
    )

    class Meta:
        model = User
        fields = ["first_name", "username", "email"]
    
    field_order = ["first_name", "username", "email", "phone_number", "password1", "password2"]

    def clean_phone_number(self):
        phone = self.cleaned_data.get('phone_number')
        if not phone.isdigit():
            raise forms.ValidationError("Phone number must contain only digits.")
        return phone

    def save(self, commit=True):
        user = super().save(commit=commit)
        phone_number = self.cleaned_data.get('phone_number')
        
        # Profile is created automatically by signals, but we update the phone_number
        if commit:
            user.save()
            profile, created = Profile.objects.get_or_create(user=user)
            profile.phone_number = phone_number
            profile.save()
        return user