from celery import shared_task
from django.utils.timezone import now
from datetime import timedelta
from django.conf import settings
from park.models import Reservation
from .utils import *



@shared_task
def send_start_reservation_reminders():
    current_time = now()

    reservations = Reservation.objects.filter(
        start_time__gte=current_time + timedelta(hours=1),
        start_time__lt=current_time + timedelta(hours=1, minutes=5),
        status="pending"
    )

    for reservation in reservations:
        send_parking_notification(
            reservation.user.email, 
            reservation.user.username,
            reservation.start_time.replace(tzinfo=None),
            reservation.spot.name)
    return "Reservation start reminders sent"

@shared_task
def send_end_reservation_reminders():
    current_time = now()

    end_reminders = Reservation.objects.filter(
            end_time__gte=current_time + timedelta(hours=1),
            end_time__lt=current_time + timedelta(hours=1, minutes=5),
            status="pending"
    )

    for reservation in end_reminders:
        send_parking_end_notification(
            reservation.user.email, 
            reservation.user.username,
            reservation.end_time.replace(tzinfo=None),
            reservation.spot.name
        )
    return "Reservation end reminders sent"