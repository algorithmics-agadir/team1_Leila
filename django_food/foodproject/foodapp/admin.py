from django.contrib import admin
from .models import City, Dish, Restaurant, Reservation, RestaurantAccount
from django.utils.html import format_html
from django.contrib.auth.models import User
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

# Register your models here.
class DishInline(admin.TabularInline):
    model = Dish
    extra = 0

class CityAdmin(admin.ModelAdmin):
    list_display = ('name', 'get_image', 'get_dishes_count', 'get_restaurants_count')
    search_fields = ('name',)
    inlines = [DishInline]
    
    def get_dishes_count(self, obj):
        return obj.dishes.count()
    get_dishes_count.short_description = "Nombre de plats"
    
    def get_restaurants_count(self, obj):
        return obj.restaurants.count()
    get_restaurants_count.short_description = "Nombre de restaurants"
    
    def get_image(self, obj):
        if obj.image:
            return format_html('<img src="{}" width="50" height="50" style="border-radius: 50%;" />', obj.image.url)
        return format_html('<span>Pas d\'image</span>')
    get_image.short_description = "Image"

class DishAdmin(admin.ModelAdmin):
    list_display = ('name', 'city', 'type', 'origin', 'price_range', 'is_vegetarian', 'is_vegan', 'get_image')
    list_filter = ('city', 'type', 'origin', 'price_range', 'is_vegetarian', 'is_vegan', 'is_tourist_recommended')
    search_fields = ('name', 'description')
    
    fieldsets = (
        ('Informations de base', {
            'fields': ('name', 'city', 'type', 'origin', 'price_range', 'description', 'image')
        }),
        ('Caractéristiques diététiques', {
            'fields': ('bad_for_cholesterol', 'bad_for_sugar', 'bad_for_lactose', 'is_vegetarian', 'is_vegan'),
            'classes': ('collapse',),
        }),
        ('Pour les touristes', {
            'fields': ('is_tourist_recommended', 'cultural_notes'),
            'classes': ('collapse',),
        }),
        ('Détails culinaires', {
            'fields': ('ingredients', 'history', 'preparation_steps'),
            'classes': ('collapse',),
        }),
    )
    
    def get_image(self, obj):
        if obj.image:
            return format_html('<img src="{}" width="50" height="50" />', obj.image.url)
        return format_html('<span>Pas d\'image</span>')
    get_image.short_description = "Image"

class RestaurantAdmin(admin.ModelAdmin):
    list_display = ('name', 'city', 'is_open', 'phone', 'email', 'get_image', 'has_account')
    list_filter = ('city', 'is_open')
    search_fields = ('name', 'address', 'description')
    
    def get_image(self, obj):
        if obj.image:
            return format_html('<img src="{}" width="50" height="50" style="border-radius: 5px;" />', obj.image.url)
        return format_html('<span>Pas d\'image</span>')
    get_image.short_description = "Image"
    
    def has_account(self, obj):
        try:
            return bool(obj.account)
        except:
            return False
    has_account.boolean = True
    has_account.short_description = "Compte actif"

class ReservationAdmin(admin.ModelAdmin):
    list_display = ('id', 'restaurant', 'name', 'date', 'time', 'guests', 'status', 'created_at')
    list_filter = ('restaurant', 'date', 'status')
    search_fields = ('name', 'email', 'notes')
    date_hierarchy = 'date'

# Personnalisation pour ajouter le lien entre User et RestaurantAccount
class RestaurantAccountInline(admin.StackedInline):
    model = RestaurantAccount
    can_delete = False
    verbose_name_plural = 'Compte restaurant'

# Étendre l'admin User standard pour inclure RestaurantAccount
class UserAdmin(BaseUserAdmin):
    inlines = (RestaurantAccountInline, )
    list_display = ('username', 'email', 'first_name', 'last_name', 'is_staff', 'is_restaurant')
    
    def is_restaurant(self, obj):
        try:
            return bool(obj.restaurant_account)
        except:
            return False
    is_restaurant.boolean = True
    is_restaurant.short_description = "Restaurant"

# Class Admin pour RestaurantAccount
class RestaurantAccountAdmin(admin.ModelAdmin):
    list_display = ('user', 'restaurant', 'is_manager', 'is_active', 'created_at', 'last_login')
    list_filter = ('is_manager', 'is_active')
    search_fields = ('user__username', 'restaurant__name')
    raw_id_fields = ('user', 'restaurant')

# Désinscrire le modèle User d'origine
admin.site.unregister(User)

# Enregistrer les modèles avec leurs classes Admin
admin.site.register(User, UserAdmin)
admin.site.register(City, CityAdmin)
admin.site.register(Dish, DishAdmin)
admin.site.register(Restaurant, RestaurantAdmin)
admin.site.register(Reservation, ReservationAdmin)
admin.site.register(RestaurantAccount, RestaurantAccountAdmin)

# Personnaliser l'interface d'administration
admin.site.site_header = "FoodFlex Administration"
admin.site.site_title = "FoodFlex Admin"
admin.site.index_title = "Tableau de bord FoodFlex"
