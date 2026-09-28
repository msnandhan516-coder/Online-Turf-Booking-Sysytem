from django.urls import path
from.import views

urlpatterns = [
    path('turf_details',views.turf_details,name='turf_details'),
    path('book_slot',views.book_slot,name='book_slot'),
    path('book_confirm',views.book_confirm,name = 'book_confirm'),
    path('manage_booking',views.manage_booking,name= 'manage_booking'),
    path('paymenthandler/', views.paymenthandler, name='paymenthandler'),
    path("StatusChange/<int:pk>",views.StatusChange,name="StatusChange"),
    path("approve_booking/<int:pk>",views.approve_booking,name="approve_booking"),
    path("cancelbooking/<int:pk>",views.cancelbooking,name="cancelbooking"),
    path("MyBookings",views.MyBookings,name="MyBookings"),
    path("cancelbookinguser/<int:pk>",views.cancelbookinguser,name="cancelbookinguser"),
    
]
