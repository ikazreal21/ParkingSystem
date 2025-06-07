from django.db import models
from django.contrib.auth.models import User
from django.contrib.auth.models import AbstractUser
import locale
import uuid
from django.utils.timezone import now, localtime
from django.core.files.storage import FileSystemStorage
from django.db import models
import pytz

def create_rand_id():
        from django.utils.crypto import get_random_string
        return get_random_string(length=13, 
            allowed_chars='ABCDEFGHIJKLMNOPQRSTUVWXYZ1234567890')

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    first_name = models.CharField(max_length=255, blank=True, null=True)
    last_name = models.CharField(max_length=255, blank=True, null=True)
    email = models.EmailField(max_length=255, blank=True, null=True)
    verification_code = models.CharField(max_length=255, blank=True, null=True)
    is_verified = models.BooleanField(default=False)
    is_first_time = models.BooleanField(default=True)


    class Meta:
        verbose_name_plural = "Profiles"

    def __str__(self):
        return f"{self.first_name} {self.last_name}"


class ParkingSpot(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    spot_number = models.IntegerField()
    name = models.CharField(max_length=255)
    is_reserved = models.BooleanField(default=False)
    is_occupied = models.BooleanField(default=False)
    is_handicapped = models.BooleanField(default=False)
    is_charging = models.BooleanField(default=False)
    is_vip = models.BooleanField(default=False)
    reservation_end_time = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"{self.name} - {str(self.spot_number)}"
    
    def get_spot_number(self):
        return self.spot_number
    
    def get_local_end_time(self):
        """ Get start_time in Asia/Manila timezone without saving """
        manila_tz = pytz.timezone('Asia/Manila')
        return self.reservation_end_time.astimezone(manila_tz) if self.reservation_end_time else None

    class Meta:
        verbose_name_plural = "Parking Spot"


class Reservation(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('parked', 'Currently Parked'),
        ('complete', 'Complete'),
        ('expired', 'Expired')
    ]

    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    spot = models.ForeignKey(ParkingSpot, on_delete=models.CASCADE)
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    is_active = models.BooleanField(default=True)
    qr = models.ImageField(upload_to='qr_codes', blank=True)
    plate_number = models.CharField(max_length=255)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')

    def get_local_start_time(self):
        """ Get start_time in Asia/Manila timezone without saving """
        manila_tz = pytz.timezone('Asia/Manila')
        return self.start_time.astimezone(manila_tz) if self.start_time else Nones

    def get_local_end_time(self):
        """ Get end_time in Asia/Manila timezone without saving """
        manila_tz = pytz.timezone('Asia/Manila')
        return self.end_time.astimezone(manila_tz) if self.end_time else None
    
    def update_status(self):
        """ Update the status based on the current time """
        current_time = now()
        if self.start_time <= current_time < self.end_time:
            self.status = 'parked'
        elif current_time >= self.end_time:
            self.status = 'expired'
        self.save()

    def __str__(self):
        return str(self.user) + " " + str(self.spot) + " " + str(self.start_time) + " " + str(self.end_time)
    
        
    class Meta:
        verbose_name_plural = "Reservations"
        ordering = ['-start_time']

    
class Parked(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    spot = models.ForeignKey(ParkingSpot, on_delete=models.CASCADE)
    start_time = models.DateTimeField(blank=True, null=True)
    end_time = models.DateTimeField(blank=True, null=True)
    is_active = models.BooleanField(default=True)
    qr = models.ImageField(upload_to='qr_codes', blank=True)
    exceeded_hours = models.FloatField(default=0.0)
    parking_fee = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)

    def __str__(self):
        return str(self.user) + " " + str(self.spot) + " " + str(self.start_time) + " " + str(self.end_time)

    class Meta:
        verbose_name_plural = "Parked"

class Logistics(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    date = models.DateField()
    total_spots = models.IntegerField(default=0)
    occupied_spots = models.IntegerField(default=0)
    reserved_spots = models.IntegerField(default=0)
    available_spots = models.IntegerField(default=0)
    total_revenue = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    exceeded_hours = models.FloatField(default=0.0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = "Logistics"
        ordering = ['-date']

    def __str__(self):
        return f"Logistics for {self.date}"

class Summary(models.Model):
    PERIOD_CHOICES = [
        ('daily', 'Daily'),
        ('weekly', 'Weekly'),
        ('monthly', 'Monthly'),
        ('yearly', 'Yearly'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    period_type = models.CharField(max_length=10, choices=PERIOD_CHOICES)
    start_date = models.DateField()
    end_date = models.DateField()
    total_spots = models.IntegerField(default=0)
    total_occupancy = models.IntegerField(default=0)
    total_reservations = models.IntegerField(default=0)
    total_revenue = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total_exceeded_hours = models.FloatField(default=0.0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = "Summaries"
        ordering = ['-start_date']

    def __str__(self):
        return f"{self.period_type.capitalize()} Summary ({self.start_date} to {self.end_date})"