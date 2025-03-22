from celery import shared_task
from django.utils.timezone import now, localtime
from datetime import timedelta
from django.conf import settings
from park.models import Reservation
from .utils import *
import pytz


@shared_task
def send_start_reservation_reminders():
    return_json = {}

    user_timezone = pytz.timezone('Asia/Manila')
    current_time = localtime(now(), user_timezone).replace(tzinfo=None)

    reservations = Reservation.objects.filter(
        start_time__gte=current_time + timedelta(hours=1),
        start_time__lt=current_time + timedelta(hours=1, minutes=5),
        status="pending"
    )
    print("reservations", reservations)
    print("current_time + timedelta(hours=1)", current_time + timedelta(hours=1))
    print("current_time + timedelta(hours=1, minutes=5)", current_time + timedelta(hours=1, minutes=5))

    reservation_len = len(reservations)

    for reservation in reservations:
        send_parking_notification(
            reservation.user.email, 
            reservation.user.username,
            reservation.get_local_start_time().replace(tzinfo=None),
            reservation.spot.name)

    return_json["reservation_len"] = reservation_len
    return_json["current_time_timedelta1hr"] = current_time + timedelta(hours=1)
    return_json["current_time_timedelta1hr5min"] = current_time + timedelta(hours=1, minutes=5)
    
    return return_json

@shared_task
def send_end_reservation_reminders():
    return_json = {}

    user_timezone = pytz.timezone('Asia/Manila')
    current_time = localtime(now(), user_timezone).replace(tzinfo=None)

    end_reminders = Reservation.objects.filter(
            end_time__gte=current_time + timedelta(hours=1),
            end_time__lt=current_time + timedelta(hours=1, minutes=5),
            status="parked"
    )

    reservation_len = len(end_reminders)

    for reservation in end_reminders:
        send_parking_end_notification(
            reservation.user.email, 
            reservation.user.username,
            reservation.get_local_end_time().replace(tzinfo=None),
            reservation.spot.name
        )

    return_json["reservation_len"] = reservation_len
    return_json["current_time_timedelta1hr"] = current_time + timedelta(hours=1)
    return_json["current_time_timedelta1hr5min"] = current_time + timedelta(hours=1, minutes=5)
    
    return return_json