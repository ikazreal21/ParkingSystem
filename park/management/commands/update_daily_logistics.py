from django.core.management.base import BaseCommand
from django.utils import timezone
from park.models import ParkingSpot, Parked, Logistics
from decimal import Decimal
import pytz
import logging

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Updates daily logistics data for the parking system'

    def handle(self, *args, **options):
        try:
            # Use Manila timezone
            manila_tz = pytz.timezone('Asia/Manila')
            today = timezone.now().astimezone(manila_tz).date()
            
            self.stdout.write(f"Updating logistics for {today}")
            
            # Get or create today's logistics record
            logistics, created = Logistics.objects.get_or_create(date=today)
            self.stdout.write(f"Logistics record {'created' if created else 'updated'}")
            
            # Update total spots
            logistics.total_spots = ParkingSpot.objects.count()
            
            # Update occupied spots
            logistics.occupied_spots = ParkingSpot.objects.filter(is_occupied=True).count()
            
            # Update reserved spots
            logistics.reserved_spots = ParkingSpot.objects.filter(is_reserved=True).count()
            
            # Update available spots
            logistics.available_spots = logistics.total_spots - logistics.occupied_spots - logistics.reserved_spots
            
            # Calculate today's revenue
            today_parked = Parked.objects.filter(
                start_time__date=today,
                is_active=True
            )
            
            total_revenue = Decimal('0.00')
            exceeded_hours = 0
            
            for parked in today_parked:
                # Add parking fee to total revenue
                if hasattr(parked, 'parking_fee'):
                    total_revenue += parked.parking_fee
                else:
                    # Calculate fee if not set (50 pesos per hour)
                    rate_per_hour = Decimal('50.00')
                    if parked.exceeded_hours > 0:
                        total_revenue += rate_per_hour * Decimal(str(parked.exceeded_hours))
                
                # Count exceeded hours
                if parked.exceeded_hours > 0:
                    exceeded_hours += parked.exceeded_hours
            
            logistics.total_revenue = total_revenue
            logistics.exceeded_hours = exceeded_hours
            
            logistics.save()
            self.stdout.write(self.style.SUCCESS(f"Successfully updated logistics for {today}"))
            
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Error updating logistics: {str(e)}"))
            raise 