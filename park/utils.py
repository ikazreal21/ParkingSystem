from django.conf import settings
from django.core.mail import send_mail


def test_send(subject, message, recipients):
	send_mail(
    		subject=subject,
    		message=message,
    		from_email=settings.DEFAULT_FROM_EMAIL,
    		recipient_list=recipients)

def send_email(subject, message, recipients):
	send_mail(
    		subject=subject,
    		message='',
    		from_email=settings.DEFAULT_FROM_EMAIL,
    		recipient_list=recipients,
			html_message=message
			)

def contact_us(message, sender):
	send_mail(
    		subject="Contact Us",
    		message=message,
    		from_email=sender,
    		recipient_list=list(settings.EMAIL_HOST_USER))


def send_parking_notification(user_email, user_name, reservation_time, parking_spot):
    reservation_time = reservation_time.strftime('%B %d, %Y at %I:%M %p')

    # Subject of the email
    subject = 'Parking Reminder: Your Reservation Time is Approaching'
    
    # Message body
    message = f"""
    Dear {user_name},

    This is a friendly reminder that your parking reservation is approaching.

    **Reservation Details:**
    - **Time:** {reservation_time}
    - **Parking Spot:** {parking_spot}

    Please ensure you arrive on time to avoid any inconvenience. If you need to modify your reservation, you can do so through our system.

    Safe travels, and thank you for choosing our parking service!

    Best regards,  
    TCT Parking System
    """

    # Sender's email (configured in Django settings)
    from_email = settings.DEFAULT_FROM_EMAIL

    # Send the email
    send_mail(
        subject,          # Subject
        message,          # Message
        from_email,       # From
        [user_email],     # To
        fail_silently=False
    )


def send_parking_end_notification(user_email, user_name, reservation_end_time, parking_spot):
    reservation_end_time = reservation_end_time.strftime('%B %d, %Y at %I:%M %p')
    # Subject of the email
    subject = 'Parking Reminder: Your Reservation is Ending Soon'
    
    # Message body
    message = f"""
    Dear {user_name},

    This is a reminder that your parking reservation is nearing its end.

    **Reservation Details:**
    - **End Time:** {reservation_end_time}
    - **Parking Spot:** {parking_spot}

    Please ensure you vacate the parking spot on time to avoid any penalties or inconvenience to other users. If you need an extension, please check availability through our system.

    Thank you for using our parking service!

    Best regards,  
    TCT Parking System
    """

    # Sender's email (configured in Django settings)
    from_email = settings.DEFAULT_FROM_EMAIL

    # Send the email
    send_mail(
        subject,          # Subject
        message,          # Message
        from_email,       # From
        [user_email],     # To
        fail_silently=False
    )
