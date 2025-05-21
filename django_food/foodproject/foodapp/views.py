from django.views.generic import ListView
from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse, HttpResponseForbidden
from .models import City, Dish, Restaurant, Reservation, RestaurantAccount, UserProfile, ForumTopic, ForumMessage
from .forms import DishFilterForm, CurrencyConverterForm, ReservationForm, ReservationModifyForm
from decimal import Decimal
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.db.models import Count, Q, Sum
from django.contrib.auth import authenticate, login, logout
from django.http import JsonResponse
import json
import datetime
from django.urls import reverse
from django.shortcuts import redirect
from django.middleware.csrf import get_token
from django.core.cache import cache
from django.utils import timezone
import time
from django.contrib import messages

try:
    from cpp_modules.food_processor import fast_sort_dishes
    USE_CPP_OPTIMIZATION = True
except ImportError:
    USE_CPP_OPTIMIZATION = False
    print("Module C++ non disponible, utilisation du tri Python standard")

def index(request):
    return redirect('accueil')

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
    dishes = Dish.objects.all()
    sort_by = request.GET.get('sort', 'name')
    city_id = request.GET.get('city')

    if city_id:
        dishes = dishes.filter(city_id=city_id)

    if USE_CPP_OPTIMIZATION:
        # Convertir les plats en format compatible avec le module C++
        dishes_data = [
            {
                'id': dish.id,
                'name': dish.name,
                'price_range': dish.price_range,
                'type': dish.type,
                'city_id': dish.city.id if dish.city else 0
            }
            for dish in dishes
        ]
        
        # Utiliser le tri rapide C++
        sorted_dishes = fast_sort_dishes(dishes_data, sort_by)
        
        # Reconvertir en QuerySet Django
        dish_ids = [dish['id'] for dish in sorted_dishes]
        dishes = Dish.objects.filter(id__in=dish_ids)
        # Préserver l'ordre du tri C++
        dishes = sorted(dishes, key=lambda x: dish_ids.index(x.id))
    else:
        # Tri Python standard
        if sort_by == 'price_asc':
            dishes = dishes.order_by('price_range')
        elif sort_by == 'price_desc':
            dishes = dishes.order_by('-price_range')
        elif sort_by == 'name':
            dishes = dishes.order_by('name')

    context = {
        'dishes': dishes,
        'current_sort': sort_by,
        'cities': City.objects.all(),
        'selected_city': city_id
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
    """
    Vue API optimisée pour renvoyer les plats avec mise en cache
    """
    # Vérifier si les données sont en cache
    cache_key = 'all_dishes_data'
    dishes_data = cache.get(cache_key)
    
    if not dishes_data:
        # Si pas en cache, récupérer depuis la base de données
        start_time = time.time()
        dishes = Dish.objects.select_related('city').all()
        
        # Préparer les données pour la sérialisation JSON
        dishes_data = []
        for dish in dishes:
            dishes_data.append({
                'id': dish.id,
                'name': dish.name,
                'description': dish.description,
                'price_range': dish.price_range,
                'price_display': dish.get_price_range_display(),
                'type': dish.type,
                'type_display': dish.get_type_display(),
                'image': dish.image.url if dish.image else '',
                'is_vegetarian': dish.is_vegetarian,
                'is_vegan': dish.is_vegan,
                'ingredients': dish.ingredients,
                'history': dish.history,
                'preparation_steps': dish.preparation_steps,
                'city': {
                    'id': dish.city.id if dish.city else None,
                    'name': dish.city.name if dish.city else None
                },
                'timestamp': timezone.now().timestamp()  # Ajouter un horodatage pour le suivi
            })
        
        # Mettre en cache pour 10 minutes
        cache.set(cache_key, dishes_data, 60 * 10)
        
        print(f"Database query completed in {time.time() - start_time:.4f} seconds")
    
    return JsonResponse(dishes_data, safe=False)

def get_restaurants(request):
    """
    Vue API pour renvoyer les restaurants avec mise en cache
    """
    # Vérifier si les données sont en cache
    cache_key = 'all_restaurants_data'
    restaurants_data = cache.get(cache_key)
    
    if not restaurants_data:
        # Si pas en cache, récupérer depuis la base de données
        start_time = time.time()
        restaurants = Restaurant.objects.select_related('city').all()
        
        # Préparer les données pour la sérialisation JSON
        restaurants_data = []
        for restaurant in restaurants:
            restaurants_data.append({
                'id': restaurant.id,
                'name': restaurant.name,
                'description': restaurant.description,
                'is_open': restaurant.is_open,
                'address': restaurant.address,
                'phone': restaurant.phone,
                'email': restaurant.email,
                'website': restaurant.website,
                'image': restaurant.image.url if restaurant.image else '',
                'city': {
                    'id': restaurant.city.id,
                    'name': restaurant.city.name
                },
                'timestamp': timezone.now().timestamp()
            })
        
        # Mettre en cache pour 10 minutes
        cache.set(cache_key, restaurants_data, 60 * 10)
        
        print(f"Restaurant query completed in {time.time() - start_time:.4f} seconds")
    
    return JsonResponse(restaurants_data, safe=False)

@csrf_exempt
@login_required
def mark_dish_viewed(request, dish_id):
    """API pour marquer un plat comme vu par l'utilisateur"""
    if request.method == 'POST':
        try:
            dish = get_object_or_404(Dish, id=dish_id)
            dish.mark_as_viewed(request.user)
            return JsonResponse({'success': True})
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)
    return JsonResponse({'error': 'Méthode non autorisée'}, status=405)

