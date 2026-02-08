from .models import Booking
from django.utils import timezone

def user_bookings(request):
    if request.user.is_authenticated and not request.user.is_admin:
        active_bookings = Booking.objects.filter(
            user_id = request.user.id
        ).filter(status__in = ['pending', 'active']).exists()
    else:
        active_bookings = False
    
    return {
        'active_bookings': active_bookings
    }