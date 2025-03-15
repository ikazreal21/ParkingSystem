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
        return redirect('dashboard')
    else:
        if request.method == "POST":
            username = request.POST.get("username")
            password = request.POST.get("password")
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
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
    reservations = Reservation.objects.filter(user=request.user)
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
    return redirect('reserved')

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
    parked = Reservation.objects.filter(user=request.user, status="pending")
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
    today = date.today()
    month = int(request.GET.get('month', today.month))
    year = int(request.GET.get('year', today.year))
    start_day = date(year, month, 1)
    days_in_month = monthrange(year, month)[1]
    reservations = Reservation.objects.filter(start_time__date__year=year, start_time__date__month=month)
    reserved_dates = {res.start_time.date() for res in reservations}
    first_weekday = start_day.weekday()
    calendar_days = []
    # Fill in the empty days at the start of the month
    for _ in range(first_weekday):
        calendar_days.append(None)
    # Fill in the days of the current month
    for day in range(1, days_in_month + 1):
        calendar_days.append(date(year, month, day))
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
    context = {'reservations': reservations, 'spot': spot_obj}
    return render(request, 'park/reservations_by_spot.html', context)

def scan_to_occupy(request, pk):
    reservation = get_object_or_404(Reservation, id=pk)
    spot = get_object_or_404(ParkingSpot, id=reservation.spot.id)


    
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

    if reservation.get_local_start_time().replace(tzinfo=None) <= current_time <= \
        reservation.get_local_end_time().replace(tzinfo=None):
        if reservation.spot.is_occupied:
            # If already occupied, unoccupy it
            reservation.spot.is_occupied = False
            reservation.spot.is_reserved = False
            reservation.status = "complete"

            parked_user = request.user if request.user and not isinstance(request.user, AnonymousUser) else reservation.user
            parked_user_exist = Parked.objects.filter(user=parked_user, spot=spot, end_time=None, is_active=True).first()

            parked_user_exist.end_time = current_time
            parked_user_exist.is_active = False
            parked_user_exist.save()
            
        else:
            # Otherwise, mark it as occupied
            reservation.spot.is_occupied = True
            reservation.spot.is_reserved = False
            reservation.status = "parked"

            parked_user = request.user if request.user and not isinstance(request.user, AnonymousUser) else reservation.user

            Parked.objects.create(
                user=parked_user,
                spot=spot,
                start_time=current_time,
                end_time=None
            )

        reservation.spot.save()
        reservation.save()
    else:
        return JsonResponse({'error': 'Invalid reservation: not within the reserved time'}, status=400)

    return redirect('dashboard')


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