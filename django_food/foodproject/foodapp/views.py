from django.views.generic import ListView
from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from .models import City, Dish, Restaurant, Reservation
from .forms import DishFilterForm, CurrencyConverterForm, ReservationForm
from decimal import Decimal
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.db.models import Count


def index(request):
    return render(request, 'foodapp/page_main.html')

def accueil(request):
    featured_dishes = Dish.objects.all().order_by('?')[:5]
    dishes = Dish.objects.all().order_by('-id')[:8]
    cities = City.objects.all()[:4]
    context = {
        'featured_dishes': featured_dishes,
        'dishes': dishes,
        'cities': cities,
    }
    return render(request, 'foodapp/accueil.html', context)

class CityListView(ListView):
    model = City
    template_name = 'foodapp/city_list.html'
    context_object_name = 'cities'

def dish_list(request):
    form = DishFilterForm(request.GET or None)
    dishes = Dish.objects.all()
    selected_city = None

    if form.is_valid():
        if form.cleaned_data.get('city'):
            selected_city = City.objects.get(id=form.cleaned_data['city'].id)
            dishes = dishes.filter(city=selected_city)
        if form.cleaned_data.get('type'):
            dishes = dishes.filter(type=form.cleaned_data['type'])
        if form.cleaned_data.get('is_vegetarian'):
            dishes = dishes.filter(is_vegetarian=True)
        if form.cleaned_data.get('is_vegan'):
            dishes = dishes.filter(is_vegan=True)
        if form.cleaned_data.get('price_range'):
            dishes = dishes.filter(price_range__in=form.cleaned_data['price_range'])

        # Filtrer les plats selon les restrictions de santé
        if form.cleaned_data.get('bad_for_cholesterol'):  # Si l'utilisateur a des problèmes de cholestérol
            dishes = dishes.filter(bad_for_cholesterol=False)  # Garder uniquement les plats sûrs
        if form.cleaned_data.get('bad_for_sugar'):  # Si l'utilisateur est diabétique
            dishes = dishes.filter(bad_for_sugar=False)  # Garder uniquement les plats sûrs
        if form.cleaned_data.get('bad_for_lactose'):  # Si l'utilisateur est intolérant au lactose
            dishes = dishes.filter(bad_for_lactose=False)  # Garder uniquement les plats sûrs

    context = {
        'form': form,
        'dishes': dishes,
        'selected_city': selected_city
    }
    return render(request, 'foodapp/dish_list.html', context)


def restaurants(request):
    restaurants = Restaurant.objects.all()
    cities = City.objects.all()
    
    # Filtrer par ville si spécifié
    city_id = request.GET.get('city')
    if city_id:
        restaurants = restaurants.filter(city_id=city_id)
    
    # Filtrer par statut (ouvert/fermé) si spécifié
    status = request.GET.get('status')
    if status:
        is_open = status == 'open'
        restaurants = restaurants.filter(is_open=is_open)
    
    # Rechercher par nom si spécifié
    search = request.GET.get('search')
    if search:
        restaurants = restaurants.filter(name__icontains=search)
    
    context = {
        'restaurants': restaurants,
        'cities': cities
    }
    return render(request, 'foodapp/modern_restaurants.html', context)

def get_dishes(request):
    dishes = Dish.objects.all()
    data = []
    for dish in dishes:
        data.append({
            'id': dish.id,
            'name': dish.name,
            'description': dish.description,
            'price': dish.price,
            'image': dish.image.url if dish.image else '',
            'city': {
                'id': dish.city.id,
                'name': dish.city.name
            }
        })
    return JsonResponse(data, safe=False)

@csrf_exempt
def dish_detail(request, dish_id):
    dish = get_object_or_404(Dish, id=dish_id)
    return render(request, 'foodapp/dish_detail.html', {
        'dish': dish
    })

def currency_converter(request):
    result = None
    rates = {
        'USD': Decimal('10.20'),  # Dollar américain
        'EUR': Decimal('11.10'),  # Euro
        'GBP': Decimal('12.90'),  # Livre sterling
        'CAD': Decimal('7.50'),   # Dollar canadien
        'AED': Decimal('2.78'),   # Dirham émirati
        'CHF': Decimal('11.45'),  # Franc suisse
        'JPY': Decimal('0.069'),  # Yen japonais
        'CNY': Decimal('1.41'),   # Yuan chinois
        'SAR': Decimal('2.72'),   # Riyal saoudien
    }
    
    form = CurrencyConverterForm(request.GET or None)
    if form.is_valid():
        amount = form.cleaned_data['amount']
        from_currency = form.cleaned_data['from_currency']
        result = amount * rates[from_currency]

    return render(request, 'foodapp/currency_converter.html', {
        'form': form,
        'result': result,
        'rates': rates
    })

def restaurant_detail(request, restaurant_id):
    restaurant = get_object_or_404(Restaurant, id=restaurant_id)
    city_dishes = Dish.objects.filter(city=restaurant.city).order_by('-id')[:6]
    
    context = {
        'restaurant': restaurant,
        'city_dishes': city_dishes,
    }
    
    return render(request, 'foodapp/restaurant_detail.html', context)

def reservation(request, restaurant_id):
    restaurant = get_object_or_404(Restaurant, id=restaurant_id)
    success = False
    reservation = None
    
    if request.method == 'POST':
        form = ReservationForm(request.POST)
        if form.is_valid():
            reservation = form.save(commit=False)
            reservation.restaurant = restaurant
            if request.user.is_authenticated:
                reservation.user = request.user
            reservation.save()
            success = True
    else:
        initial_data = {}
        if request.user.is_authenticated:
            initial_data = {
                'name': request.user.get_full_name(),
                'email': request.user.email
            }
        form = ReservationForm(initial=initial_data)
    
    context = {
        'restaurant': restaurant,
        'form': form,
        'success': success,
        'reservation': reservation
    }
    
    return render(request, 'foodapp/reservation.html', context)

@login_required
def dashboard(request):
    # Statistics
    restaurants_count = Restaurant.objects.count()
    active_restaurants_count = Restaurant.objects.filter(is_open=True).count()
    dishes_count = Dish.objects.count()
    vegetarian_dishes_count = Dish.objects.filter(is_vegetarian=True).count()
    cities_count = City.objects.count()
    users_count = User.objects.count()
    staff_count = User.objects.filter(is_staff=True).count()
    
    # Dish type counts
    sweet_dishes_count = Dish.objects.filter(type='sweet').count()
    salty_dishes_count = Dish.objects.filter(type='salty').count()
    drink_dishes_count = Dish.objects.filter(type='drink').count()
    
    # Latest data
    latest_restaurants = Restaurant.objects.all().order_by('-created_at')[:5]
    latest_dishes = Dish.objects.all().order_by('-id')[:5]
    
    # All cities for charts
    cities = City.objects.all()
    
    context = {
        'restaurants_count': restaurants_count,
        'active_restaurants_count': active_restaurants_count,
        'dishes_count': dishes_count,
        'vegetarian_dishes_count': vegetarian_dishes_count,
        'cities_count': cities_count,
        'users_count': users_count,
        'staff_count': staff_count,
        'sweet_dishes_count': sweet_dishes_count,
        'salty_dishes_count': salty_dishes_count,
        'drink_dishes_count': drink_dishes_count,
        'latest_restaurants': latest_restaurants,
        'latest_dishes': latest_dishes,
        'cities': cities,
    }
    
    return render(request, 'foodapp/dashboard.html', context)
