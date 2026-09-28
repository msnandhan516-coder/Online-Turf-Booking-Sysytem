from django.shortcuts import render,redirect
from django.contrib import messages
from django.http import HttpResponse
from datetime import datetime
from .models import TurfDetails, Booking_Confirmation,TimeSlot
import json
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from django.template.loader import render_to_string
from django.http import HttpResponseBadRequest
from django.contrib.auth.decorators import login_required
from datetime import datetime


# Razorpay Client Removed - Transitioned to Simulated Payment Mode


# Create your views here.
@login_required(login_url="signin")
def turf_details(request):
    
    turf_area = request.POST['area']
    turf_catogary = request.POST['catogary']
    
    items = TurfDetails.objects.filter(Turf_area= turf_area,Turf_catogary = turf_catogary)
    if items is not None:
        return render (request,'turf_list.html',{'items':items})
    else:
        messages.info(request,'Turf Not Found')
        return redirect('booking')
    
@login_required(login_url="signin")
def book_slot(request):
    turf_id = request.POST.get('submit')
    turf = TurfDetails.objects.get(Turf_id=turf_id)
    date_now = datetime.now().date()
    
    # Show slots from today onwards
    slots = TimeSlot.objects.filter(Turf=turf, Date__gte=date_now).order_by('Date', 'TimeSlot')
    
    # Pre-populate user info if available
    user_initial = {
        'name': f"{request.user.first_name} {request.user.last_name}".strip(),
        'phone': ''
    }
    if hasattr(request.user, 'profile'):
        user_initial['phone'] = request.user.profile.phone_number

    context = {
        'turf': [turf],
        "slots": slots,
        "date": date_now,
        "user_initial": user_initial,
    }
            
    return render(request, 'book_slot.html', context)

@login_required(login_url="signin")
def book_confirm(request):
    try:
        customer_name = request.POST['customer_name']
        customer_mobile = request.POST['customer_mobile']
        slotid = request.POST["timesloat"]
        slot = TimeSlot.objects.get(id=slotid)
        
        # Concurrency safety check
        if slot.Booking_status:
            messages.info(request, "This slot was just booked by someone else. Please select another slot.")
            return redirect("booking")

        confirmation = Booking_Confirmation.objects.create(
            slot=slot, 
            customer_name=customer_name, 
            customer_phone=customer_mobile,
            cutomer=request.user
        )
    except Exception as e:
        print(f"Booking Initiation Error: {e}")
        messages.info(request, "An error occurred while initiating the booking.")
        return redirect("booking")
    
    currency = 'INR'
    # Use dynamic price from Turf model
    # Use dynamic price from Turf model
    amount = int(slot.Turf.Turf_price)

    # Simulated Payment Context (Bypassing Razorpay Order Creation)
    context = {
        'slotid': confirmation.id,
        'amount': amount,
        'turf_name': slot.Turf.Turf_name,
        'customer_name': customer_name
    }
        
    return render(request, "makepayment.html", context)

def StatusChange(request, pk):
    booking = Booking_Confirmation.objects.get(id=pk)
    booking.paymet_status = True
    booking.save()
    
    slot = booking.slot
    slot.Booking_status = True
    slot.save()
    
    return render(request, "booking_confirm.html", {"booking": booking})
@login_required(login_url="signin")
def approve_booking(request, pk):
    booking = Booking_Confirmation.objects.get(id=pk)
    booking.paymet_status = True
    booking.save()
    
    # Also update the slot status to confirmed
    slot = booking.slot
    slot.Booking_status = True
    slot.save()
    
    messages.success(request, f"Booking #{pk} has been verified and confirmed.")
    return redirect('manage_booking')
    
    
@csrf_exempt
def paymenthandler(request):
    if request.method == "POST":
        try:
            booking_id = request.GET.get('booking_id')
            payment_id = request.POST.get('razorpay_payment_id', '')
            razorpay_order_id = request.POST.get('razorpay_order_id', '')
            signature = request.POST.get('razorpay_signature', '')
            params_dict = {
                'razorpay_order_id': razorpay_order_id,
                'razorpay_payment_id': payment_id,
                'razorpay_signature': signature
            }

            # verify the payment signature.
            result = razorpay_client.utility.verify_payment_signature(params_dict)
            if result is not None:
                # Get the actual amount from the booking details
                booking = Booking_Confirmation.objects.get(id=booking_id)
                amount = int(booking.slot.Turf.Turf_price) * 100
                try:
                    razorpay_client.payment.capture(payment_id, amount)
                    return redirect('StatusChange', pk=booking_id)
                except:
                    # Capture might fail if already captured or other reasons
                    return redirect('StatusChange', pk=booking_id)
            else:
                return render(request, 'paymentfail.html')
        except Exception as e:
            print(f"Payment Error: {e}")
            return HttpResponseBadRequest()
        
      # if we don't find the required parameters in POST data
    else:
  # if other than POST request is made.
        return HttpResponseBadRequest()
        
        
        
@login_required(login_url="signin")
def manage_booking(request):
    
    bookings = Booking_Confirmation.objects.all()
    return render(request,'manage_booking.html',{'bookings':bookings})

@login_required(login_url="signin")
def cancelbooking(request,pk):
    booking = Booking_Confirmation.objects.get(id = pk)
    slotid = booking.slot.id
    slot = TimeSlot.objects.get(id = slotid)
    slot.Booking_status = False
    slot.save()
    booking.delete()
    messages.info(request,"Booking Deleted")

    return redirect("manage_booking")

@login_required(login_url="signin")
def cancelbookinguser(request,pk):
    booking = Booking_Confirmation.objects.get(id = pk)
    slotid = booking.slot.id
    slot = TimeSlot.objects.get(id = slotid)
    slot.Booking_status = False
    slot.save()
    booking.delete()
    messages.info(request,"Booking Deleted")

    return redirect("MyBookings")

@login_required(login_url="signin")
def MyBookings(request):
    
    dt = datetime.now()
    print(dt)
    dt = dt.date()
    upcomming = []
    previous = []
    today = []
    booking = Booking_Confirmation.objects.filter(cutomer = request.user)
    for i in booking:
        timeslot = i.slot
        if timeslot.Date > dt:
            upcomming.append(i)
        elif timeslot.Date == dt:
            today.append(i)
        elif  timeslot.Date < dt:
            previous.append(i)
        
    context= {
        "booking":upcomming,
        "previous":previous,
        'today':today
    }
    
    return render(request,"mybookings.html",context)




    
    
        
        
        
    
    