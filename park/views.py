from django.conf import Settings
from django.shortcuts import render, redirect
from django.utils.datastructures import MultiValueDictKeyError
from django.http import HttpResponse
from django.contrib.auth.forms import UserCreationForm
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout

from django.contrib.auth.decorators import login_required

from .models import *
from .forms import *
from .utils import *

from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.utils.timezone import now, localtime
from .models import *
from django.contrib.auth.models import User
from django.db.models import Q

import qrcode
import qrcode.image.svg
from io import BytesIO
from django.core.files.base import ContentFile
from django.http import Http404

from django.shortcuts import render, get_object_or_404
from django.utils import timezone
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.utils.dateparse import parse_date
from calendar import monthrange
from datetime import datetime, date, timedelta
from django.utils.timezone import make_aware

from django.contrib.auth.models import AnonymousUser

import pytz
from django.core.paginator import Paginator
import json
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch



def get_remaining_time(reservation):
    """Returns the remaining time in seconds until the parking reservation ends."""
    user_timezone = pytz.timezone('Asia/Manila')  # Adjust to your timezone
    current_time = localtime(now(), user_timezone).replace(tzinfo=None)

    print(current_time)

    if reservation.reservation_end_time:
        print(reservation.get_local_end_time().replace(tzinfo=None))
        print(reservation.get_local_end_time().replace(tzinfo=None) > current_time)
        if reservation.get_local_end_time().replace(tzinfo=None) > current_time:
            remaining_time = reservation.get_local_end_time().replace(tzinfo=None) - current_time
            return remaining_time.total_seconds()  # Return seconds remaining
    return 0

# def send_start_reservation_reminders():
#     return_json = []

#     user_timezone = pytz.timezone('Asia/Manila')
#     current_time = localtime(now(), user_timezone).replace(tzinfo=None)

#     reservations = Reservation.objects.filter(
#         start_time__gte=current_time + timedelta(hours=1),
#         start_time__lt=current_time + timedelta(hours=1, minutes=5),
#         status="pending"
#     )
#     print("reservations", reservations)
#     print("current_time + timedelta(hours=1)", current_time + timedelta(hours=1))
#     print("current_time + timedelta(hours=1, minutes=5)", current_time + timedelta(hours=1, minutes=5))

#     reservation_len = len(reservations)

#     for reservation in reservations:
#         send_parking_notification(
#             reservation.user.email, 
#             reservation.user.username,
#             reservation.start_time.replace(tzinfo=None),
#             reservation.spot.name)

#     return_json["reservation_len"] = reservation_len
#     return_json["current_time_timedelta1hr"] = current_time + timedelta(hours=1)
#     return_json["current_time_timedelta1hr5min"] = current_time + timedelta(hours=1, minutes=5)
    
#     return return_json

# def send_end_reservation_reminders():

#     return_json = []

#     user_timezone = pytz.timezone('Asia/Manila')
#     current_time = localtime(now(), user_timezone).replace(tzinfo=None)

#     end_reminders = Reservation.objects.filter(
#             end_time__gte=current_time + timedelta(hours=1),
#             end_time__lt=current_time + timedelta(hours=1, minutes=5),
#             status="parked"
#     )

#     reservation_len = len(end_reminders)

#     for reservation in end_reminders:
#         send_parking_end_notification(
#             reservation.user.email, 
#             reservation.user.username,
#             reservation.end_time.replace(tzinfo=None),
#             reservation.spot.name
#         )

#     return_json["reservation_len"] = reservation_len
#     return_json["current_time_timedelta1hr"] = current_time + timedelta(hours=1)
#     return_json["current_time_timedelta1hr5min"] = current_time + timedelta(hours=1, minutes=5)
    
#     return return_json

# @login_required(login_url='login')
def LandingPage(request):
    return render(request, 'park/landing.html')

def About(request):
    return render(request, 'park/about.html')

def Services(request):
    return render(request, 'park/services.html')

def Reviews(request):
    return render(request, 'park/reviews.html')

def Login(request):
    if request.user.is_authenticated:
        if request.user.is_staff:
            if request.user.is_superuser:
                return redirect('admin_dashboard')
            return redirect('admin_dashboard')
        else:
            return redirect('dashboard')
    else:
        if request.method == "POST":
            username = request.POST.get("username")
            password = request.POST.get("password")
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                if user.is_staff:
                    if user.is_superuser:
                        return redirect('admin_dashboard')
                    return redirect('admin_dashboard')
                return redirect("dashboard")
            else:
                messages.info(request, "Username or Password is Incorrect")
    return render(request, 'park/login.html')

