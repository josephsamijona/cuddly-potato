from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.generic import ListView, DetailView, View
from django.utils.decorators import method_decorator
from django.db.models import Q
from django.contrib.auth.mixins import UserPassesTestMixin

from ..models import Personnel
from forms.forms import UserRegistrationForm, ProfileUpdateForm, PersonnelUpdateForm
from ..middleware.access_middleware import role_required, RoleRequiredMixin


class UserListView(RoleRequiredMixin, ListView):
    """
    Vue pour afficher la liste des utilisateurs du système.
    Accessible uniquement aux administrateurs.
    """
    model = User
    template_name = 'admin/user_list.html'
    context_object_name = 'users'
    paginate_by = 10
    roles_allowed = ['ADMIN']
    
    def get_queryset(self):
        queryset = super().get_queryset()
        
        # Ajouter un filtre de recherche si présent dans la requête
        search_query = self.request.GET.get('q')
        if search_query:
            queryset = queryset.filter(
                Q(username__icontains=search_query) |
                Q(first_name__icontains=search_query) |
                Q(last_name__icontains=search_query) |
                Q(email__icontains=search_query)
            )
            
        return queryset.order_by('last_name', 'first_name')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['search_query'] = self.request.GET.get('q', '')
        
        # Ajouter les informations de rôle pour chaque utilisateur
        users_with_roles = []
        for user in context['users']:
            try:
                role = user.personnel.get_role_display()
            except:
                role = "Administrateur" if user.is_superuser else "Non défini"
            
            users_with_roles.append({
                'user': user,
                'role': role
            })
        
        context['users_with_roles'] = users_with_roles
        return context


class UserDetailView(RoleRequiredMixin, DetailView):
    """
    Vue pour afficher les détails d'un utilisateur.
    Accessible uniquement aux administrateurs.
    """
    model = User
    template_name = 'admin/user_detail.html'
    context_object_name = 'user_detail'
    roles_allowed = ['ADMIN']
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        user = self.get_object()
        
        # Vérifier si l'utilisateur a un profil personnel
        try:
            personnel = user.personnel
            context['personnel'] = personnel
            context['role'] = personnel.get_role_display()
        except:
            context['personnel'] = None
            context['role'] = "Administrateur" if user.is_superuser else "Non défini"
            
        return context


class UserUpdateView(RoleRequiredMixin, View):
    """
    Vue pour modifier les informations d'un utilisateur.
    Accessible uniquement aux administrateurs.
    """
    roles_allowed = ['ADMIN']
    
    def get(self, request, pk):
        user = get_object_or_404(User, pk=pk)
        user_form = ProfileUpdateForm(instance=user)
        
        # Vérifier si l'utilisateur a un profil personnel
        try:
            personnel = user.personnel
            personnel_form = PersonnelUpdateForm(instance=personnel)
            has_personnel = True
        except Personnel.DoesNotExist:
            personnel_form = None
            has_personnel = False
        
        context = {
            'user_form': user_form,
            'personnel_form': personnel_form,
            'has_personnel': has_personnel,
            'user_detail': user
        }
        
        return render(request, 'admin/user_update.html', context)
    
    def post(self, request, pk):
        user = get_object_or_404(User, pk=pk)
        user_form = ProfileUpdateForm(request.POST, instance=user)
        
        # Vérifier si l'utilisateur a un profil personnel
        try:
            personnel = user.personnel
            personnel_form = PersonnelUpdateForm(request.POST, instance=personnel)
            has_personnel = True
        except Personnel.DoesNotExist:
            personnel_form = None
            has_personnel = False
        
        if user_form.is_valid() and (not has_personnel or personnel_form.is_valid()):
            user_form.save()
            
            if has_personnel and personnel_form:
                personnel_form.save()
            
            messages.success(request, f"Les informations de {user.username} ont été mises à jour avec succès.")
            return redirect('user_detail', pk=user.pk)
        
        context = {
            'user_form': user_form,
            'personnel_form': personnel_form,
            'has_personnel': has_personnel,
            'user_detail': user
        }
        
        return render(request, 'admin/user_update.html', context)


@login_required
@role_required(['ADMIN'])
def user_toggle_active(request, pk):
    """
    Vue pour activer/désactiver un utilisateur.
    Accessible uniquement aux administrateurs.
    """
    user = get_object_or_404(User, pk=pk)
    
    # Empêcher la désactivation de son propre compte
    if user == request.user:
        messages.error(request, "Vous ne pouvez pas désactiver votre propre compte.")
        return redirect('user_detail', pk=user.pk)
    
    # Inverser l'état actif
    user.is_active = not user.is_active
    user.save()
    
    status = "activé" if user.is_active else "désactivé"
    messages.success(request, f"L'utilisateur {user.username} a été {status} avec succès.")
    
    return redirect('user_detail', pk=user.pk)