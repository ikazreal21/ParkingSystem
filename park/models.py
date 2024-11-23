from django.db import models
from django.contrib.auth.models import User
from django.contrib.auth.models import AbstractUser
import locale
import uuid

from django.core.files.storage import FileSystemStorage
from django.db import models


class ParkingSpot(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    spot_number = models.IntegerField()
    is_reserved = models.BooleanField(default=False)
    is_occupied = models.BooleanField(default=False)
    is_handicapped = models.BooleanField(default=False)
    is_charging = models.BooleanField(default=False)
    is_vip = models.BooleanField(default=False)

    def __str__(self):
        return str(self.spot_number)
    
    def get_spot_number(self):
        return self.spot_number


class Reservation(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    spot = models.ForeignKey(ParkingSpot, on_delete=models.CASCADE)
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return str(self.user) + " " + str(self.spot) + " " + str(self.start_time) + " " + str(self.end_time)
    
class Parked(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    spot = models.ForeignKey(ParkingSpot, on_delete=models.CASCADE)
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    is_active = models.BooleanField(default=True)
    qr = models.ImageField(upload_to='qr_codes', blank=True)

    def __str__(self):
        return str(self.user) + " " + str(self.spot) + " " + str(self.start_time) + " " + str(self.end_time)