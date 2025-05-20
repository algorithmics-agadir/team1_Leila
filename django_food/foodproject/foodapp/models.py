from django.db import models
from django.contrib.auth.models import User

# Create your models here.


class Restaurant(models.Model):
    name = models.CharField(max_length=100)
    city = models.ForeignKey('City', on_delete=models.CASCADE, related_name='restaurants')
    address = models.CharField(max_length=200)
    phone = models.CharField(max_length=20)
    email = models.EmailField()
    website = models.URLField(blank=True)
    description = models.TextField(blank=True)
    image = models.ImageField(upload_to='restaurants/', blank=True, null=True)
    is_open = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name} - {self.city.name}"


class RestaurantAccount(models.Model):
    """
    Compte utilisateur spécifique pour les restaurants permettant l'accès au tableau de bord restaurateur
    """
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='restaurant_account')
    restaurant = models.OneToOneField(Restaurant, on_delete=models.CASCADE, related_name='account')
    is_manager = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    phone_number = models.CharField(max_length=20, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    last_login = models.DateTimeField(null=True, blank=True)
    
    def __str__(self):
        return f"Compte {self.restaurant.name} - {self.user.username}"


class City(models.Model):
    name = models.CharField(max_length=100)
    description = models.CharField(max_length=500)
    image = models.ImageField(upload_to='cities/', blank=True, null=True)

    def __str__(self):
        return self.name

class Dish(models.Model):
    SWEET = 'sweet'
    SALTY = 'salty'
    DRINK = 'drink'
    TYPE_CHOICES = [
        (SWEET, 'Sweet'),
        (SALTY, 'Salty'),
        (DRINK, 'Drink'),
    ]
    
    # Origines culinaires
    MOROCCAN = 'moroccan'
    ITALIAN = 'italian'
    FRENCH = 'french'
    JAPANESE = 'japanese'
    MEXICAN = 'mexican'
    CHINESE = 'chinese'
    INDIAN = 'indian'
    OTHER = 'other'
    ORIGIN_CHOICES = [
        (MOROCCAN, 'Cuisine Marocaine'),
        (ITALIAN, 'Cuisine Italienne'),
        (FRENCH, 'Cuisine Française'),
        (JAPANESE, 'Cuisine Japonaise'),
        (MEXICAN, 'Cuisine Mexicaine'),
        (CHINESE, 'Cuisine Chinoise'),
        (INDIAN, 'Cuisine Indienne'),
        (OTHER, 'Autre Cuisine'),
    ]

    city = models.ForeignKey(City, on_delete=models.CASCADE, related_name='dishes')
    name = models.CharField(max_length=100)
    type = models.CharField(max_length=10, choices=TYPE_CHOICES)
    origin = models.CharField(max_length=20, choices=ORIGIN_CHOICES, default=OTHER)
    image = models.ImageField(upload_to='dishes/', blank=True, null=True)
    bad_for_cholesterol = models.BooleanField(default=False)
    bad_for_sugar = models.BooleanField(default=False)
    bad_for_lactose = models.BooleanField(default=False)
    is_vegetarian = models.BooleanField(default=False)
    is_vegan = models.BooleanField(default=False)
    price_range = models.CharField(max_length=10, choices=[
        ('low', '$'),
        ('medium', '$$'),
        ('high', '$$$'),
    ], default='medium')
    description = models.TextField(blank=True)
    ingredients = models.TextField(blank=True)
    history = models.TextField(blank=True)
    preparation_steps = models.TextField(blank=True)
    
    # Nouveau champ pour les plats traditionnels recommandés aux touristes
    is_tourist_recommended = models.BooleanField(default=False)
    
    # Notes culturelles pour les touristes
    cultural_notes = models.TextField(blank=True, help_text="Informations culturelles sur ce plat pour les touristes")

    def __str__(self):
        return f"{self.name} ({self.city.name})"


class Reservation(models.Model):
    STATUS_PENDING = 'pending'
    STATUS_CONFIRMED = 'confirmed'
    STATUS_CANCELED = 'canceled'
    STATUS_COMPLETED = 'completed'
    
    STATUS_CHOICES = [
        (STATUS_PENDING, 'En attente'),
        (STATUS_CONFIRMED, 'Confirmée'),
        (STATUS_CANCELED, 'Annulée'),
        (STATUS_COMPLETED, 'Terminée'),
    ]
    
    restaurant = models.ForeignKey(Restaurant, on_delete=models.CASCADE, related_name='reservations')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reservations', null=True, blank=True)
    name = models.CharField(max_length=100)
    email = models.EmailField()
    phone = models.CharField(max_length=20)
    date = models.DateField()
    time = models.TimeField()
    guests = models.IntegerField()
    notes = models.TextField(blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_PENDING)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"Réservation {self.id} - {self.restaurant.name} - {self.date} {self.time}"
