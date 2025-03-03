from django.db import models
from django.contrib.auth.models import User
from django.contrib.auth.models import AbstractUser
import locale
import uuid
from django.utils.timezone import now
from django.core.files.storage import FileSystemStorage
from django.db import models


class ParkingSpot(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    spot_number = models.IntegerField()
    name = models.CharField(max_length=255)
    is_reserved = models.BooleanField(default=False)
    is_occupied = models.BooleanField(default=False)
    is_handicapped = models.BooleanField(default=False)
    is_charging = models.BooleanField(default=False)
    is_vip = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.name} - {str(self.spot_number)}"
    
    def get_spot_number(self):
        return self.spot_number

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
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    
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

    
class Parked(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    spot = models.ForeignKey(ParkingSpot, on_delete=models.CASCADE)
    start_time = models.DateTimeField(blank=True, null=True)
    end_time = models.DateTimeField(blank=True, null=True)
    is_active = models.BooleanField(default=True)
    qr = models.ImageField(upload_to='qr_codes', blank=True)

    def __str__(self):
        return str(self.user) + " " + str(self.spot) + " " + str(self.start_time) + " " + str(self.end_time)

    class Meta:
        verbose_name_plural = "Parked"