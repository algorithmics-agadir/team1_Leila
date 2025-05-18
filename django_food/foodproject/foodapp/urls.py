from django.urls import path
from . import views

urlpatterns = [
    path('', views.accueil, name='accueil'),
    path('app/', views.index, name='index'),
    path('dishes/', views.dish_list, name='dish_list'),
    path('dishes/<int:dish_id>/', views.dish_detail, name='dish_detail'),
    path('currency/', views.currency_converter, name='currency_converter'),
    path('restaurants/', views.restaurants, name='restaurants'),
    path('restaurants/<int:restaurant_id>/', views.restaurant_detail, name='restaurant_detail'),
    path('restaurants/<int:restaurant_id>/reservation/', views.reservation, name='reservation'),
    path('api/dishes/', views.get_dishes, name='api_dishes'),
    path('dashboard/', views.dashboard, name='dashboard'),
]
