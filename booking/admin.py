from django.contrib import admin
from .models import Booking_Confirmation, TimeSlot, TurfDetails, TurfBlogs, SiteSettings
# Register your models here.
admin.site.register(Booking_Confirmation)
admin.site.register(TimeSlot)
admin.site.register(TurfDetails)
admin.site.register(TurfBlogs)
admin.site.register(SiteSettings)