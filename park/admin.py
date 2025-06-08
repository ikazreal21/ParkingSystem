from django.contrib import admin
from .models import *
from django.contrib.auth.admin import UserAdmin
from django.forms import TextInput, Textarea, CharField
from django import forms
from django.db import models
from django.contrib.auth.models import Group
from admin_interface.models import Theme
from django.utils.html import format_html
from django.urls import reverse
from django.utils import timezone
from datetime import datetime, timedelta
import json
import pytz

admin.site.unregister(Group)
# admin.site.unregister(Theme)

class CustomAdminSite(admin.AdminSite):
    site_header = "TCT Parking Administration"
    site_title = "TCT Parking Admin Portal"
    index_title = "Welcome to TCT Parking Admin Portal"

admin_site = CustomAdminSite(name='admin')

class ParkingSpotAdmin(admin.ModelAdmin):
    list_display = ('name', 'spot_number', 'is_reserved', 'is_occupied', 'is_handicapped', 'is_charging', 'is_vip')
    list_filter = ('is_reserved', 'is_occupied', 'is_handicapped', 'is_charging', 'is_vip')
    search_fields = ('name', 'spot_number')
    ordering = ('spot_number',)

class ReservationAdmin(admin.ModelAdmin):
    list_display = ('user', 'spot', 'reference_number', 'start_time', 'end_time', 'status', 'is_active')
    list_filter = ('status', 'is_active', 'start_time', 'end_time')
    search_fields = ('user__username', 'spot__name', 'reference_number')
    date_hierarchy = 'start_time'

class ParkedAdmin(admin.ModelAdmin):
    list_display = ('user', 'spot', 'start_time', 'end_time', 'is_active', 'exceeded_hours')
    list_filter = ('is_active', 'start_time', 'end_time')
    search_fields = ('user__username', 'spot__name')
    date_hierarchy = 'start_time'

class ProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'first_name', 'last_name', 'email', 'is_verified', 'is_first_time')
    list_filter = ('is_verified', 'is_first_time')
    search_fields = ('user__username', 'first_name', 'last_name', 'email')

class LogisticsAdmin(admin.ModelAdmin):
    list_display = ('date', 'total_spots', 'occupied_spots', 'reserved_spots', 'available_spots', 'total_revenue', 'exceeded_hours')
    list_filter = ('date',)
    date_hierarchy = 'date'
    ordering = ('-date',)
    change_list_template = 'admin/park/logistics/change_list.html'

    def changelist_view(self, request, extra_context=None):
        # Get the last 7 days of logistics data
        manila_tz = pytz.timezone('Asia/Manila')
        end_date = timezone.now().astimezone(manila_tz).date()
        start_date = end_date - timedelta(days=7)
        print(f"Fetching logistics data from {start_date} to {end_date}")
        logistics_data = Logistics.objects.filter(
            date__range=[start_date, end_date]
        ).order_by('date')

        # Prepare data for charts
        chart_data = []
        for log in logistics_data:
            chart_data.append({
                'date': log.date.strftime('%Y-%m-%d'),
                'total_spots': log.total_spots,
                'occupied_spots': log.occupied_spots,
                'reserved_spots': log.reserved_spots,
                'available_spots': log.available_spots,
                'total_revenue': float(log.total_revenue),
                'exceeded_hours': log.exceeded_hours
            })

        extra_context = extra_context or {}
        extra_context['logistics_data'] = json.dumps(chart_data)
        
        return super().changelist_view(request, extra_context=extra_context)

class SummaryAdmin(admin.ModelAdmin):
    list_display = ('period_type', 'start_date', 'end_date', 'total_spots', 'total_occupancy', 'total_reservations', 'total_revenue', 'total_exceeded_hours')
    list_filter = ('period_type', 'start_date', 'end_date')
    date_hierarchy = 'start_date'
    ordering = ('-start_date',)

# Register models with custom admin site
admin_site.register(ParkingSpot, ParkingSpotAdmin)
admin_site.register(Reservation, ReservationAdmin)
admin_site.register(Parked, ParkedAdmin)
admin_site.register(Profile, ProfileAdmin)
admin_site.register(Logistics, LogisticsAdmin)
admin_site.register(Summary, SummaryAdmin)

# Custom admin site settings
admin_site.site_header = "TCT Parking Admin"
admin_site.site_title = "TCT Parking Admin Portal"
admin_site.index_title = "Welcome to TCT Parking Admin Portal"