def moroccan_cuisine(request):
    """
    Vue spéciale pour montrer les plats marocains aux touristes
    """
    # Récupérer les plats marocains recommandés aux touristes
    recommended_dishes = Dish.objects.filter(origin=Dish.MOROCCAN, is_tourist_recommended=True)
    
    # Tous les plats marocains
    all_moroccan_dishes = Dish.objects.filter(origin=Dish.MOROCCAN)
    
    # Répartir les plats par type
    sweet_dishes = all_moroccan_dishes.filter(type=Dish.SWEET)
    salty_dishes = all_moroccan_dishes.filter(type=Dish.SALTY)
    drinks = all_moroccan_dishes.filter(type=Dish.DRINK)
    
    # Marquer les plats comme nouveaux pour cet utilisateur
    if request.user.is_authenticated:
        for dish in list(recommended_dishes) + list(sweet_dishes) + list(salty_dishes) + list(drinks):
            dish.is_new_for_current_user = dish.is_new_for_user(request.user)
    else:
        for dish in list(recommended_dishes) + list(sweet_dishes) + list(salty_dishes) + list(drinks):
            dish.is_new_for_current_user = dish.is_new()
    
    context = {
        'recommended_dishes': recommended_dishes,
        'sweet_dishes': sweet_dishes,
        'salty_dishes': salty_dishes,
        'drinks': drinks,
        'total_dishes': all_moroccan_dishes.count(),
    }
    
    return render(request, 'foodapp/moroccan_cuisine.html', context)

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
    reservation_obj = None
    
    if request.method == 'POST':
        form = ReservationForm(request.POST)
        if form.is_valid():
            # Vérifier la disponibilité
            date = form.cleaned_data['date']
            time = form.cleaned_data['time']
            guests = form.cleaned_data['guests']
            
            # Vérifier si le créneau est disponible
            if is_slot_available(restaurant, date, time, guests):
                reservation_obj = form.save(commit=False)
                reservation_obj.restaurant = restaurant
                if request.user.is_authenticated:
                    reservation_obj.user = request.user
                reservation_obj.save()
                success = True
            else:
                form.add_error(None, "Désolé, ce créneau n'est plus disponible. Veuillez choisir un autre horaire.")
    else:
        initial_data = {}
        if request.user.is_authenticated:
            initial_data = {
                'name': request.user.get_full_name() or request.user.username,
                'email': request.user.email,
                'phone': getattr(request.user.profile, 'phone', '') if hasattr(request.user, 'profile') else ''
            }
        form = ReservationForm(initial=initial_data)
    
    # Récupérer les créneaux disponibles pour JavaScript
    available_dates = get_available_dates(restaurant)
    
    context = {
        'restaurant': restaurant,
        'form': form,
        'success': success,
        'reservation': reservation_obj,
        'available_dates': json.dumps([date.strftime('%Y-%m-%d') for date in available_dates])
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

@csrf_exempt
def signup_view(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            username = data.get('username')
            email = data.get('email')
            password = data.get('password')
            account_type = data.get('account_type', 'user')
            
            # Vérifier si l'utilisateur existe déjà
            if User.objects.filter(username=username).exists():
                return JsonResponse({'errors': {'username': "Ce nom d'utilisateur est déjà pris"}}, status=400)
            
            if User.objects.filter(email=email).exists():
                return JsonResponse({'errors': {'email': "Cette adresse email est déjà utilisée"}}, status=400)
            
            # Créer un nouvel utilisateur
            user = User.objects.create_user(username=username, email=email, password=password)
            user.save()
            
            # Créer un profil utilisateur standard dans tous les cas
            UserProfile.objects.create(user=user)
            
            # Si c'est un compte restaurant, créer également un RestaurantAccount
            if account_type == 'restaurant':
                restaurant_name = data.get('restaurant_name')
                restaurant_city_id = data.get('restaurant_city')
                restaurant_phone = data.get('restaurant_phone')
                restaurant_address = data.get('restaurant_address')
                
                # Vérifier que toutes les données restaurant sont fournies
                if not restaurant_name or not restaurant_city_id or not restaurant_phone or not restaurant_address:
                    return JsonResponse({'errors': {'general': "Informations du restaurant incomplètes"}}, status=400)
                
                try:
                    city = City.objects.get(id=restaurant_city_id)
                    
                    # Créer le restaurant
                    restaurant = Restaurant.objects.create(
                        name=restaurant_name,
                        city=city,
                        address=restaurant_address,
                        phone=restaurant_phone,
                        email=email,
                        is_open=True
                    )
                    
                    # Associer le compte restaurant à l'utilisateur
                    RestaurantAccount.objects.create(
                        user=user,
                        restaurant=restaurant,
                        is_active=True
                    )
                except City.DoesNotExist:
                    return JsonResponse({'errors': {'restaurant_city': "Ville non trouvée"}}, status=400)
                except Exception as e:
                    return JsonResponse({'errors': {'general': f"Erreur lors de la création du restaurant: {str(e)}"}}, status=400)
            
            # Connecter l'utilisateur
            login(request, user)
            
            return JsonResponse({'success': True, 'account_type': account_type}, status=201)
        except Exception as e:
            return JsonResponse({'errors': {'general': str(e)}}, status=400)
    else:
        # Assurer que le token CSRF est généré
        csrf_token = get_token(request)
        # Passer la liste des villes pour le formulaire restaurant
        cities = City.objects.all()
        return render(request, 'foodapp/signup.html', {'cities': cities})

@csrf_exempt
def login_view(request):
    if request.method == 'POST':
        try:
            # Essayer de lire les données JSON si disponibles
            try:
                data = json.loads(request.body)
                username = data.get('username')
                password = data.get('password')
                remember = data.get('remember', False)
            except:
                # Sinon, traiter comme un formulaire standard
                username = request.POST.get('username')
                password = request.POST.get('password')
                remember = request.POST.get('remember', False)
            
            user = authenticate(request, username=username, password=password)
            
            if user is not None:
                login(request, user)
                
                # Si "remember me" n'est pas coché, le cookie de session expirera à la fermeture du navigateur
                if not remember:
                    request.session.set_expiry(0)
                
                # Vérifier si c'est un compte restaurant et rediriger en conséquence
                try:
                    if hasattr(user, 'restaurant_account') and user.restaurant_account.is_active:
                        # C'est un compte restaurant actif
                        if request.headers.get('Content-Type') == 'application/json':
                            return JsonResponse({
                                'success': True, 
                                'redirect': reverse('restaurant_dashboard'),
                                'account_type': 'restaurant'
                            }, status=200)
                        else:
                            return redirect('restaurant_dashboard')
                except:
                    pass
                
                # Compte utilisateur normal
                if request.headers.get('Content-Type') == 'application/json':
                    return JsonResponse({
                        'success': True,
                        'account_type': 'user'
                    }, status=200)
                else:
                    return redirect('index')
            else:
                if request.headers.get('Content-Type') == 'application/json':
                    return JsonResponse({'errors': {'general': "Nom d'utilisateur ou mot de passe incorrect"}}, status=401)
                else:
                    # Pour les formulaires traditionnels, rediriger avec un message d'erreur
                    return render(request, 'foodapp/login.html', {
                        'error': "Nom d'utilisateur ou mot de passe incorrect"
                    })
        except Exception as e:
            return JsonResponse({'errors': {'general': str(e)}}, status=400)
    else:
        # Assurer que le token CSRF est généré
        csrf_token = get_token(request)
        return render(request, 'foodapp/login.html')

def logout_view(request):
    logout(request)
    return redirect('index')

@login_required
def restaurant_dashboard(request):
    """Tableau de bord spécifique pour les comptes restaurants"""
    
    # Vérifier si l'utilisateur a bien un compte restaurant associé
    try:
        restaurant_account = request.user.restaurant_account
        if not restaurant_account.is_active:
            return redirect('index')
    except:
        # Si l'utilisateur n'a pas de compte restaurant associé, le rediriger vers l'accueil
        return redirect('index')
    
    # Récupérer le restaurant associé à ce compte
    restaurant = restaurant_account.restaurant
    
    # Récupérer les réservations de ce restaurant
    # Filtrer par statut si demandé
    status_filter = request.GET.get('status', None)
    date_filter = request.GET.get('date', None)
    
    reservations = Reservation.objects.filter(restaurant=restaurant).order_by('-date', '-time')
    
    if status_filter:
        reservations = reservations.filter(status=status_filter)
    
    if date_filter:
        reservations = reservations.filter(date=date_filter)
    
    # Statistiques
    total_reservations = Reservation.objects.filter(restaurant=restaurant).count()
    pending_reservations = Reservation.objects.filter(restaurant=restaurant, status=Reservation.STATUS_PENDING).count()
    confirmed_reservations = Reservation.objects.filter(restaurant=restaurant, status=Reservation.STATUS_CONFIRMED).count()
    canceled_reservations = Reservation.objects.filter(restaurant=restaurant, status=Reservation.STATUS_CANCELED).count()
    
    # Réservations pour aujourd'hui
    today = timezone.now().date()
    today_reservations = Reservation.objects.filter(restaurant=restaurant, date=today).order_by('time')
    
    context = {
        'restaurant': restaurant,
        'account': restaurant_account,
        'reservations': reservations,
        'today_reservations': today_reservations,
        'total_reservations': total_reservations,
        'pending_reservations': pending_reservations,
        'confirmed_reservations': confirmed_reservations,
        'canceled_reservations': canceled_reservations,
        'status_filter': status_filter,
        'date_filter': date_filter,
    }
    
    return render(request, 'foodapp/restaurant_dashboard.html', context)

@login_required
@csrf_exempt
def update_reservation_status(request, reservation_id):
    """API pour mettre à jour le statut d'une réservation depuis le tableau de bord restaurant"""
    if request.method != 'POST':
        return JsonResponse({'error': 'Méthode non autorisée'}, status=405)
    
    # Vérifier que l'utilisateur est bien un compte restaurant
    try:
        restaurant_account = request.user.restaurant_account
        if not restaurant_account.is_active:
            return JsonResponse({'error': 'Accès non autorisé'}, status=403)
    except:
        return JsonResponse({'error': 'Accès non autorisé'}, status=403)
    
    # Récupérer la réservation
    try:
        reservation = Reservation.objects.get(id=reservation_id, restaurant=restaurant_account.restaurant)
    except Reservation.DoesNotExist:
        return JsonResponse({'error': 'Réservation non trouvée'}, status=404)
    
    # Mettre à jour le statut
    try:
        data = json.loads(request.body)
        new_status = data.get('status')
        if new_status in [s[0] for s in Reservation.STATUS_CHOICES]:
            reservation.status = new_status
            reservation.save()
            return JsonResponse({
                'success': True, 
                'reservation_id': reservation.id,
                'status': reservation.status,
                'status_display': reservation.get_status_display()
            })
        else:
            return JsonResponse({'error': 'Statut invalide'}, status=400)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)

@login_required
def user_profile(request):
    """Vue pour afficher et éditer le profil utilisateur"""
    
    # Récupérer ou créer le profil de l'utilisateur
    user_profile, created = UserProfile.objects.get_or_create(user=request.user)
    
    # Récupérer les réservations de l'utilisateur
    user_reservations = Reservation.objects.filter(user=request.user).order_by('-date')
    
    # Traiter le formulaire de mise à jour du profil
    if request.method == 'POST':
        # Mise à jour des informations du profil
        user_profile.bio = request.POST.get('bio', '')
        user_profile.phone = request.POST.get('phone', '')
        user_profile.favorite_cuisine = request.POST.get('favorite_cuisine', '')
        user_profile.is_vegetarian = request.POST.get('is_vegetarian') == 'on'
        user_profile.is_vegan = request.POST.get('is_vegan') == 'on'
        
        # Traiter l'image de profil
        if 'profile_image' in request.FILES:
            user_profile.profile_image = request.FILES['profile_image']
        
        # Enregistrer les modifications
        user_profile.save()
        
        # Rediriger pour éviter les soumissions multiples
        return redirect('user_profile')
    
    # Récupérer quelques plats recommandés
    if user_profile.is_vegan:
        recommended_dishes = Dish.objects.filter(is_vegan=True)[:3]
    elif user_profile.is_vegetarian:
        recommended_dishes = Dish.objects.filter(is_vegetarian=True)[:3]
    else:
        recommended_dishes = Dish.objects.all().order_by('?')[:3]
    
    context = {
        'user_profile': user_profile,
        'user_reservations': user_reservations,
        'recommended_dishes': recommended_dishes,
        'cities': City.objects.all(),
    }
    
    return render(request, 'foodapp/user_profile.html', context)

# Nouvelles fonctions pour améliorer la gestion des réservations

def is_slot_available(restaurant, date, time, guests, exclude_reservation_id=None):
    """
    Vérifie si un créneau horaire est disponible pour un restaurant donné
    """
    # Récupérer toutes les réservations pour ce restaurant à cette date et heure
    reservations_query = Reservation.objects.filter(
        restaurant=restaurant,
        date=date,
        time=time,
        status__in=[Reservation.STATUS_PENDING, Reservation.STATUS_CONFIRMED]
    )
    
    # Exclure une réservation spécifique (utile pour les modifications)
    if exclude_reservation_id:
        reservations_query = reservations_query.exclude(id=exclude_reservation_id)
    
    # Compter le nombre de convives déjà réservés
    total_guests = reservations_query.aggregate(Sum('guests'))['guests__sum'] or 0
    
    # Supposons qu'un restaurant peut accueillir au maximum 50 personnes simultanément
    # Cette valeur devrait être stockée dans le modèle du restaurant en pratique
    max_capacity = 50
    
    # Vérifier si l'ajout de nouveaux convives ne dépasse pas la capacité
    return (total_guests + guests) <= max_capacity

def get_available_dates(restaurant, start_date=None, days_ahead=30):
    """
    Renvoie les dates disponibles pour réserver dans ce restaurant
    """
    if start_date is None:
        start_date = timezone.now().date()
    
    # Générer une liste de dates pour les prochains jours
    available_dates = []
    for i in range(days_ahead):
        date = start_date + datetime.timedelta(days=i)
        # On pourrait vérifier ici si le restaurant est fermé certains jours
        # Par exemple si le restaurant est fermé le lundi
        if date.weekday() != 0:  # 0 = Lundi
            available_dates.append(date)
    
    return available_dates

@login_required
def user_reservations_list(request):
    """Vue pour afficher toutes les réservations d'un utilisateur"""
    
    # Récupérer les réservations de l'utilisateur
    reservations = Reservation.objects.filter(user=request.user).order_by('-date', '-time')
    
    # Filtrer par statut si demandé
    status_filter = request.GET.get('status')
    if status_filter:
        reservations = reservations.filter(status=status_filter)
    
    context = {
        'reservations': reservations,
        'status_filter': status_filter,
        'STATUS_CHOICES': Reservation.STATUS_CHOICES
    }
    
    return render(request, 'foodapp/user_reservations_list.html', context)

@login_required
def reservation_detail(request, reservation_id):
    """Vue pour afficher les détails d'une réservation"""
    
    # Récupérer la réservation
    reservation = get_object_or_404(Reservation, id=reservation_id)
    
    # Vérifier que l'utilisateur a le droit de voir cette réservation
    if reservation.user != request.user:
        # Vérifier si c'est un restaurateur qui gère ce restaurant
        try:
            restaurant_account = request.user.restaurant_account
            if restaurant_account.restaurant != reservation.restaurant:
                return HttpResponseForbidden("Vous n'êtes pas autorisé à voir cette réservation.")
        except:
            return HttpResponseForbidden("Vous n'êtes pas autorisé à voir cette réservation.")
    
    context = {
        'reservation': reservation,
        'restaurant': reservation.restaurant
    }
    
    return render(request, 'foodapp/reservation_detail.html', context)

@login_required
def reservation_cancel(request, reservation_id):
    """Vue pour annuler une réservation"""
    
    # Récupérer la réservation
    reservation = get_object_or_404(Reservation, id=reservation_id)
    
    # Vérifier que l'utilisateur a le droit d'annuler cette réservation
    if reservation.user != request.user:
        return HttpResponseForbidden("Vous n'êtes pas autorisé à annuler cette réservation.")
    
    # Vérifier que la réservation n'est pas déjà annulée ou terminée
    if reservation.status in [Reservation.STATUS_CANCELED, Reservation.STATUS_COMPLETED]:
        return redirect('reservation_detail', reservation_id=reservation_id)
    
    if request.method == 'POST':
        # Annuler la réservation
        reservation.status = Reservation.STATUS_CANCELED
        reservation.save()
        return redirect('user_reservations_list')
    
    context = {
        'reservation': reservation,
        'restaurant': reservation.restaurant
    }
    
    return render(request, 'foodapp/reservation_cancel.html', context)

@login_required
def reservation_modify(request, reservation_id):
    """Vue pour modifier une réservation"""
    
    # Récupérer la réservation
    reservation = get_object_or_404(Reservation, id=reservation_id)
    
    # Vérifier que l'utilisateur a le droit de modifier cette réservation
    if reservation.user != request.user:
        return HttpResponseForbidden("Vous n'êtes pas autorisé à modifier cette réservation.")
    
    # Vérifier que la réservation n'est pas déjà annulée ou terminée
    if reservation.status in [Reservation.STATUS_CANCELED, Reservation.STATUS_COMPLETED]:
        return redirect('reservation_detail', reservation_id=reservation_id)
    
    # Date limite pour les modifications (24h avant la réservation)
    modification_limit = datetime.datetime.combine(
        reservation.date, 
        reservation.time
    ).replace(tzinfo=timezone.get_current_timezone()) - datetime.timedelta(hours=24)
    
    can_modify = timezone.now() < modification_limit
    
    if request.method == 'POST' and can_modify:
        form = ReservationModifyForm(request.POST, instance=reservation)
        if form.is_valid():
            # Vérifier la disponibilité
            date = form.cleaned_data['date']
            time = form.cleaned_data['time']
            guests = form.cleaned_data['guests']
            
            # Vérifier si le créneau est disponible (en excluant la réservation actuelle)
            if is_slot_available(reservation.restaurant, date, time, guests, exclude_reservation_id=reservation_id):
                form.save()
                return redirect('reservation_detail', reservation_id=reservation_id)
            else:
                form.add_error(None, "Désolé, ce créneau n'est plus disponible. Veuillez choisir un autre horaire.")
    else:
        form = ReservationModifyForm(instance=reservation)
    
    # Récupérer les créneaux disponibles pour JavaScript
    available_dates = get_available_dates(reservation.restaurant)
    
    context = {
        'form': form,
        'reservation': reservation,
        'restaurant': reservation.restaurant,
        'can_modify': can_modify,
        'modification_limit': modification_limit,
        'available_dates': json.dumps([date.strftime('%Y-%m-%d') for date in available_dates])
    }
    
    return render(request, 'foodapp/reservation_modify.html', context)

@login_required
def available_slots(request, restaurant_id):
    """API pour récupérer les créneaux horaires disponibles pour un restaurant"""
    
    restaurant = get_object_or_404(Restaurant, id=restaurant_id)
    
    date_str = request.GET.get('date')
    if not date_str:
        return JsonResponse({'error': 'Date non spécifiée'}, status=400)
    
    try:
        date = datetime.datetime.strptime(date_str, '%Y-%m-%d').date()
    except ValueError:
        return JsonResponse({'error': 'Format de date invalide'}, status=400)
    
    # Heures d'ouverture du restaurant (exemple)
    opening_hours = [
        {'start': '12:00', 'end': '14:30'},  # Déjeuner
        {'start': '19:00', 'end': '22:30'}   # Dîner
    ]
    
    # Créneaux de 30 minutes
    time_slots = []
    for period in opening_hours:
        start_time = datetime.datetime.strptime(period['start'], '%H:%M').time()
        end_time = datetime.datetime.strptime(period['end'], '%H:%M').time()
        
        current_time = start_time
        while current_time < end_time:
            # Vérifier si ce créneau est disponible
            is_available = is_slot_available(restaurant, date, current_time, 1)  # 1 = minimum de convives
            
            time_slots.append({
                'time': current_time.strftime('%H:%M'),
                'available': is_available
            })
            
            # Passer au prochain créneau de 30 minutes
            current_datetime = datetime.datetime.combine(date, current_time)
            current_datetime += datetime.timedelta(minutes=30)
            current_time = current_datetime.time()
    
    return JsonResponse({'slots': time_slots})

@csrf_exempt
def restaurant_signup_view(request):
    """Vue spécifique pour l'inscription des restaurants"""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            username = data.get('username')
            email = data.get('email')
            password = data.get('password')
            
            # Vérifier si l'utilisateur existe déjà
            if User.objects.filter(username=username).exists():
                return JsonResponse({'errors': {'username': "Ce nom d'utilisateur est déjà pris"}}, status=400)
            
            if User.objects.filter(email=email).exists():
                return JsonResponse({'errors': {'email': "Cette adresse email est déjà utilisée"}}, status=400)
            
            # Récupérer les données du restaurant
            restaurant_name = data.get('restaurant_name')
            restaurant_city_id = data.get('restaurant_city')
            restaurant_phone = data.get('restaurant_phone')
            restaurant_address = data.get('restaurant_address')
            restaurant_description = data.get('restaurant_description')
            restaurant_website = data.get('restaurant_website', '')
            restaurant_capacity = data.get('restaurant_capacity', 50)
            
            # Vérifier que toutes les données restaurant sont fournies
            if not restaurant_name:
                return JsonResponse({'errors': {'restaurant_name': "Le nom du restaurant est requis"}}, status=400)
            if not restaurant_city_id:
                return JsonResponse({'errors': {'restaurant_city': "La ville est requise"}}, status=400)
            if not restaurant_phone:
                return JsonResponse({'errors': {'restaurant_phone': "Le numéro de téléphone est requis"}}, status=400)
            if not restaurant_address:
                return JsonResponse({'errors': {'restaurant_address': "L'adresse est requise"}}, status=400)
            if not restaurant_description:
                return JsonResponse({'errors': {'restaurant_description': "La description est requise"}}, status=400)
            
            # Récupérer les fonctionnalités cochées
            try:
                features = json.loads(data.get('features', '[]'))
            except:
                features = []
            
            # Créer un nouvel utilisateur
            user = User.objects.create_user(username=username, email=email, password=password)
            user.save()
            
            # Créer un profil utilisateur
            UserProfile.objects.create(user=user)
            
            try:
                city = City.objects.get(id=restaurant_city_id)
                
                # Créer le restaurant avec plus de détails
                restaurant = Restaurant.objects.create(
                    name=restaurant_name,
                    city=city,
                    address=restaurant_address,
                    phone=restaurant_phone,
                    email=email,
                    website=restaurant_website,
                    description=restaurant_description,
                    is_open=True,
                    capacity=restaurant_capacity,
                )
                
                # Enregistrer les fonctionnalités dans preferences (JSON)
                if features:
                    restaurant.preferences = {'features': features}
                    restaurant.save()
                
                # Associer le compte restaurant à l'utilisateur
                RestaurantAccount.objects.create(
                    user=user,
                    restaurant=restaurant,
                    is_active=True
                )
            except City.DoesNotExist:
                return JsonResponse({'errors': {'restaurant_city': "Ville non trouvée"}}, status=400)
            except Exception as e:
                return JsonResponse({'errors': {'general': f"Erreur lors de la création du restaurant: {str(e)}"}}, status=400)
            
            # Connecter l'utilisateur
            login(request, user)
            
            return JsonResponse({'success': True}, status=201)
        except Exception as e:
            return JsonResponse({'errors': {'general': str(e)}}, status=400)
    else:
        # Assurer que le token CSRF est généré
        csrf_token = get_token(request)
        # Passer la liste des villes pour le formulaire restaurant
        cities = City.objects.all()
        return render(request, 'foodapp/restaurant_signup.html', {'cities': cities})

# Vues pour le forum communautaire
@login_required
def forum_topics_list(request):
    """Vue pour afficher la liste des sujets du forum"""
    # Récupérer tous les sujets, triés par épinglés puis par date de dernière mise à jour
    topics = ForumTopic.objects.all()
    
    # Filtrer par catégorie si demandé
    category = request.GET.get('category')
    if category:
        topics = topics.filter(category=category)
    
    # Rechercher par titre si spécifié
    search = request.GET.get('search')
    if search:
        topics = topics.filter(title__icontains=search)
    
    # Compteurs pour la sidebar
    category_counts = {
        'general': ForumTopic.objects.filter(category='general').count(),
        'recipes': ForumTopic.objects.filter(category='recipes').count(),
        'restaurants': ForumTopic.objects.filter(category='restaurants').count(),
        'travel': ForumTopic.objects.filter(category='travel').count(),
        'events': ForumTopic.objects.filter(category='events').count(),
    }
    
    # Récupérer les sujets récents pour la sidebar
    recent_topics = ForumTopic.objects.order_by('-created_at')[:5]
    
    context = {
        'topics': topics,
        'category': category,
        'search': search,
        'category_counts': category_counts,
        'recent_topics': recent_topics,
        'categories': ForumTopic.CATEGORY_CHOICES,
    }
    
    return render(request, 'foodapp/forum/topics_list.html', context)

@login_required
def forum_topics_by_category(request, category):
    """Vue pour afficher les sujets d'une catégorie spécifique"""
    # Rediriger vers la liste des sujets avec un filtre de catégorie
    return redirect(f'{reverse("forum_topics_list")}?category={category}')

@login_required
def forum_topic_detail(request, topic_id):
    """Vue pour afficher le détail d'un sujet et ses messages"""
    topic = get_object_or_404(ForumTopic, id=topic_id)
    
    # Incrémenter le compteur de vues
    topic.views_count += 1
    topic.save()
    
    # Récupérer tous les messages pour ce sujet
    messages = topic.messages.all()
    
    # Formulaire pour ajouter un nouveau message
    form = None
    if request.user.is_authenticated:
        form = ForumMessageForm()
    
    context = {
        'topic': topic,
        'messages': messages,
        'form': form,
    }
    
    return render(request, 'foodapp/forum/topic_detail.html', context)

@login_required
def forum_new_topic(request):
    """Vue pour créer un nouveau sujet"""
    if request.method == 'POST':
        form = ForumTopicForm(request.POST)
        if form.is_valid():
            # Créer le sujet mais ne pas l'enregistrer immédiatement
            topic = form.save(commit=False)
            # Définir l'auteur comme l'utilisateur connecté
            topic.author = request.user
            # Enregistrer le sujet
            topic.save()
            
            # Créer le premier message (le contenu du sujet)
            message = ForumMessage(
                topic=topic,
                author=request.user,
                content=topic.content
            )
            message.save()
            
            # Rediriger vers le détail du sujet
            return redirect('forum_topic_detail', topic_id=topic.id)
    else:
        form = ForumTopicForm()
    
    context = {
        'form': form,
        'categories': ForumTopic.CATEGORY_CHOICES,
    }
    
    return render(request, 'foodapp/forum/new_topic.html', context)

@login_required
def forum_reply(request, topic_id):
    """Vue pour répondre à un sujet"""
    topic = get_object_or_404(ForumTopic, id=topic_id)
    
    if request.method == 'POST':
        form = ForumMessageForm(request.POST)
        if form.is_valid():
            # Créer le message mais ne pas l'enregistrer immédiatement
            message = form.save(commit=False)
            # Définir l'auteur et le sujet
            message.author = request.user
            message.topic = topic
            # Enregistrer le message
            message.save()
            
            # Mettre à jour la date de dernière activité du sujet
            topic.updated_at = timezone.now()
            topic.save()
            
            # Rediriger vers le détail du sujet
            return redirect('forum_topic_detail', topic_id=topic.id)
    else:
        form = ForumMessageForm()
    
    context = {
        'form': form,
        'topic': topic,
    }
    
    return render(request, 'foodapp/forum/reply.html', context)

@login_required
def forum_edit_message(request, message_id):
    """Vue pour modifier un message"""
    message = get_object_or_404(ForumMessage, id=message_id)
    
    # Vérifier que l'utilisateur est bien l'auteur du message
    if message.author != request.user and not request.user.is_staff:
        return HttpResponseForbidden("Vous n'êtes pas autorisé à modifier ce message.")
    
    if request.method == 'POST':
        form = ForumMessageForm(request.POST, instance=message)
        if form.is_valid():
            form.save()
            return redirect('forum_topic_detail', topic_id=message.topic.id)
    else:
        form = ForumMessageForm(instance=message)
    
    context = {
        'form': form,
        'message': message,
        'topic': message.topic,
    }
    
    return render(request, 'foodapp/forum/edit_message.html', context)

@login_required
def forum_delete_message(request, message_id):
    """Vue pour supprimer un message"""
    message = get_object_or_404(ForumMessage, id=message_id)
    topic = message.topic
    
    # Vérifier que l'utilisateur est bien l'auteur du message ou un administrateur
    if message.author != request.user and not request.user.is_staff:
        return HttpResponseForbidden("Vous n'êtes pas autorisé à supprimer ce message.")
    
    # Vérifier si c'est le premier message (contenu du sujet)
    is_first_message = message.id == topic.messages.order_by('created_at').first().id
    
    if request.method == 'POST':
        if is_first_message:
            # Si c'est le premier message, supprimer tout le sujet
            topic.delete()
            return redirect('forum_topics_list')
        else:
            # Sinon, supprimer juste le message
            message.delete()
            return redirect('forum_topic_detail', topic_id=topic.id)
    
    context = {
        'message': message,
        'topic': topic,
        'is_first_message': is_first_message,
    }
    
    return render(request, 'foodapp/forum/delete_message.html', context)

# Formulaires pour le forum
from django import forms

class ForumTopicForm(forms.ModelForm):
    """Formulaire pour créer un nouveau sujet"""
    class Meta:
        model = ForumTopic
        fields = ['title', 'category', 'content']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Titre du sujet'}),
            'category': forms.Select(attrs={'class': 'form-control'}),
            'content': forms.Textarea(attrs={'class': 'form-control', 'rows': 5, 'placeholder': 'Contenu du sujet'}),
        }

