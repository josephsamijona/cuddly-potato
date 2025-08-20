from django.shortcuts import redirect
from django.urls import reverse
from django.contrib import messages
from django.conf import settings
import logging

# Configurer le logger pour tracer les tentatives d'accès non autorisé
logger = logging.getLogger('access_control')

class AccessControlMiddleware:
    """
    Middleware pour gérer le contrôle d'accès basé sur les rôles dans tout le système.
    
    Ce middleware vérifie si l'utilisateur connecté a le droit d'accéder
    à une vue spécifique en fonction de son rôle.
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
        # Dictionnaire qui définit les URL accessibles sans authentification
        self.public_urls = [
            '/login/',
            '/logout/',
            '/password_reset/',
            '/admin/login/',
            '/static/',
            '/media/'
        ]

    def __call__(self, request):
        # Exécution avant la vue
        response = self.get_response(request)
        # Exécution après la vue
        return response
    
    def process_view(self, request, view_func, view_args, view_kwargs):
        # Récupérer le chemin de la requête
        path = request.path_info
        
        # Vérifier si le chemin est une URL publique (accessible sans authentification)
        if any(path.startswith(url) for url in self.public_urls):
            return None
        
        # Vérifier si l'utilisateur est authentifié
        if not request.user.is_authenticated:
            messages.error(request, "Veuillez vous connecter pour accéder à cette page.")
            return redirect(settings.LOGIN_URL)
        
        # Accès pour les superutilisateurs (administrateurs Django)
        if request.user.is_superuser:
            return None
            
        # Vérifier si l'utilisateur a un profil de personnel associé
        try:
            role = request.user.personnel.role
        except AttributeError:
            logger.warning(f"L'utilisateur {request.user.username} n'a pas de profil personnel associé")
            messages.error(request, "Votre compte n'a pas de rôle attribué. Contactez l'administrateur.")
            return redirect(settings.LOGIN_URL)
        
        # Obtenir le nom de la vue à partir de view_func
        view_name = view_func.__name__
        view_class = view_func.__class__.__name__ if hasattr(view_func, '__class__') else ""
        
        # Définir les permissions par rôle
        # Ces dictionnaires associent chaque rôle à une liste de vues auxquelles il a accès
        view_permissions = {
            'ADMIN': [],  # Accès à tout pour les administrateurs
            'MEDECIN': [
                # Dashboard
                'DashboardView', 'index',
                
                # Patients
                'PatientListView', 'PatientDetailView', 'PatientSearchView',
                
                # Dossiers médicaux
                'DossierMedicalView', 'ConsultationCreateView', 'ConsultationDetailView', 
                'ConsultationListView', 'consultation_create', 'consultation_detail',
                
                # Rendez-vous
                'CalendrierRendezVousView', 'RendezVousListView', 'RendezVousCreateView', 
                'RendezVousUpdateView', 'RendezVousDuJourView', 'rendez_vous_create',
                
                # Examens
                'ExamenListView', 'ExamenCreateView', 'ExamenDetailView', 'ResultatExamenView',
                'examen_create', 'examen_detail',
                
                # Prescriptions
                'PrescriptionListView', 'PrescriptionCreateView', 'PrescriptionDetailView', 
                'PrescriptionPrintView', 'prescription_create', 'prescription_print'
            ],
            'INFIRMIER': [
                # Dashboard
                'DashboardView', 'index',
                
                # Patients
                'PatientListView', 'PatientDetailView', 'PatientSearchView',
                
                # Dossiers médicaux
                'DossierMedicalView', 'ConsultationDetailView', 'ConsultationListView',
                
                # Rendez-vous
                'CalendrierRendezVousView', 'RendezVousListView', 'RendezVousDuJourView'
            ],
            'LABORANTIN': [
                # Dashboard
                'DashboardView', 'index',
                
                # Examens
                'ExamenListView', 'ExamenDetailView', 'ResultatExamenCreateView', 
                'ResultatExamenView', 'resultat_create'
            ],
            'PHARMACIEN': [
                # Dashboard
                'DashboardView', 'index',
                
                # Pharmacie
                'MedicamentListView', 'MedicamentCreateView', 'StockView', 
                'MouvementStockCreateView', 'MouvementStockListView', 'POSView',
                'medicament_create', 'stock_update', 'pos_vente',
                
                # Prescriptions
                'PrescriptionListView', 'PrescriptionDetailView', 'PrescriptionPrintView',
                
                # Facturation liée à la pharmacie
                'FactureListView'
            ],
            'RECEPTION': [
                # Dashboard
                'DashboardView', 'index',
                
                # Patients
                'PatientListView', 'PatientDetailView', 'PatientCreateView', 
                'PatientUpdateView', 'PatientSearchView', 'patient_create',
                
                # Rendez-vous
                'CalendrierRendezVousView', 'RendezVousListView', 'RendezVousCreateView', 
                'RendezVousUpdateView', 'RendezVousDuJourView', 'rendez_vous_create',
                
                # Facturation
                'FactureListView', 'FactureCreateView', 'FactureDetailView', 
                'FacturePrintView', 'PaiementCreateView', 'facture_create', 'facture_print'
            ]
        }
        
        # Les URL spécifiques qui sont accessibles à certains rôles
        # Ceci est un niveau supplémentaire de contrôle pour des URL précises
        url_permissions = {
            'ADMIN': [],  # Accès complet aux administrateurs
            'MEDECIN': [
                '/patients/',
                '/dossiers/',
                '/rendezvous/',
                '/examens/',
                '/prescriptions/'
            ],
            'INFIRMIER': [
                '/patients/',
                '/dossiers/',
                '/rendezvous/'
            ],
            'LABORANTIN': [
                '/examens/'
            ],
            'PHARMACIEN': [
                '/pharmacie/',
                '/prescriptions/',
                '/facturation/liste/'
            ],
            'RECEPTION': [
                '/patients/',
                '/rendezvous/',
                '/facturation/'
            ]
        }
        
        # 1. Vérification basée sur le nom de la vue
        if role == 'ADMIN':
            return None  # Accès total pour les administrateurs
        
        # Pour les autres rôles, vérifier si la vue est dans la liste des vues autorisées
        if view_permissions.get(role) and (view_name in view_permissions[role] or view_class in view_permissions[role]):
            return None  # Accès autorisé
        
        # 2. Vérification basée sur l'URL si la vérification par vue a échoué
        if url_permissions.get(role) and any(path.startswith(url) for url in url_permissions[role]):
            return None  # Accès autorisé
        
        # Si nous arrivons ici, l'accès est refusé
        logger.warning(f"Accès refusé: Utilisateur {request.user.username} ({role}) a tenté d'accéder à {path}")
        messages.error(request, "Vous n'avez pas les permissions nécessaires pour accéder à cette page.")
        
        # Rediriger vers le tableau de bord ou la page d'accueil
        return redirect('dashboard')


# Décorateurs et Mixins pour un contrôle d'accès plus précis
from django.contrib.auth.decorators import user_passes_test
from functools import wraps
from django.contrib.auth.mixins import UserPassesTestMixin

def role_required(roles):
    """
    Décorateur pour restreindre l'accès aux vues basées sur des fonctions.
    Utilisation: @role_required(['ADMIN', 'MEDECIN'])
    
    Args:
        roles: Liste des rôles autorisés à accéder à la vue
    """
    def check_role(user):
        if user.is_superuser:
            return True
        try:
            return user.personnel.role in roles
        except AttributeError:
            return False
    
    return user_passes_test(check_role, login_url=settings.LOGIN_URL)


class RoleRequiredMixin(UserPassesTestMixin):
    """
    Mixin pour restreindre l'accès aux vues basées sur des classes.
    Utilisation:
    
    class MaVue(RoleRequiredMixin, ListView):
        roles_allowed = ['ADMIN', 'MEDECIN']
    """
    roles_allowed = []
    
    def test_func(self):
        user = self.request.user
        if user.is_superuser:
            return True
        try:
            return user.personnel.role in self.roles_allowed
        except AttributeError:
            return False
            
    def handle_no_permission(self):
        messages.error(self.request, "Vous n'avez pas les permissions nécessaires pour accéder à cette page.")
        return redirect('dashboard')