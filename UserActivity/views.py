
from django.shortcuts import get_object_or_404, render, redirect, get_list_or_404
from django.contrib.auth import logout
from django.urls import reverse_lazy
from django.views.generic.list import ListView
from django.views.generic.detail import DetailView
from django.views.generic.edit import DeleteView
from django.views import View

from .models import UserCar
from autoService.models import Booking
from accounts.models import Client

from .forms import UserCarForm
import logging

logging.basicConfig(
    level=logging.DEBUG,
    format='[%(asctime)s] #%(levelname)-8s %(filename)s:'
           '%(lineno)d - %(name)s - %(message)s'
)

logger = logging.getLogger(__name__)

def add_user_car(request):
    print(request.user)
    if request.method == 'POST':
        form = UserCarForm(request.POST)
        if form.is_valid():
            user_car = form.save(commit=False)
            user_car.user = request.user
            user_car.save()
            
            return redirect('garage')
    else:
        form = UserCarForm()
            
    return render(request, 'UserActivity/add-user-car.html', {'form': form})

class UserGarageVeiw(ListView):
    queryset = UserCar.objects.all()
    template_name = 'UserActivity/garage.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        user_cars = UserCar.objects.filter(user=self.request.user.id)
        
        context['user_cars'] = user_cars    
        
        return context
    
class CustomLogoutView(View):
    def get(self, request):
        logout(request)
        return redirect('login')
    
class UserBookingsView(ListView):
    queryset = Booking.objects.all()
    template_name = 'UserActivity/client-bookings.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user_bookings = Booking.objects.filter(user_id=self.request.user.id)
        
        context['user_bookings'] = user_bookings
        return context
    
class Profile(DetailView):
    model = Client
    context_object_name = 'client'
    template_name = 'UserActivity/profile.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        client_data = self.request.user
        context['client_data'] = client_data
        
        return context
    

    
class ClientDeleteBookingsView(DeleteView):
    model = Booking
    success_url = reverse_lazy('my_bookings')