from django.urls import path
from . import views
from django.shortcuts import redirect

# Fonction pour rediriger vers signup
def redirect_to_signup(request):
    return redirect('signup')

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
    path('restaurant-signup/', views.restaurant_signup_view, name='restaurant_signup'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    
    # URL pour la déconnexion via /accounts/logout/ (compatibilité)
    path('accounts/logout/', views.logout_view, name='accounts_logout'),
    
    # URL pour rediriger /accounts/login/ vers signup
    path('accounts/login/', redirect_to_signup, name='accounts_login'),
    
    # URLs pour le tableau de bord restaurant
    path('restaurant/dashboard/', views.restaurant_dashboard, name='restaurant_dashboard'),
    path('api/reservation/<int:reservation_id>/status/', views.update_reservation_status, name='update_reservation_status'),
    
    # URL pour le profil utilisateur
    path('profile/', views.user_profile, name='user_profile'),
    
    # URL pour les paramètres utilisateur
    path('settings/', views.user_settings, name='user_settings'),
    
    # Nouvelles URLs pour les améliorations de réservation
    path('reservations/', views.user_reservations_list, name='user_reservations_list'),
    path('reservations/<int:reservation_id>/', views.reservation_detail, name='reservation_detail'),
    path('reservations/<int:reservation_id>/cancel/', views.reservation_cancel, name='reservation_cancel'),
    path('reservations/<int:reservation_id>/modify/', views.reservation_modify, name='reservation_modify'),
    path('api/available-slots/<int:restaurant_id>/', views.available_slots, name='available_slots'),
    
    # Nouvelle URL pour marquer un plat comme vu
    path('api/mark-dish-viewed/<int:dish_id>/', views.mark_dish_viewed, name='mark_dish_viewed'),
    
    # URLs pour le forum communautaire
    path('forum/', views.forum_topics_list, name='forum_topics_list'),
    path('forum/category/<str:category>/', views.forum_topics_by_category, name='forum_topics_by_category'),
    path('forum/topic/<int:topic_id>/', views.forum_topic_detail, name='forum_topic_detail'),
    path('forum/new-topic/', views.forum_new_topic, name='forum_new_topic'),
    path('forum/topic/<int:topic_id>/reply/', views.forum_reply, name='forum_reply'),
    path('forum/message/<int:message_id>/edit/', views.forum_edit_message, name='forum_edit_message'),
    path('forum/message/<int:message_id>/delete/', views.forum_delete_message, name='forum_delete_message'),
] 