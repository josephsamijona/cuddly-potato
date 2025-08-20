# Dans votre fichier urls.py principal ou dans un fichier auth_urls.py séparé

from django.urls import path
from .views.auth import (
    login_view, logout_view, ProfileView, 
    password_change_view, RegisterUserView
)
from .views.admin import (
    UserListView, UserDetailView, 
    UserUpdateView, user_toggle_active
)

# URLs pour l'authentification et la gestion du profil
urlpatterns = [
    # Authentification de base
    path('login/', login_view, name='login'),
    path('logout/', logout_view, name='logout'),
    path('profile/', ProfileView.as_view(), name='profile'),
    path('password-change/', password_change_view, name='password_change'),
    
    # Administration des utilisateurs (accès ADMIN uniquement)
    path('users/', UserListView.as_view(), name='user_list'),
    path('users/add/', RegisterUserView.as_view(), name='user_add'),
    path('users/<int:pk>/', UserDetailView.as_view(), name='user_detail'),
    path('users/<int:pk>/update/', UserUpdateView.as_view(), name='user_update'),
    path('users/<int:pk>/toggle-active/', user_toggle_active, name='user_toggle_active'),
]