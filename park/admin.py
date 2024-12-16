from django.contrib import admin
from .models import *
from django.contrib.auth.admin import UserAdmin
from django.forms import TextInput, Textarea, CharField
from django import forms
from django.db import models
from django.contrib.auth.models import Group
from admin_interface.models import Theme


admin.site.unregister(Group)
# admin.site.unregister(Theme)
admin.site.register(ParkingSpot)
admin.site.register(Reservation)
admin.site.register(Parked)



admin.site.site_title = "Victory Mall Parking Admin"
admin.site.site_header = "Victory Mall Parking Admin"