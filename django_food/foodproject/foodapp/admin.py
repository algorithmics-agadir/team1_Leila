from django.contrib import admin
from .models import Restaurant, City, Dish, Reservation

class RestaurantAdmin(admin.ModelAdmin):
    list_display = ('name', 'city', 'phone', 'email', 'is_open', 'created_at')
    list_filter = ('is_open', 'city')
    search_fields = ('name', 'address', 'email', 'phone')
    date_hierarchy = 'created_at'
    list_editable = ('is_open',)
    list_per_page = 25
    fieldsets = (
        ('Informations générales', {
            'fields': ('name', 'city', 'description', 'image')
        }),
        ('Coordonnées', {
            'fields': ('address', 'phone', 'email', 'website')
        }),
        ('Statut', {
            'fields': ('is_open',)
        }),
    )

class CityAdmin(admin.ModelAdmin):
    list_display = ('name', 'description', 'get_restaurants_count', 'get_dishes_count')
    search_fields = ('name', 'description')
    
    def get_restaurants_count(self, obj):
        return obj.restaurants.count()
    get_restaurants_count.short_description = 'Restaurants'
    
    def get_dishes_count(self, obj):
        return obj.dishes.count()
    get_dishes_count.short_description = 'Plats'

class DishAdmin(admin.ModelAdmin):
    list_display = ('name', 'city', 'type', 'price_range', 'is_vegetarian', 'is_vegan')
    list_filter = ('type', 'city', 'price_range', 'is_vegetarian', 'is_vegan', 'bad_for_cholesterol', 'bad_for_sugar', 'bad_for_lactose')
    search_fields = ('name', 'description', 'ingredients')
    list_editable = ('price_range', 'is_vegetarian', 'is_vegan')
    fieldsets = (
        ('Informations générales', {
            'fields': ('name', 'city', 'type', 'description', 'image')
        }),
        ('Caractéristiques', {
            'fields': ('price_range', 'ingredients', 'history', 'preparation_steps')
        }),
        ('Restrictions alimentaires', {
            'fields': ('is_vegetarian', 'is_vegan', 'bad_for_cholesterol', 'bad_for_sugar', 'bad_for_lactose'),
            'classes': ('collapse',),
        }),
    )

class ReservationAdmin(admin.ModelAdmin):
    list_display = ('id', 'restaurant', 'name', 'date', 'time', 'guests', 'status', 'created_at')
    list_filter = ('status', 'date', 'restaurant')
    search_fields = ('name', 'email', 'phone')
    date_hierarchy = 'date'
    list_editable = ('status',)
    list_per_page = 25
    readonly_fields = ('created_at', 'updated_at')
    fieldsets = (
        ('Informations de réservation', {
            'fields': ('restaurant', 'date', 'time', 'guests', 'status')
        }),
        ('Informations du client', {
            'fields': ('user', 'name', 'email', 'phone')
        }),
        ('Notes et suivi', {
            'fields': ('notes', 'created_at', 'updated_at')
        }),
    )

# Enregistrer les modèles dans l'admin
admin.site.register(Restaurant, RestaurantAdmin)
admin.site.register(City, CityAdmin)
admin.site.register(Dish, DishAdmin)
admin.site.register(Reservation, ReservationAdmin)

# Personnaliser l'interface d'administration
admin.site.site_header = "FoodFlex Administration"
admin.site.site_title = "FoodFlex Admin"
admin.site.index_title = "Tableau de bord FoodFlex"
