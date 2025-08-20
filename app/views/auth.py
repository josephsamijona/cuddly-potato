from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib import messages
from django.views.generic import View
from django.utils.decorators import method_decorator
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy, reverse

from forms.forms import LoginForm, ProfileUpdateForm, PersonnelUpdateForm, UserRegistrationForm
from ..models import Personnel


def login_view(request):
    """
    Vue de connexion pour les utilisateurs du système.
    Accessible à tous les utilisateurs.
    """
    # Rediriger vers le dashboard si déjà connecté
    if request.user.is_authenticated:
        return redirect('dashboard')
    
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(request, username=username, password=password)
            
            if user is not None:
                login(request, user)
                messages.success(request, f"Bienvenue, {user.first_name} {user.last_name}")
                
                # Rediriger vers la page demandée ou le tableau de bord
                next_page = request.GET.get('next', 'dashboard')
                return redirect(next_page)
            else:
                messages.error(request, "Nom d'utilisateur ou mot de passe incorrect.")
    else:
        form = LoginForm()
    
    return render(request, 'accounts/login.html', {'form': form})


def logout_view(request):
    """
    Vue de déconnexion.
    Accessible à tous les utilisateurs connectés.
    """
    logout(request)
    messages.info(request, "Vous avez été déconnecté avec succès.")
    return redirect('login')


@method_decorator(login_required, name='dispatch')
class ProfileView(View):
    """
    Vue pour afficher et modifier le profil utilisateur.
    Accessible à tous les utilisateurs connectés.
    """
    def get(self, request):
        user_form = ProfileUpdateForm(instance=request.user)
        
        # Vérifier si l'utilisateur a un profil personnel
        try:
            personnel = request.user.personnel
            personnel_form = PersonnelUpdateForm(instance=personnel)
            role = personnel.get_role_display()
        except Personnel.DoesNotExist:
            personnel_form = None
            role = "Administrateur" if request.user.is_superuser else "Non défini"
        
        context = {
            'user_form': user_form,
            'personnel_form': personnel_form,
            'role': role
        }
        
        return render(request, 'accounts/profile.html', context)
    
    def post(self, request):
        user_form = ProfileUpdateForm(request.POST, instance=request.user)
        
        # Vérifier si l'utilisateur a un profil personnel
        try:
            personnel = request.user.personnel
            personnel_form = PersonnelUpdateForm(request.POST, instance=personnel)
            has_personnel = True
        except Personnel.DoesNotExist:
            personnel_form = None
            has_personnel = False
        
        if user_form.is_valid() and (not has_personnel or personnel_form.is_valid()):
            user_form.save()
            
            if has_personnel and personnel_form:
                personnel_form.save()
            
            messages.success(request, "Votre profil a été mis à jour avec succès.")
            return redirect('profile')
        
        context = {
            'user_form': user_form,
            'personnel_form': personnel_form,
            'role': request.user.personnel.get_role_display() if has_personnel else "Non défini"
        }
        
        return render(request, 'accounts/profile.html', context)


@login_required
def password_change_view(request):
    """
    Vue pour changer le mot de passe.
    Accessible à tous les utilisateurs connectés.
    """
    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            # Garder l'utilisateur connecté après le changement de mot de passe
            update_session_auth_hash(request, user)
            messages.success(request, "Votre mot de passe a été changé avec succès.")
            return redirect('profile')
        else:
            messages.error(request, "Veuillez corriger les erreurs ci-dessous.")
    else:
        form = PasswordChangeForm(request.user)
    
    return render(request, 'accounts/password_change.html', {'form': form})


class RegisterUserView(LoginRequiredMixin, View):
    """
    Vue pour l'enregistrement d'un nouvel utilisateur par un administrateur.
    Accessible uniquement aux administrateurs.
    """
    def get(self, request):
        # Vérifier si l'utilisateur est admin
        if not request.user.is_superuser and (not hasattr(request.user, 'personnel') or request.user.personnel.role != 'ADMIN'):
            messages.error(request, "Vous n'avez pas les permissions nécessaires pour créer un utilisateur.")
            return redirect('dashboard')
        
        form = UserRegistrationForm()
        return render(request, 'accounts/register.html', {'form': form})
    
    def post(self, request):
        # Vérifier si l'utilisateur est admin
        if not request.user.is_superuser and (not hasattr(request.user, 'personnel') or request.user.personnel.role != 'ADMIN'):
            messages.error(request, "Vous n'avez pas les permissions nécessaires pour créer un utilisateur.")
            return redirect('dashboard')
        
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            messages.success(request, f"L'utilisateur {user.username} a été créé avec succès.")
            return redirect('user_list')  # Rediriger vers la liste des utilisateurs
        
        return render(request, 'accounts/register.html', {'form': form})