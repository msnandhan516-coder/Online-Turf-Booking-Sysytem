from pyexpat.errors import messages
from django.shortcuts import render,redirect
from django.http import HttpResponse
from django.contrib import messages
from django.contrib.auth import login,logout,authenticate
from booking.models import TurfDetails, TimeSlot, TurfBlogs, Booking_Confirmation, SiteSettings
from booking.forms import TurfDetailsForm, TimeSlotForm, BlogaddForm, SiteSettingsForm
from .forms import UserAddForm
from .decorators import admin_only
from django.contrib.auth.decorators import login_required
from datetime import datetime

# Create your views here.
# index rendering....
@admin_only
def index(request):
    blogs = TurfBlogs.objects.all().order_by('-date')[:3]
    turfs = TurfDetails.objects.all()
    settings = SiteSettings.objects.first()
    if not settings:
        settings = SiteSettings.objects.create()
    
    context = {
        "blogs": blogs,
        "turfs": turfs,
        "settings": settings
    }
    return render(request, 'index.html', context)

@login_required(login_url="signin")
def manager_home(request):
    from django.db.models import Sum
    total_bookings = Booking_Confirmation.objects.all().count()
    completed_bookings = Booking_Confirmation.objects.filter(paymet_status=True)
    completed_count = completed_bookings.count()
    
    # Dynamic revenue calculation based on actual turf prices
    total_revenue = completed_bookings.aggregate(total=Sum('slot__Turf__Turf_price'))['total'] or 0
    
    total_turfs = TurfDetails.objects.all().count()
    recent_bookings = Booking_Confirmation.objects.all().order_by('-booking_date')[:5]
    
    context = {
        "total_bookings": total_bookings,
        "completed_count": completed_count,
        "total_revenue": total_revenue,
        "total_turfs": total_turfs,
        "recent_bookings": recent_bookings
    }
    return render(request, 'turf_manager_home.html', context)

@login_required(login_url="signin")
def bulk_generate_slots(request):
    if request.method == "POST":
        turf_id = request.POST.get('turf')
        date_str = request.POST.get('date')
        start_time = int(request.POST.get('start_time', 6))
        end_time = int(request.POST.get('end_time', 22))
        
        turf = TurfDetails.objects.get(Turf_id=turf_id)
        date_obj = datetime.strptime(date_str, '%Y-%m-%d').date()
        
        created_count = 0
        for hour in range(start_time, end_time):
            # Format: "06-07 AM", "11-12 AM", "12-01 PM", "01-02 PM"
            h1 = hour % 12
            if h1 == 0: h1 = 12
            h2 = (hour + 1) % 12
            if h2 == 0: h2 = 12
            
            p1 = "AM" if hour < 12 else "PM"
            p2 = "AM" if (hour + 1) <= 12 or (hour + 1) == 24 else "PM"
            
            # Note: The model's choices are like "09-10 AM"
            # If the period changes (11-12 AM to 12-01 PM), we just use the second period for the label generally
            slot_label = f"{h1:02d}-{h2:02d} {p2}"
            
            if not TimeSlot.objects.filter(Turf=turf, Date=date_obj, TimeSlot=slot_label).exists():
                TimeSlot.objects.create(Turf=turf, Date=date_obj, TimeSlot=slot_label)
                created_count += 1
            
        messages.success(request, f"{created_count} slots generated for {turf.Turf_name} on {date_str}")
        return redirect('SlotList')

    turfs = TurfDetails.objects.all()
    return render(request, 'bulk_generate_slots.html', {'turfs': turfs})

@login_required(login_url="signin")
def site_settings_edit(request):
    settings = SiteSettings.objects.first()
    if not settings:
        settings = SiteSettings.objects.create()
    
    form = SiteSettingsForm(instance=settings)
    if request.method == "POST":
        form = SiteSettingsForm(request.POST, instance=settings)
        if form.is_valid():
            form.save()
            messages.success(request, "Site settings updated successfully")
            return redirect('manager_home')
            
    return render(request, 'site_settings_form.html', {"form": form, "title": "Update Site Settings"})