class ForumMessageForm(forms.ModelForm):
    """Formulaire pour créer un nouveau message"""
    class Meta:
        model = ForumMessage
        fields = ['content']
        widgets = {
            'content': forms.Textarea(attrs={'class': 'form-control', 'rows': 5, 'placeholder': 'Votre message'}),
        }

@login_required
def user_settings(request):
    """
    Vue pour afficher et gérer les paramètres utilisateur
    """
    # Récupérer le profil de l'utilisateur
    profile, created = UserProfile.objects.get_or_create(user=request.user)
    
    if request.method == 'POST':
        # Paramètres généraux
        theme = request.POST.get('theme', 'dark')
        notifications_enabled = request.POST.get('notifications_enabled') == 'on'
        language = request.POST.get('language', 'fr')
        
        # Mettre à jour les préférences
        preferences = profile.preferences or {}
        preferences.update({
            'theme': theme,
            'notifications_enabled': notifications_enabled,
            'language': language
        })
        
        # Sauvegarder les modifications
        profile.preferences = preferences
        profile.save()
        
        messages.success(request, 'Vos paramètres ont été mis à jour avec succès.')
        return redirect('user_settings')
    
    # Préparer les préférences par défaut si elles n'existent pas
    if not profile.preferences:
        profile.preferences = {
            'theme': 'dark',
            'notifications_enabled': True,
            'language': 'fr'
        }
        profile.save()
    
    context = {
        'profile': profile,
        'preferences': profile.preferences
    }
    
    return render(request, 'foodapp/user_settings.html', context) 