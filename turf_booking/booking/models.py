from ast import mod
from django.db import models
from django.contrib.auth.models import User


# Create your models here.

class TurfDetails(models.Model):
     option1 = (
     ("Cricket","Cricket"),
     ("FootBall","FootBall"),
     ("Badminton",'Badminton')
     )
    
     Turf_id = models.AutoField(primary_key=True)
     Turf_area = models.CharField(max_length=200)
     Turf_name =models.CharField(max_length=200)
     Turf_catogary = models.CharField(max_length=200,choices=option1)
     Turf_price = models.IntegerField()
     Turf_Image = models.FileField(upload_to="Truf_Image")
     
     def __str__(self):
          return str("{} {} {} Turf".format(self.Turf_name,self.Turf_area,self.Turf_catogary))
     

     
class TimeSlot(models.Model):
     
     options = (
          ("12-01 AM", "12-01 AM"), ("01-02 AM", "01-02 AM"), ("02-03 AM", "02-03 AM"), ("03-04 AM", "03-04 AM"),
          ("04-05 AM", "04-05 AM"), ("05-06 AM", "05-06 AM"), ("06-07 AM", "06-07 AM"), ("07-08 AM", "07-08 AM"),
          ("08-09 AM", "08-09 AM"), ("09-10 AM", "09-10 AM"), ("10-11 AM", "10-11 AM"), ("11-12 AM", "11-12 AM"),
          ("12-01 PM", "12-01 PM"), ("01-02 PM", "01-02 PM"), ("02-03 PM", "02-03 PM"), ("03-04 PM", "03-04 PM"),
          ("04-05 PM", "04-05 PM"), ("05-06 PM", "05-06 PM"), ("06-07 PM", "06-07 PM"), ("07-08 PM", "07-08 PM"),
          ("08-09 PM", "08-09 PM"), ("09-10 PM", "09-10 PM"), ("10-11 PM", "10-11 PM"), ("11-12 PM", "11-12 PM"),
     )
     
     TimeSlot = models.CharField(max_length=255, choices=options)
     Turf = models.ForeignKey(TurfDetails,on_delete=models.CASCADE)
     Date = models.DateField(auto_now_add=False)
     Booking_status = models.BooleanField(default=False)
     
     def __str__(self):
          return str("{}   {}".format(self.Date,self.TimeSlot))
     
class Booking_Confirmation(models.Model):
         
     booking_date = models.DateField(auto_now_add=True) 
     slot = models.ForeignKey(TimeSlot,on_delete=models.CASCADE)
     cutomer = models.ForeignKey(User,on_delete=models.CASCADE,null=True,blank=True)
     customer_name = models.CharField(max_length=200)
     customer_phone = models.CharField(max_length=200)
     paymet_status = models.BooleanField(default=False)


class TurfBlogs(models.Model):
     blog_title = models.CharField(max_length = 255 )
     blog_text = models.CharField(max_length = 1000)
     image = models.FileField(upload_to="blog_image")
     date = models.DateTimeField(auto_now_add = True)

class SiteSettings(models.Model):
    about_title = models.CharField(max_length=255, default="About Us")
    about_content = models.TextField(default="Default about content...")
    contact_address = models.CharField(max_length=500, default="Our Address")
    contact_phone = models.CharField(max_length=20, default="+91 0000000000")
    contact_email = models.EmailField(default="info@example.com")
    site_name = models.CharField(max_length=255, default="BOOKTURF PRO")
    homepage_banner_title = models.CharField(max_length=255, default="Best Synthetic Turf in the City")
    homepage_banner_subtitle = models.CharField(max_length=255, default="Enjoy your Play ground")
    operating_hours = models.CharField(max_length=255, default="08.00AM - 10.00PM")
    
    # Social Media Connections
    facebook_url = models.URLField(max_length=500, default="https://facebook.com")
    instagram_url = models.URLField(max_length=500, default="https://instagram.com")
    twitter_url = models.URLField(max_length=500, default="https://twitter.com")
    
    footer_description = models.TextField(default="Premium multi-sport facilities designed for elite performance. Book your session and dominate the pitch.")

    def __str__(self):
        return "Site Settings"
     
     
     
    