@login_required(login_url="signin")
def booking(request):
    Turf_details = TurfDetails.objects.all() 
    area = []
    cat = []
    for i in Turf_details:
        area.append(i.Turf_area)
        cat.append(i.Turf_catogary)
    area = list(set(area))
    cat = list(set(cat))
    context = {
        "area":area,
        'cat':cat,
        "turfs": Turf_details
    }
        
    return render(request, 'booking.html',context)

def about(request):
    settings = SiteSettings.objects.first()
    return render(request, 'about.html', {'settings': settings})

def contact(request):
    settings = SiteSettings.objects.first()
    return render(request, 'contact.html', {'settings': settings})

@login_required(login_url="signin")
def manage_turf(request):
    return render(request,'manage_turf.html')

def signup(request):
    form = UserAddForm()
    if request.method == "POST":
        form = UserAddForm(request.POST)
        if form.is_valid():
            form.save()
            messages.info(request,"User Created")
            return redirect('signin')
    return render(request,"register.html",{"form":form})

@login_required(login_url="signin")
def manage_users(request):
    from .models import Profile
    # Get all profiles which contain the phone numbers
    profiles = Profile.objects.select_related('user').all().order_by('user__username')
    return render(request, "manage_users.html", {"profiles": profiles})

def signin(request):
    
    if request.method == 'POST' :
        username = request.POST['username']
        password = request.POST['password']
        
        user1 = authenticate(request, username=username, password=password)
        
        if user1 is not None:
            login(request, user1)
            # Remove insecure password storage in session
            request.session['username'] = username
            return redirect('index')
        else:
            print(f"DEBUG: Authentication failed for user: {username}")
            messages.info(request, "username or password incorrect")
            return redirect("signin")
    
    return render(request, 'login.html')

def signout(request):
    
    logout(request)
    return redirect('index')


# turf settings manager

@login_required(login_url="signin")
def add_turf(request):
    form = TurfDetailsForm()
    
    if request.method == 'POST':
        form = TurfDetailsForm(request.POST,request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request,'New Turf Added to list')
            return redirect('manage_turf')
        
    return render(request,'add_turf.html',{"form":form})

@login_required(login_url="signin")
def edit_turf(request):
    
    turf = TurfDetails.objects.all()
    if request.method=='POST':
        Turf_id = request.POST['submit']
        Turf_det = TurfDetails.objects.get(Turf_id = Turf_id)
        Turf_det.delete()
        messages.info(request,'Turf Deleted succesfully')
        return redirect('edit_turf')
    
    return render(request,'edit_turf.html',{'turf':turf})

@login_required(login_url="signin")
def AddTimeSlot(request):
    form = TimeSlotForm()
    if request.method == "POST":
        form = TimeSlotForm(request.POST)
        if form.is_valid():
            Timeslot = form.cleaned_data.get("TimeSlot")
            Turf = form.cleaned_data.get("Turf")
            Date = form.cleaned_data.get("Date")
            if TimeSlot.objects.filter(TimeSlot = Timeslot, Turf = Turf,Date = Date).exists():
                messages.info(request,"Time Slot Already in list")
                return redirect("AddTimeSlot")
            else:
                form.save()
                messages.info(request,"Time Slot Added list")
                return redirect("AddTimeSlot")
            
    return render(request,"addtimeslot.html",{"form":form})

@login_required(login_url="signin")
def SlotList(request):
    # Sort by date (descending) and then time slot
    slots = TimeSlot.objects.all().order_by('-Date', 'TimeSlot')
    context = {
        "slots":slots
    }
    return render(request,"slotlist.html",context)

@login_required(login_url="signin")
def Deleteslot(request,pk):
    slot = TimeSlot.objects.get(id = pk)
    slot.delete()
    messages.info(request,"Slot deleted")
    return redirect("SlotList")

@login_required(login_url="signin")
def AddBlog(request):
    form = BlogaddForm()
    blog = TurfBlogs.objects.all()
    if request.method == "POST":
        form = BlogaddForm(request.POST,request.FILES)
        if form.is_valid():
            form.save()
            messages.info(request,"Blog Added list")
            return redirect("AddBlog")

    context = {
        "form":form,
        "blog":blog
    }
    return render(request,"blogadd.html",context)

@login_required(login_url="signin")
def deleteblog(request,pk):
    TurfBlogs.objects.get(id = pk).delete()
    messages.info(request,"Blog deleted.......")
    return redirect("AddBlog")




