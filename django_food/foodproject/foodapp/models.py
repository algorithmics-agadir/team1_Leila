from django.db import models
from django.contrib.auth.models import User
from django.utils.html import mark_safe
from django.utils import timezone
import datetime

class City(models.Model):
    name = models.CharField(max_length=100)
    image = models.ImageField(upload_to='cities/', blank=True, null=True)
    description = models.TextField(blank=True)
    population = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)
    
    def __str__(self):
        return self.name
    
    def get_image(self):
        if self.image:
            return mark_safe(f'<img src="{self.image.url}" width="50" height="50" style="object-fit: cover; border-radius: 5px;" />')
        return "—"
    
    get_image.short_description = "Image"
    
    class Meta:
        verbose_name_plural = "Cities"
        ordering = ['name']

class Dish(models.Model):
    # Types de plats
    SWEET = 'sweet'
    SALTY = 'salty'
    DRINK = 'drink'
    TYPE_CHOICES = [
        (SWEET, 'Sucré'),
        (SALTY, 'Salé'),
        (DRINK, 'Boisson'),
    ]
    
    PRICE_LOW = 'L'
    PRICE_MEDIUM = 'M'
    PRICE_HIGH = 'H'
    
    PRICE_RANGE_CHOICES = [
        (PRICE_LOW, 'Abordable'),
        (PRICE_MEDIUM, 'Modéré'),
        (PRICE_HIGH, 'Premium'),
    ]
    
    # Origine culinaire
    MOROCCAN = 'moroccan'
    INTERNATIONAL = 'international'
    FUSION = 'fusion'
    ORIGIN_CHOICES = [
        (MOROCCAN, 'Marocaine'),
        (INTERNATIONAL, 'Internationale'),
        (FUSION, 'Fusion'),
    ]
    
    name = models.CharField(max_length=100)
    description = models.TextField()
    price_range = models.CharField(max_length=10)
    image = models.ImageField(upload_to='dishes/', null=True, blank=True)
    type = models.CharField(max_length=20, choices=TYPE_CHOICES)
    is_vegetarian = models.BooleanField(default=False)
    is_vegan = models.BooleanField(default=False)
    ingredients = models.TextField(null=True, blank=True)
    preparation_steps = models.TextField(null=True, blank=True)
    history = models.TextField(null=True, blank=True)
    city = models.ForeignKey('City', related_name='dishes', on_delete=models.SET_NULL, null=True, blank=True)
    
    # Nouveaux champs pour l'origine culinaire et recommandations touristiques
    origin = models.CharField(max_length=20, choices=ORIGIN_CHOICES, default=MOROCCAN)
    is_tourist_recommended = models.BooleanField(default=False, 
                                              help_text="Cochez cette case si ce plat est particulièrement recommandé aux touristes")
    cultural_notes = models.TextField(blank=True, null=True,
                                     help_text="Notes culturelles sur ce plat pour les touristes")
    
    # Champ pour la date de création du plat (pour l'icône "Nouveau")
    created_at = models.DateTimeField(auto_now_add=True)
    
    # Champ pour suivre les utilisateurs qui ont vu ce plat
    viewed_by = models.ManyToManyField(User, related_name='viewed_dishes', blank=True)
    
    def __str__(self):
        return self.name
    
    def is_new(self):
        """Vérifie si le plat est considéré comme nouveau (moins de 3 jours)"""
        three_days_ago = timezone.now() - datetime.timedelta(days=3)
        return self.created_at >= three_days_ago
    
    def mark_as_viewed(self, user):
        """Marque le plat comme vu par l'utilisateur"""
        if user.is_authenticated:
            self.viewed_by.add(user)
    
    def is_new_for_user(self, user):
        """Vérifie si le plat est nouveau pour cet utilisateur spécifique"""
        if not user.is_authenticated:
            return self.is_new()
        return self.is_new() and not self.viewed_by.filter(id=user.id).exists()
    
    def get_image_preview(self):
        if self.image:
            return mark_safe(f'<img src="{self.image.url}" width="100" height="75" style="object-fit: cover; border-radius: 5px;" />')
        return "—"
    
    get_image_preview.short_description = "Image"

class Restaurant(models.Model):
    name = models.CharField(max_length=100)
    city = models.ForeignKey(City, on_delete=models.CASCADE, related_name='restaurants')
    address = models.CharField(max_length=200)
    phone = models.CharField(max_length=20)
    email = models.EmailField()
    website = models.URLField(blank=True)
    description = models.TextField(blank=True)
    image = models.ImageField(upload_to='restaurants/', blank=True, null=True)
    is_open = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    capacity = models.PositiveIntegerField(default=50, help_text="Capacité maximale du restaurant")
    
    def __str__(self):
        return f"{self.name} - {self.city.name}"
    
    def get_image_preview(self):
        if self.image:
            return mark_safe(f'<img src="{self.image.url}" width="100" height="75" style="object-fit: cover; border-radius: 5px;" />')
        return "—"
    
    get_image_preview.short_description = "Image"
    
    @property
    def rating(self):
        reviews = self.reviews.all()
        if not reviews:
            return 0
        return sum(review.rating for review in reviews) / reviews.count()

class RestaurantAccount(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='restaurant_account')
    restaurant = models.OneToOneField(Restaurant, on_delete=models.CASCADE, related_name='account')
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Compte restaurant pour {self.restaurant.name}"

