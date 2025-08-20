# Dans votre fichier urls.py principal ou dans un fichier auth_urls.py séparé

from django.urls import path
from .views.auth import (
    login_view, logout_view, ProfileView, 
    password_change_view, RegisterUserView
)
from .views.dashboard import DashboardView, index
from .views.admin import (
    UserListView, UserDetailView, 
    UserUpdateView, user_toggle_active
)
from .views.patients import (
    PatientListView, PatientDetailView, PatientCreateView, 
    PatientUpdateView, patient_search_view, patient_create
)
from .views.dossiers import (
    DossierMedicalView, ConsultationCreateView, ConsultationDetailView,
    ConsultationListView, consultation_create, consultation_update
)
from .views.rendezvous import (
    CalendrierRendezVousView, RendezVousListView, RendezVousCreateView,
    RendezVousUpdateView, RendezVousDuJourView, rendez_vous_create,
    rendez_vous_update_status, check_disponibilite
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
    #dashboardl;'
    
    path('', index, name='index'),
    path('dashboard/', DashboardView.as_view(), name='dashboard'),
    
    #patients
    path('patients/', PatientListView.as_view(), name='patient_list'),
    path('patients/ajouter/', PatientCreateView.as_view(), name='patient_create'),
    path('patients/recherche/', patient_search_view, name='patient_search'),
    path('patients/<int:pk>/', PatientDetailView.as_view(), name='patient_detail'),
    path('patients/<int:pk>/modifier/', PatientUpdateView.as_view(), name='patient_update'),
    
    # Alternative avec vue basée sur fonction
    path('patients/nouveau/', patient_create, name='patient_create_func'),
    
    #dossiers
    
    # Dossiers médicaux
    path('dossiers/<int:pk>/', DossierMedicalView.as_view(), name='dossier_medical'),
    
    # Consultations - vues basées sur des classes
    path('dossiers/<int:dossier_id>/consultation/nouvelle/', ConsultationCreateView.as_view(), name='consultation_create_from_dossier'),
    path('consultations/<int:pk>/', ConsultationDetailView.as_view(), name='consultation_detail'),
    path('consultations/liste/', ConsultationListView.as_view(), name='consultation_list'),
    path('consultations/patient/<int:patient_id>/', ConsultationListView.as_view(), name='consultation_list_patient'),
    
    # Consultations - vues basées sur des fonctions (alternatives)
    path('patients/<int:patient_id>/consultation/nouvelle/', consultation_create, name='consultation_create_from_patient'),
    path('consultations/<int:pk>/modifier/', consultation_update, name='consultation_update'),
        # Vues principales des rendez-vous
    path('rendezvous/calendrier/', CalendrierRendezVousView.as_view(), name='rendezvous_calendrier'),
    path('rendezvous/liste/', RendezVousListView.as_view(), name='rendezvous_list'),
    path('rendezvous/jour/', RendezVousDuJourView.as_view(), name='rendezvous_jour'),
    path('rendezvous/nouveau/', RendezVousCreateView.as_view(), name='rendezvous_create'),
    path('rendezvous/<int:pk>/modifier/', RendezVousUpdateView.as_view(), name='rendezvous_update'),
    
    # Actions sur les rendez-vous
    path('rendezvous/<int:pk>/statut/', rendez_vous_update_status, name='rendezvous_update_status'),
    
    # API pour vérifier la disponibilité
    path('rendezvous/check-disponibilite/', check_disponibilite, name='rendezvous_check_disponibilite'),
    
    # Création de rendez-vous depuis la fiche patient (vue fonctionnelle)
    path('patients/<int:patient_id>/rendezvous/nouveau/', rendez_vous_create, name='rendezvous_create_patient'),

]