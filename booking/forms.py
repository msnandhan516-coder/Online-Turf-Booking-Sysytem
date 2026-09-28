from django import forms
from .models import TurfDetails, TimeSlot, TurfBlogs, SiteSettings
from datetime import date

dy = date.today
class TurfDetailsForm(forms.ModelForm):
    
    class Meta:
        model = TurfDetails
        fields = '__all__'
        
class TimeSlotForm(forms.ModelForm):
    class Meta:
        model = TimeSlot
        fields = ["TimeSlot","Turf","Date"]
        
        widgets = {
            "Date": forms.TextInput(attrs={"type":"date","min":dy})
        }

class BlogaddForm(forms.ModelForm):
    class Meta:
        model = TurfBlogs
        fields = ["blog_title","blog_text","image"]

class SiteSettingsForm(forms.ModelForm):
    class Meta:
        model = SiteSettings
        fields = '__all__'
