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
from django.utils.timezone import now
from .models import *
from django.contrib.auth.models import User
from django.db.models import Q

import qrcode
import qrcode.image.svg
from io import BytesIO
from django.core.files.base import ContentFile

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
            form = CreateUserForm(request.POST)
            if form.is_valid():
                form.save()
                user = form.cleaned_data.get('username')
            
                system_messages = messages.get_messages(request)
                for message in system_messages:
                    # This iteration is necessary
                    pass


                messages.success(request, "Account Created For " + user)
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
    return render(request, 'park/reservations.html', {'reservations': reservations})

@login_required(login_url='login')
def reserve_spot(request):
    if request.method == 'POST':
        spot_id = request.POST['spot_id']
        start_time = request.POST['start_time']
        end_time = request.POST['end_time']

        spot = get_object_or_404(ParkingSpot, id=spot_id)
        if spot.is_reserved or spot.is_occupied:
            return JsonResponse({'error': 'Spot is already reserved or occupied'}, status=400)

        reservation = Reservation.objects.create(
            user=request.user,
            spot=spot,
            start_time=start_time,
            end_time=end_time
        )
        spot.is_reserved = True
        spot.save()

        # Generate QR code
        qr_data = f"Reservation ID: {reservation.id}\nUser: {request.user.username}\nSpot: {spot.spot_number}\nStart: {start_time}\nEnd: {end_time}"
        qr = qrcode.make(qr_data)
        buffer = BytesIO()
        qr.save(buffer, format="PNG")
        reservation_qr = Parked.objects.create(
            user=request.user,
            spot=spot,
            start_time=start_time,
            end_time=end_time,
            is_active=True
        )
        reservation_qr.qr.save(f"qr_{reservation.id}.png", ContentFile(buffer.getvalue()), save=True)

        return redirect('reservations')

    spots = ParkingSpot.objects.filter(is_reserved=False, is_occupied=False)
    return render(request, 'park/reserve_spot.html', {'spots': spots})

@login_required(login_url='login')
def cancel_reservation(request, reservation_id):
    reservation = get_object_or_404(Reservation, id=reservation_id, user=request.user)
    reservation.spot.is_reserved = False
    reservation.spot.save()
    reservation.delete()
    return redirect('reservations')

# Parked vehicle views
@login_required(login_url='login')
def parked_vehicles(request):
    parked = Parked.objects.filter(user=request.user, is_active=True)
    return render(request, 'parked_vehicles.html', {'parked': parked})

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