class Reservation(models.Model):
    # Statut de réservation
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
    guests = models.PositiveIntegerField(default=2)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_PENDING)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    confirmation_code = models.CharField(max_length=10, unique=True, blank=True, null=True)
    
    def __str__(self):
        return f"Réservation de {self.name} au {self.restaurant.name} le {self.date} à {self.time}"
    
    def save(self, *args, **kwargs):
        # Générer un code de confirmation si nécessaire
        if not self.confirmation_code:
            import random
            import string
            # Générer un code aléatoire de 10 caractères alphanumériques
            self.confirmation_code = ''.join(
                random.choices(string.ascii_uppercase + string.digits, k=6)
            )
        super().save(*args, **kwargs)
    
    @property
    def is_past(self):
        """Vérifie si la réservation est passée"""
        now = timezone.now()
        reservation_datetime = timezone.make_aware(
            timezone.datetime.combine(self.date, self.time)
        )
        return reservation_datetime < now
    
    @property
    def can_cancel(self):
        """Vérifie si la réservation peut être annulée"""
        return (
            not self.is_past and 
            self.status not in [self.STATUS_CANCELED, self.STATUS_COMPLETED]
        )
    
    @property
    def can_modify(self):
        """Vérifie si la réservation peut être modifiée"""
        if self.is_past or self.status in [self.STATUS_CANCELED, self.STATUS_COMPLETED]:
            return False
        
        # Vérifier que la réservation est au moins 24h dans le futur
        now = timezone.now()
        reservation_datetime = timezone.make_aware(
            timezone.datetime.combine(self.date, self.time)
        )
        return (reservation_datetime - now).total_seconds() > 24 * 3600

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    bio = models.TextField(blank=True)
    phone = models.CharField(max_length=20, blank=True)
    profile_image = models.ImageField(upload_to='profiles/', blank=True, null=True)
    favorite_cuisine = models.CharField(max_length=100, blank=True)
    date_of_birth = models.DateField(null=True, blank=True)
    is_vegetarian = models.BooleanField(default=False)
    is_vegan = models.BooleanField(default=False)
    preferences = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"Profil de {self.user.username}"
    
    def get_image_preview(self):
        if self.profile_image:
            return mark_safe(f'<img src="{self.profile_image.url}" width="50" height="50" style="object-fit: cover; border-radius: 50%;" />')
        return "—"
    
    get_image_preview.short_description = "Image"
    
    @property
    def full_name(self):
        if self.user.first_name and self.user.last_name:
            return f"{self.user.first_name} {self.user.last_name}"
        return self.user.username

class Review(models.Model):
    RATING_CHOICES = [
        (1, '1 étoile'),
        (2, '2 étoiles'),
        (3, '3 étoiles'),
        (4, '4 étoiles'),
        (5, '5 étoiles'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reviews')
    restaurant = models.ForeignKey(Restaurant, on_delete=models.CASCADE, related_name='reviews')
    rating = models.IntegerField(choices=RATING_CHOICES)
    comment = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_published = models.BooleanField(default=True)
    photos = models.ImageField(upload_to='reviews/', blank=True, null=True)
    
    def __str__(self):
        return f"Avis de {self.user.username} sur {self.restaurant.name} - {self.rating}/5"
    
    class Meta:
        unique_together = ('user', 'restaurant')
        ordering = ['-created_at']

class ForumTopic(models.Model):
    """Modèle pour les sujets de discussion du forum"""
    CATEGORY_CHOICES = [
        ('general', 'Discussion Générale'),
        ('recipes', 'Recettes & Astuces'),
        ('restaurants', 'Restaurants'),
        ('travel', 'Voyages Culinaires'),
        ('events', 'Événements & Rencontres'),
    ]
    
    title = models.CharField(max_length=200, verbose_name="Titre")
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='forum_topics', verbose_name="Auteur")
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, default='general', verbose_name="Catégorie")
    content = models.TextField(verbose_name="Contenu")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Créé le")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Mis à jour le")
    is_pinned = models.BooleanField(default=False, verbose_name="Épinglé")
    views_count = models.PositiveIntegerField(default=0, verbose_name="Nombre de vues")
    
    def __str__(self):
        return self.title
    
    @property
    def messages_count(self):
        return self.messages.count()
    
    @property
    def last_activity(self):
        last_message = self.messages.order_by('-created_at').first()
        if last_message:
            return last_message.created_at
        return self.created_at
    
    class Meta:
        verbose_name = "Sujet de forum"
        verbose_name_plural = "Sujets de forum"
        ordering = ['-is_pinned', '-updated_at']

class ForumMessage(models.Model):
    """Modèle pour les messages dans les sujets du forum"""
    topic = models.ForeignKey(ForumTopic, on_delete=models.CASCADE, related_name='messages', verbose_name="Sujet")
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='forum_messages', verbose_name="Auteur")
    content = models.TextField(verbose_name="Contenu")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Créé le")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Mis à jour le")
    is_solution = models.BooleanField(default=False, verbose_name="Marqué comme solution")
    
    def __str__(self):
        return f"Message de {self.author.username} dans {self.topic.title}"
    
    class Meta:
        verbose_name = "Message de forum"
        verbose_name_plural = "Messages de forum"
        ordering = ['created_at']