def Register(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    else:
        form = CreateUserForm()
        if request.method == 'POST':
            user_email = request.POST.get("email")
            if User.objects.filter(email=user_email).exists():
                system_messages = messages.get_messages(request)
                for message in system_messages:
                    # This iteration is necessary
                    pass
                messages.error(request, "This email is already registered.")
                return redirect('login')
            
            form = CreateUserForm(request.POST)
            verification_code = create_rand_id()
            if form.is_valid():
                user = form.save()
                username = form.cleaned_data.get('username')
                email = form.cleaned_data.get("email")
                Profile.objects.create(
                    user=user,
                    email=email,
                    verification_code=verification_code
                )
                send_verification_email(email, user, verification_code)
            
                system_messages = messages.get_messages(request)
                for message in system_messages:
                    # This iteration is necessary
                    pass


                messages.success(request, "Account Created For " + username)
                return redirect('login')
            else:
                system_messages = messages.get_messages(request)
                for message in system_messages:
                    # This iteration is necessary
                    pass
                messages.info(request, "Make Sure your Credentials is Correct or Valid")
            
    context = {"form": form}
    return render(request, 'park/login.html', context)

def Logout(request):
    logout(request)
    return redirect('login')

# def Dashboard(request):
#     return render(request, 'park/base.html')

# Dashboard view
@login_required(login_url='login')
def Dashboard(request):
    user = Profile.objects.get(user=request.user)
    if user.is_verified:
        if user.is_first_time:
            return redirect('user_profile')
    else:
        return redirect('need_verification')
    total_spots = ParkingSpot.objects.count()
    reserved_spots = ParkingSpot.objects.filter(is_reserved=True).count()
    occupied_spots = ParkingSpot.objects.filter(is_occupied=True).count()
    available_spots = total_spots - reserved_spots - occupied_spots

    # send_start_reservation_reminders()
    # send_end_reservation_reminders()
    context = {
        'total_spots': total_spots,
        'reserved_spots': reserved_spots,
        'occupied_spots': occupied_spots,
        'available_spots': available_spots,
    }
    return render(request, 'park/dashboard.html', context)

# Parking spot list and detail views
@login_required(login_url='login')
def parking_spots(request):
    spots = ParkingSpot.objects.all()
    # print(request.get_host())
    return render(request, 'park/parking_spots.html', {'spots': spots})

@login_required(login_url='login')
def parking_spot_detail(request, spot_id):
    spot = get_object_or_404(ParkingSpot, id=spot_id)
    
    return render(request, 'park/parking_spot_detail.html', {'spot': spot})

# Create, update, delete parking spots
@login_required(login_url='login')
def create_parking_spot(request):
    if request.method == 'POST':
        spot_number = request.POST['spot_number']
        name = request.POST['name']
        is_handicapped = request.POST.get('is_handicapped', False)
        is_charging = request.POST.get('is_charging', False)
        is_vip = request.POST.get('is_vip', False)

        ParkingSpot.objects.create(
            spot_number=spot_number,
            name=name,
            is_handicapped=is_handicapped,
            is_charging=is_charging,
            is_vip=is_vip
        )
        return redirect('parking_spots')

    return render(request, 'park/create_parking_spot.html')

@login_required(login_url='login')
def update_parking_spot(request, spot_id):
    spot = get_object_or_404(ParkingSpot, id=spot_id)
    if request.method == 'POST':
        spot.spot_number = request.POST['spot_number']
        spot.name = request.POST['name']
        spot.is_handicapped = request.POST.get('is_handicapped', False)
        spot.is_charging = request.POST.get('is_charging', False)
        spot.is_vip = request.POST.get('is_vip', False)
        spot.save()
        return redirect('parking_spots')

    return render(request, 'park/update_parking_spot.html', {'spot': spot})

@login_required(login_url='login')
def delete_parking_spot(request, spot_id):
    spot = get_object_or_404(ParkingSpot, id=spot_id)
    spot.delete()
    return redirect('parking_spots')

# Reservation views
@login_required(login_url='login')
def reservations(request):
    reservations = Reservation.objects.filter(user=request.user, status__in=["complete", "expired"])
    for i in reservations:
        print(i.user.email)
    return render(request, 'park/reservations.html', {'reservations': reservations})

@login_required(login_url='login')
def reserve_spot(request):
    spots = ParkingSpot.objects.filter(is_reserved=False, is_occupied=False)

    if request.method == 'POST':
        spot_id = request.POST['spot_id']
        start_time = make_aware(datetime.strptime(request.POST['start_time'], "%Y-%m-%dT%H:%M"))
        end_time = make_aware(datetime.strptime(request.POST['end_time'], "%Y-%m-%dT%H:%M"))
        plate_number = request.POST['plate_number']

        spot = get_object_or_404(ParkingSpot, id=spot_id)

        # Check if the spot is already occupied
        if spot.is_occupied:
            messages.info(request, 'Spot is already reserved or occupied')
            return redirect('available')
        # Check for overlapping reservations
        existing_reservations = Reservation.objects.filter(
            spot=spot,
            end_time__gt=start_time,  # Ends after the new start time
            start_time__lt=end_time    # Starts before the new end time
        )

        if existing_reservations.exists():
            messages.info(request, 'Spot is already reserved or occupied')
            return redirect('available')

        # Create the reservation with status "Pending"
        reservation = Reservation.objects.create(
            user=request.user,
            spot=spot,
            plate_number=plate_number,
            start_time=start_time,
            end_time=end_time,
            status="pending"  # Set initial status
        )
        spot.is_reserved = True
        spot.save()

        # Generate QR code
        qr_data = f"{request.get_host()}/scan_to_occupy/{reservation.id}"
        qr = qrcode.make(qr_data)
        buffer = BytesIO()
        qr.save(buffer, format="PNG")

        # Attach QR code to reservation object
        reservation.qr.save(f"qr_{reservation.spot.name}.png", ContentFile(buffer.getvalue()), save=True)

        
        # Save the buffer content as an image response
        # buffer.seek(0)  # Move to the beginning of the buffer
        # response = HttpResponse(buffer.read(), content_type="image/png")
        # response["Content-Disposition"] = f"attachment; filename=reservation_{reservation.spot.name}.png"
        # return response

    # Fetch available spots
    return redirect('current')

@login_required(login_url='login')
def cancel_reservation(request, reservation_id):
    reservation = get_object_or_404(Reservation, id=reservation_id, user=request.user)
    reservation.spot.is_reserved = False
    reservation.spot.save()
    reservation.delete()
    return redirect('current')

# Parked vehicle views
@login_required(login_url='login')
def parked_vehicles(request):
    parked = Reservation.objects.filter(user=request.user, status__in=["parked", "pending"])
    return render(request, 'park/parked_vehicles.html', {'parked': parked})

@login_required(login_url='login')
def park_vehicle(request):
    if request.method == 'POST':
        spot_id = request.POST['spot_id']
        start_time = now()

        spot = get_object_or_404(ParkingSpot, id=spot_id)
        if spot.is_occupied:
            return JsonResponse({'error': 'Spot is already occupied'}, status=400)

        parked = Parked.objects.create(
            user=request.user,
            spot=spot,
            start_time=start_time,
            end_time=None
        )
        spot.is_occupied = True
        spot.save()

        return redirect('parked_vehicles')

    spots = ParkingSpot.objects.filter(is_reserved=False, is_occupied=False)
    return render(request, 'park/park_vehicle.html', {'spots': spots})

@login_required(login_url='login')
def unpark_vehicle(request, parked_id):
    parked = get_object_or_404(Parked, id=parked_id, user=request.user, is_active=True)
    parked.is_active = False
    parked.end_time = now()
    parked.spot.is_occupied = False
    parked.spot.save()
    parked.save()
    return redirect('parked_vehicles')

@login_required(login_url='login')
def view_qr(request, reservation_id):
    try:
        # Fetch the reservation with the given ID and ensure it is active
        reservation = get_object_or_404(Reservation, id=reservation_id, is_active=True)

        # Log debug information (optional)
        print(f"Reservation ID: {reservation_id}")
        print(f"Reservation: {reservation}")

        # Render the QR view template
        return render(request, 'park/view_qr.html', {'reservation': reservation})
    except Http404:
        # Handle the case where the reservation is not found or not active
        return render(request, 'park/error.html', {
            'message': "The reservation you are trying to view does not exist or is no longer active."
        })
    except Exception as e:
        # Handle any unexpected errors
        print(f"Unexpected error: {e}")
        return render(request, 'park/error.html', {
            'message': "An unexpected error occurred. Please try again later."
        })
    

# Calendar 
@login_required(login_url='login')
def calendar_view(request):
    # Set timezone to Asia/Manila
    manila_tz = pytz.timezone('Asia/Manila')
    today = localtime(now(), manila_tz)
    
    try:
        month = int(request.GET.get('month', today.month))
        year = int(request.GET.get('year', today.year))
        
        # Validate month and year
        if month < 1 or month > 12:
            month = today.month
        if year < 1900 or year > 9999:
            year = today.year
            
        # Create datetime in Manila timezone
        start_day = manila_tz.localize(datetime(year, month, 1))
        days_in_month = monthrange(year, month)[1]
        
        # Get reservations for the month in Manila timezone
        reservations = Reservation.objects.filter(
            start_time__year=year,
            start_time__month=month
        )
        
        # Convert reservation dates to Manila timezone
        reserved_dates = {
            res.start_time.astimezone(manila_tz).date() 
            for res in reservations
        }
        
        first_weekday = start_day.weekday()
        calendar_days = []
        
        # Fill in the empty days at the start of the month
        for _ in range(first_weekday):
            calendar_days.append(None)
            
        # Fill in the days of the current month
        for day in range(1, days_in_month + 1):
            calendar_days.append(
                manila_tz.localize(datetime(year, month, day)).date()
            )
            
        # Ensure the total days fill complete weeks (42 days for 6 weeks)
        while len(calendar_days) % 7 != 0:
            calendar_days.append(None)
            
        # Split days into weeks
        weeks = [calendar_days[i:i + 7] for i in range(0, len(calendar_days), 7)]

        context = {
            'weeks': weeks,
            'reserved_dates': reserved_dates,
            'current_month': month,
            'current_year': year,
        }
        return render(request, 'park/calendar.html', context)
    except (ValueError, TypeError):
        # If there's any error in parsing the date, return to current month/year
        return redirect('calendar')

# Reservations by Date View
@login_required(login_url='login')
def reservations_by_date(request, selected_date):
    date_obj = parse_date(selected_date)
    reservations = Reservation.objects.filter(start_time__date=date_obj)
    context = {'reservations': reservations}
    return render(request, 'park/reservations_by_date.html', context)


@login_required(login_url='login')
def reservations_by_spot(request, pk):
    spot_obj = ParkingSpot.objects.get(id=pk)
    reservations = Reservation.objects.filter(spot=spot_obj)

    remaining_seconds = get_remaining_time(spot_obj)

    print(remaining_seconds)

    context = {'reservations': reservations, 'spot': spot_obj,  'remaining_seconds': remaining_seconds}
    return render(request, 'park/reservations_by_spot.html', context)

def scan_to_occupy(request, pk):
    reservation = get_object_or_404(Reservation, id=pk, status__in=["parked", "pending"])
    print(reservation)
    spot = get_object_or_404(ParkingSpot, id=reservation.spot.id)
    print(spot)


    
    # Convert all times to the same timezone (e.g., system's local timezone)
    user_timezone = pytz.timezone('Asia/Manila')  # Change this to your desired timezone
    
    # start_time = reservation.start_time.replace(tzinfo=None)
    # end_time = reservation.end_time.replace(tzinfo=None)

    # Get the current server time and remove timezone
    current_time = localtime(now(), user_timezone).replace(tzinfo=None)

    # Format times in 12-hour format
    def format_time(dt):
        return dt.strftime('%Y-%m-%d %I:%M:%S')  # 12-hour format with timezone

    # print("start_time:", start_time)
    # print("end_time:", end_time)
    # print("current_time:", current_time)

    print("Start Time:", reservation.get_local_start_time().replace(tzinfo=None))
    print("Current Time:", current_time)
    # print("End Time:", format_time(reservation.get_local_end_time()))

    print(reservation.spot.is_occupied)
    print(reservation.spot.is_reserved)

    if reservation.get_local_start_time().replace(tzinfo=None) <= current_time <= \
        reservation.get_local_end_time().replace(tzinfo=None):
        if reservation.spot.is_occupied:
            # If already occupied, unoccupy it
            reservation.spot.is_occupied = False
            reservation.spot.is_reserved = False
            reservation.is_active = False
            reservation.status = "complete"

            parked_user = reservation.user
            parked_user_exist = Parked.objects.filter(user=parked_user, spot=spot, end_time=None, is_active=True).first()

            if parked_user_exist:
                parked_user_exist.end_time = current_time
                parked_user_exist.is_active = False
                parked_user_exist.save()

            reservation.spot.reservation_end_time = None
            reservation.spot.save()
            reservation.save()

            return redirect('done_parking')
        else:
            # Otherwise, mark it as occupied
            reservation.spot.is_occupied = True
            reservation.spot.is_reserved = False
            reservation.status = "parked"

            parked_user = reservation.user

            reservation.spot.reservation_end_time = reservation.get_local_end_time().replace(tzinfo=None)
            print("Reservation End Time:",  reservation.spot.reservation_end_time)

            Parked.objects.create(
                user=parked_user,
                spot=spot,
                start_time=current_time,
                end_time=None
            )

            reservation.spot.save()
            reservation.save()
            
            return redirect('you_are_now_parked')
    else:
        if reservation.spot.is_occupied:
            reservation.spot.is_occupied = False
            reservation.spot.is_reserved = False
            reservation.status = "complete"

            parked_user = reservation.user
            parked_user_exist = Parked.objects.filter(user=parked_user, spot=spot, end_time=None, is_active=True).first()

            if parked_user_exist:
                parked_user_exist.end_time = current_time
                parked_user_exist.is_active = False

                # Calculate exceeded hours
                exceeded_time = current_time - reservation.get_local_end_time().replace(tzinfo=None)
                exceeded_hours = exceeded_time.total_seconds() / 3600  # Convert seconds to hours

                exceeded_hours = max(0, int(exceeded_hours))  # Avoid negative values
                # Save the exceeded hours (assuming you have a field for it)
                parked_user_exist.exceeded_hours = exceeded_hours  
                parked_user_exist.save()


            reservation.spot.reservation_end_time = None
            reservation.spot.save()
            reservation.save()
            
            context = {
                'exceeded_hours': exceeded_hours
            }
            return render(request, 'park/exceed_time.html', context)
        else:
            return redirect('not_in_schedule')


def termsandconditions(request):
    return render(request, 'park/termsandcondition.html')

# Email Verification
def VerifyEmail(request, verification_code):
    patient = Profile.objects.get(verification_code=verification_code)
    patient.is_verified = True
    patient.save()
    return render(request, 'park/verified.html')

def send_verification_email(email, user, verification_code):
    subject = 'Email Verification'
    message = f'Hi {user.username},\n\nPlease click the link below to verify your email address:\n\nhttps://tctparking.ellequin.com/verify_email/{verification_code}'
    send_email(subject, message, [email])

def NeedVerification(request):
    logout(request)
    return render(request, 'park/need_verification.html')

# Profile
def UserProfile(request):
    user_profile = Profile.objects.get(user=request.user)
    if request.method == 'POST':
        form = ProfileForm(request.POST, request.FILES, instance=user_profile)
        print(form)
        if form.is_valid():
            user_profile = form.save()
            user_profile.is_first_time = False
            user_profile.save()
            return redirect('user_profile')
    context = {'user_profile': user_profile}
    return render(request, 'park/profile.html', context)


# Additional Links
def you_are_now_parked(request):
    return render(request, 'park/you_are_now_parked.html')

def not_in_schedule(request):
    return render(request, 'park/not_schedule.html')

def exceed_time(request):
    return render(request, 'park/exceed_time.html')

def done_parking(request):
    return render(request, 'park/done_parking.html')

# PWA
def AssetLink(request):
    assetlink = [
            {
            "relation": ["delegate_permission/common.handle_all_urls"],
            "target": {
                "namespace": "android_app",
                "package_name": "com.ellequin.tctparking.twa",
                "sha256_cert_fingerprints": ["DC:AB:C1:F1:A9:06:70:47:95:C3:EC:05:75:EA:C7:4C:BE:DA:51:0A:EC:08:64:36:FB:79:91:AA:6D:9E:0F:4C"]
            }
        }
    ]

    return JsonResponse(assetlink, safe=False)

@login_required(login_url='login')
def logistics_view(request):
    today = timezone.now().date()
    logistics = Logistics.objects.filter(date=today).first()
    
    if not logistics:
        # Create new logistics entry for today
        total_spots = ParkingSpot.objects.count()
        occupied_spots = ParkingSpot.objects.filter(is_occupied=True).count()
        reserved_spots = ParkingSpot.objects.filter(is_reserved=True).count()
        available_spots = total_spots - occupied_spots - reserved_spots
        
        # Calculate revenue (you can adjust the rate per hour)
        rate_per_hour = 50  # Example rate
        exceeded_hours = Parked.objects.filter(
            start_time__date=today,
            exceeded_hours__gt=0
        ).aggregate(total=models.Sum('exceeded_hours'))['total'] or 0
        
        total_revenue = exceeded_hours * rate_per_hour
        
        logistics = Logistics.objects.create(
            date=today,
            total_spots=total_spots,
            occupied_spots=occupied_spots,
            reserved_spots=reserved_spots,
            available_spots=available_spots,
            total_revenue=total_revenue,
            exceeded_hours=exceeded_hours
        )
    
    context = {
        'logistics': logistics,
        'today': today
    }
    return render(request, 'park/logistics.html', context)

@login_required(login_url='login')
def summary_view(request):
    period = request.GET.get('period', 'daily')
    today = timezone.now().date()
    
    if period == 'daily':
        start_date = today
        end_date = today
    elif period == 'weekly':
        start_date = today - timedelta(days=today.weekday())
        end_date = start_date + timedelta(days=6)
    elif period == 'monthly':
        start_date = today.replace(day=1)
        end_date = (start_date + timedelta(days=32)).replace(day=1) - timedelta(days=1)
    else:  # yearly
        start_date = today.replace(month=1, day=1)
        end_date = today.replace(month=12, day=31)
    
    summary = Summary.objects.filter(
        period_type=period,
        start_date=start_date,
        end_date=end_date
    ).first()
    
    if not summary:
        # Calculate summary data
        total_spots = ParkingSpot.objects.count()
        total_occupancy = Parked.objects.filter(
            start_time__date__gte=start_date,
            start_time__date__lte=end_date
        ).count()
        total_reservations = Reservation.objects.filter(
            start_time__date__gte=start_date,
            start_time__date__lte=end_date
        ).count()
        
        # Calculate revenue
        rate_per_hour = 50  # Example rate
        exceeded_hours = Parked.objects.filter(
            start_time__date__gte=start_date,
            start_time__date__lte=end_date,
            exceeded_hours__gt=0
        ).aggregate(total=models.Sum('exceeded_hours'))['total'] or 0
        
        total_revenue = exceeded_hours * rate_per_hour
        
        summary = Summary.objects.create(
            period_type=period,
            start_date=start_date,
            end_date=end_date,
            total_spots=total_spots,
            total_occupancy=total_occupancy,
            total_reservations=total_reservations,
            total_revenue=total_revenue,
            total_exceeded_hours=exceeded_hours
        )
    
    context = {
        'summary': summary,
        'period': period,
        'start_date': start_date,
        'end_date': end_date
    }
    return render(request, 'park/summary.html', context)

@login_required(login_url='login')
def admin_dashboard(request):
    if not request.user.is_staff:
        return redirect('dashboard')
    
    # Get statistics
    total_spots = ParkingSpot.objects.count()
    reserved_spots = ParkingSpot.objects.filter(is_reserved=True).count()
    occupied_spots = ParkingSpot.objects.filter(is_occupied=True).count()
    available_spots = total_spots - reserved_spots - occupied_spots
    
    # Get user statistics
    total_users = User.objects.count()
    verified_users = Profile.objects.filter(is_verified=True).count()
    
    # Get today's logistics
    today = timezone.now().date()
    logistics = Logistics.objects.filter(date=today).first()
    
    context = {
        'total_spots': total_spots,
        'reserved_spots': reserved_spots,
        'occupied_spots': occupied_spots,
        'available_spots': available_spots,
        'total_users': total_users,
        'verified_users': verified_users,
        'logistics': logistics,
    }
    
    return render(request, 'park/admin/dashboard.html', context)

@login_required(login_url='login')
def admin_reservations(request):
    if not request.user.is_staff:
        return redirect('dashboard')
    
    # Get filter parameters
    status = request.GET.get('status')
    date = request.GET.get('date')
    search = request.GET.get('search')
    
    # Base queryset
    reservations = Reservation.objects.all().order_by('-start_time')
    
    # Apply filters
    if status:
        reservations = reservations.filter(status=status)
    if date:
        reservations = reservations.filter(start_time__date=date)
    if search:
        reservations = reservations.filter(
            Q(user__username__icontains=search) |
            Q(spot__spot_number__icontains=search)
        )
    
    # Pagination
    paginator = Paginator(reservations, 10)
    page = request.GET.get('page')
    reservations = paginator.get_page(page)
    
    context = {
        'reservations': reservations,
    }
    
    return render(request, 'park/admin/reservations.html', context)

@login_required(login_url='login')
def admin_parked(request):
    if not request.user.is_staff:
        return redirect('dashboard')
    
    # Get filter parameters
    status = request.GET.get('status')
    date = request.GET.get('date')
    search = request.GET.get('search')
    
    # Base queryset
    parked_vehicles = Parked.objects.all().order_by('-start_time')
    
    # Apply filters
    if status:
        parked_vehicles = parked_vehicles.filter(status=status)
    if date:
        parked_vehicles = parked_vehicles.filter(start_time__date=date)
    if search:
        parked_vehicles = parked_vehicles.filter(
            Q(user__username__icontains=search) |
            Q(spot__spot_number__icontains=search)
        )
    
    # Pagination
    paginator = Paginator(parked_vehicles, 10)
    page = request.GET.get('page')
    parked_vehicles = paginator.get_page(page)
    
    context = {
        'parked_vehicles': parked_vehicles,
    }
    
    return render(request, 'park/admin/parked.html', context)

@login_required(login_url='login')
def admin_parked_detail(request, parked_id):
    if not request.user.is_staff:
        return redirect('dashboard')
    
    parked = get_object_or_404(Parked, id=parked_id)
    # Get the associated reservation to get the plate number
    reservation = Reservation.objects.filter(
        user=parked.user,
        spot=parked.spot,
        start_time__lte=parked.start_time,
        end_time__gte=parked.start_time
    ).first()
    
    context = {
        'parked': parked,
        'plate_number': reservation.plate_number if reservation else 'N/A'
    }
    return render(request, 'park/admin/parked_detail.html', context)

@login_required(login_url='login')
def admin_logistics(request):
    if not request.user.is_staff:
        return redirect('dashboard')
    
    # Get filter parameters
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')
    
    # Base queryset
    logistics = Logistics.objects.all().order_by('-date')
    
    # Apply filters
    if start_date:
        logistics = logistics.filter(date__gte=start_date)
    if end_date:
        logistics = logistics.filter(date__lte=end_date)
    
    # Get data for charts
    dates = [log.date.strftime('%Y-%m-%d') for log in logistics[:7]]
    occupied_spots_data = [log.occupied_spots for log in logistics[:7]]
    reserved_spots_data = [log.reserved_spots for log in logistics[:7]]
    revenue_data = [float(log.total_revenue) for log in logistics[:7]]
    
    # Calculate totals
    total_spots = ParkingSpot.objects.count()
    occupied_spots = ParkingSpot.objects.filter(is_occupied=True).count()
    reserved_spots = ParkingSpot.objects.filter(is_reserved=True).count()
    total_revenue = sum(float(log.total_revenue) for log in logistics)
    
    # Pagination
    paginator = Paginator(logistics, 10)
    page = request.GET.get('page')
    logistics = paginator.get_page(page)
    
    context = {
        'logistics': logistics,
        'total_spots': total_spots,
        'occupied_spots': occupied_spots,
        'reserved_spots': reserved_spots,
        'total_revenue': total_revenue,
        'dates': json.dumps(dates),
        'occupied_spots_data': json.dumps(occupied_spots_data),
        'reserved_spots_data': json.dumps(reserved_spots_data),
        'revenue_data': json.dumps(revenue_data),
    }
    
    return render(request, 'park/admin/logistics.html', context)

@login_required(login_url='login')
def admin_summaries(request):
    if not request.user.is_staff:
        return redirect('dashboard')
    
    # Get filter parameters
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')
    
    # Base queryset
    summaries = Summary.objects.all().order_by('-start_date')
    
    # Apply filters
    if start_date:
        summaries = summaries.filter(start_date__gte=start_date)
    if end_date:
        summaries = summaries.filter(end_date__lte=end_date)
    
    # Get data for charts
    periods = [summary.period for summary in summaries[:7]]
    occupancy_data = [summary.total_occupancy for summary in summaries[:7]]
    revenue_data = [float(summary.total_revenue) for summary in summaries[:7]]
    
    # Calculate totals
    total_spots = ParkingSpot.objects.count()
    total_occupancy = sum(summary.total_occupancy for summary in summaries) / len(summaries) if summaries else 0
    total_reservations = sum(summary.total_reservations for summary in summaries)
    total_revenue = sum(float(summary.total_revenue) for summary in summaries)
    
    # Pagination
    paginator = Paginator(summaries, 10)
    page = request.GET.get('page')
    summaries = paginator.get_page(page)
    
    context = {
        'summaries': summaries,
        'total_spots': total_spots,
        'total_occupancy': round(total_occupancy, 2),
        'total_reservations': total_reservations,
        'total_revenue': total_revenue,
        'periods': json.dumps(periods),
        'occupancy_data': json.dumps(occupancy_data),
        'revenue_data': json.dumps(revenue_data),
    }
    
    return render(request, 'park/admin/summaries.html', context)

@login_required(login_url='login')
def admin_users(request):
    if not request.user.is_staff:
        return redirect('dashboard')
    
    # Get filter parameters
    status = request.GET.get('status')
    verified = request.GET.get('verified')
    search = request.GET.get('search')
    
    # Base queryset
    users = User.objects.all().order_by('-date_joined')
    
    # Apply filters
    if status == 'active':
        users = users.filter(is_active=True)
    elif status == 'inactive':
        users = users.filter(is_active=False)
    
    if verified == 'true':
        users = users.filter(profile__is_verified=True)
    elif verified == 'false':
        users = users.filter(profile__is_verified=False)
    
    if search:
        users = users.filter(
            Q(username__icontains=search) |
            Q(email__icontains=search)
        )
    
    # Pagination
    paginator = Paginator(users, 10)
    page = request.GET.get('page')
    users = paginator.get_page(page)
    
    context = {
        'users': users,
    }
    
    return render(request, 'park/admin/users.html', context)

# @login_required(login_url='login')
# def admin_settings(request):
#     if not request.user.is_staff:
#         return redirect('dashboard')
    
#     if request.method == 'POST':
#         # Update settings
#         settings = get_object_or_404(Settings, id=1)
        
#         # Parking settings
#         settings.base_hourly_rate = request.POST.get('base_hourly_rate')
#         settings.overtime_rate_multiplier = request.POST.get('overtime_rate_multiplier')
#         settings.max_daily_rate = request.POST.get('max_daily_rate')
#         settings.grace_period = request.POST.get('grace_period')
        
#         # Reservation settings
#         settings.max_reservation_duration = request.POST.get('max_reservation_duration')
#         settings.min_notice_period = request.POST.get('min_notice_period')
#         settings.max_advance_booking = request.POST.get('max_advance_booking')
#         settings.cancellation_window = request.POST.get('cancellation_window')
        
#         # Notification settings
#         settings.expiration_warning = request.POST.get('expiration_warning')
#         settings.overtime_warning = request.POST.get('overtime_warning')
#         settings.enable_email_notifications = 'enable_email_notifications' in request.POST
#         settings.enable_sms_notifications = 'enable_sms_notifications' in request.POST
        
#         # System settings
#         settings.maintenance_mode = 'maintenance_mode' in request.POST
#         settings.enable_auto_logistics = 'enable_auto_logistics' in request.POST
#         settings.enable_auto_summary = 'enable_auto_summary' in request.POST
#         settings.summary_period = request.POST.get('summary_period')
        
#         settings.save()
#         messages.success(request, 'Settings updated successfully.')
#         return redirect('admin_settings')
    
#     # Get current settings
#     settings = get_object_or_404(Settings, id=1)
    
#     context = {
#         'settings': settings,
#     }
    
#     return render(request, 'park/admin/settings.html', context)

@login_required(login_url='login')
def admin_reservation_detail(request, reservation_id):
    if not request.user.is_staff:
        return redirect('dashboard')
    
    reservation = get_object_or_404(Reservation, id=reservation_id)
    context = {
        'reservation': reservation,
    }
    return render(request, 'park/admin/reservation_detail.html', context)

@login_required(login_url='login')
def download_reservation_pdf(request, reservation_id):
    # Get the reservation
    reservation = get_object_or_404(Reservation, id=reservation_id, user=request.user)
    
    # Set timezone to Asia/Manila
    manila_tz = pytz.timezone('Asia/Manila')
    current_time = localtime(now(), manila_tz)
    
    # Create a BytesIO buffer to receive the PDF data
    buffer = BytesIO()
    
    # Create the PDF object, using the buffer as its "file"
    doc = SimpleDocTemplate(buffer, pagesize=letter, rightMargin=72, leftMargin=72, topMargin=72, bottomMargin=72)
    
    # Container for the 'Flowable' objects
    elements = []
    
    # Styles
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        spaceAfter=30,
        alignment=1  # Center alignment
    )
    heading_style = ParagraphStyle(
        'CustomHeading',
        parent=styles['Heading2'],
        fontSize=16,
        spaceAfter=12
    )
    normal_style = ParagraphStyle(
        'CustomNormal',
        parent=styles['Normal'],
        fontSize=12,
        spaceAfter=8
    )
    
    # Add content
    elements.append(Paragraph("Parking Reservation Details", title_style))
    elements.append(Spacer(1, 20))
    
    # Add QR code if it exists
    if reservation.qr:
        try:
            qr_path = reservation.qr.path
            img = Image(qr_path, width=2*inch, height=2*inch)
            elements.append(img)
            elements.append(Spacer(1, 20))
        except:
            pass  # Skip if QR code can't be loaded
    
    # Reservation Information
    elements.append(Paragraph("Reservation Information", heading_style))
    elements.append(Paragraph(f"Reference Number: {reservation.reference_number}", normal_style))
    elements.append(Paragraph(f"Status: {reservation.status.title()}", normal_style))
    elements.append(Paragraph(f"Parking Spot: {reservation.spot.name} (Spot Number: {reservation.spot.spot_number})", normal_style))
    elements.append(Paragraph(f"Plate Number: {reservation.plate_number}", normal_style))
    
    # Convert times to Manila timezone
    start_time = reservation.start_time.astimezone(manila_tz)
    end_time = reservation.end_time.astimezone(manila_tz)
    
    elements.append(Paragraph(f"Start Time: {start_time.strftime('%B %d, %Y %I:%M %p')}", normal_style))
    elements.append(Paragraph(f"End Time: {end_time.strftime('%B %d, %Y %I:%M %p')}", normal_style))
    elements.append(Paragraph(f"User: {reservation.user.username}", normal_style))
    
    # Add footer
    elements.append(Spacer(1, 30))
    footer_style = ParagraphStyle(
        'Footer',
        parent=styles['Normal'],
        fontSize=10,
        textColor=colors.gray,
        alignment=1  # Center alignment
    )
    elements.append(Paragraph("This is an official document from the parking system.", footer_style))
    elements.append(Paragraph(f"Generated on: {current_time.strftime('%B %d, %Y %I:%M %p')}", footer_style))
    
    # Build the PDF
    doc.build(elements)
    
    # Get the value of the BytesIO buffer
    pdf = buffer.getvalue()
    buffer.close()
    
    # Create the HTTP response
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="reservation_{reservation.id}.pdf"'
    response.write(pdf)
    
    return response