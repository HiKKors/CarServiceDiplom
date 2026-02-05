from django_filters import CharFilter, FilterSet, DateFilter
from .models import AutoService, Booking

import csv



class ServiceFilterForm(FilterSet):
    address = CharFilter(label = 'Город', method='filter_by_city')
    name = CharFilter(label="Название", lookup_expr='icontains')
    class Meta:
        model = AutoService
        fields = []
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.cities = []
        with open('city.csv', 'r') as f:
            reader = csv.DictReader(f)
            for row in reader:
                self.cities.append(row['city'])
        
        # self.filters['address'].extra['choices'] = [(city, city) for city  in self.cities]

    def filter_by_city(self, queryset, name, value):
        if value:
            return queryset.filter(address__icontains=value)
        return queryset
    

class AllBookingsFilterForm(FilterSet):
    service_id = CharFilter(label="Название", lookup_expr='icontains', field_name='service_id__name')
    date = CharFilter(label='Дата', lookup_expr='exact')
    
    class Meta:
        model = Booking
        fields = []
    