from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('accueil/', views.accueil, name='accueil'),
    path('dishes/', views.dish_list, name='dish_list'),
    path('dishes/<int:dish_id>/', views.dish_detail, name='dish_detail'),
    path('currency/', views.currency_converter, name='currency_converter'),
    path('restaurants/', views.restaurants, name='restaurants'),
    path('restaurants/<int:restaurant_id>/', views.restaurant_detail, name='restaurant_detail'),
    path('restaurants/<int:restaurant_id>/reservation/', views.reservation, name='reservation'),
    path('api/dishes/', views.get_dishes, name='api_dishes'),
    path('api/restaurants/', views.get_restaurants, name='api_restaurants'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('moroccan-cuisine/', views.moroccan_cuisine, name='moroccan_cuisine'),
    path('signup/', views.signup_view, name='signup'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    
    # Nouvelles URLs pour le tableau de bord restaurant
    path('restaurant/dashboard/', views.restaurant_dashboard, name='restaurant_dashboard'),
    path('api/reservation/<int:reservation_id>/status/', views.update_reservation_status, name='update_reservation_status'),
]
