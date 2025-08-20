from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.views.generic import ListView, DetailView, CreateView, UpdateView, View
from django.urls import reverse_lazy, reverse
from django.utils import timezone
from django.db.models import Q
from django.http import JsonResponse

from datetime import datetime, timedelta
import calendar
from ..models import RendezVous, Patient, Personnel
from ..forms import RendezVousForm
from ..middleware.access_middleware import role_required, RoleRequiredMixin


class CalendrierRendezVousView(RoleRequiredMixin, View):
    """
    Vue pour afficher le calendrier des rendez-vous.
    Accessible aux médecins, infirmiers, réceptionnistes et administrateurs.
    """
    template_name = 'rendezvous/calendrier.html'
    roles_allowed = ['ADMIN', 'MEDECIN', 'INFIRMIER', 'RECEPTION']
    
    def get(self, request):
        # Récupérer le mois/année à afficher
        year = int(request.GET.get('year', timezone.now().year))
        month = int(request.GET.get('month', timezone.now().month))
        
        # Récupérer le filtre médecin si présent
        medecin_id = request.GET.get('medecin')
        
        # Calculer les dates de début et fin du mois
        cal = calendar.monthcalendar(year, month)
        first_day = datetime(year, month, 1)
        
        # Trouver le dernier jour du mois
        if month == 12:
            last_day = datetime(year + 1, 1, 1) - timedelta(days=1)
        else:
            last_day = datetime(year, month + 1, 1) - timedelta(days=1)
        
        # Récupérer tous les rendez-vous du mois
        rdvs = RendezVous.objects.filter(
            date_heure__gte=first_day,
            date_heure__lt=datetime(last_day.year, last_day.month, last_day.day) + timedelta(days=1)
        )
        
        # Filtrer par médecin si demandé
        if medecin_id:
            rdvs = rdvs.filter(medecin_id=medecin_id)
        
        # Si l'utilisateur est un médecin, montrer seulement ses rendez-vous
        try:
            if request.user.personnel.role == 'MEDECIN':
                rdvs = rdvs.filter(medecin=request.user.personnel)
        except:
            pass
        
        # Organiser les rendez-vous par date
        rdvs_by_date = {}
        for rdv in rdvs:
            date_key = rdv.date_heure.strftime('%Y-%m-%d')
            if date_key not in rdvs_by_date:
                rdvs_by_date[date_key] = []
            rdvs_by_date[date_key].append(rdv)
        
        # Liste des médecins pour le filtre
        medecins = Personnel.objects.filter(role='MEDECIN').order_by('user__last_name')
        
        # Préparer le contexte
        context = {
            'year': year,
            'month': month,
            'month_name': calendar.month_name[month],
            'calendar': cal,
            'rdvs_by_date': rdvs_by_date,
            'medecins': medecins,
            'selected_medecin': medecin_id,
            'prev_month': (month - 1) if month > 1 else 12,
            'prev_year': year if month > 1 else year - 1,
            'next_month': (month + 1) if month < 12 else 1,
            'next_year': year if month < 12 else year + 1,
        }
        
        return render(request, self.template_name, context)


class RendezVousListView(RoleRequiredMixin, ListView):
    """
    Vue pour afficher la liste des rendez-vous.
    Accessible aux médecins, infirmiers, réceptionnistes et administrateurs.
    """
    model = RendezVous
    template_name = 'rendezvous/liste.html'
    context_object_name = 'rendez_vous'
    paginate_by = 15
    roles_allowed = ['ADMIN', 'MEDECIN', 'INFIRMIER', 'RECEPTION']
    
    def get_queryset(self):
        queryset = super().get_queryset()
        
        # Filtrer par date si spécifiée
        date_filtre = self.request.GET.get('date')
        if date_filtre:
            try:
                date_obj = datetime.strptime(date_filtre, '%Y-%m-%d').date()
                queryset = queryset.filter(date_heure__date=date_obj)
            except ValueError:
                pass
        
        # Filtrer par statut si spécifié
        statut = self.request.GET.get('statut')
        if statut:
            queryset = queryset.filter(statut=statut)
        
        # Filtrer par médecin si spécifié
        medecin_id = self.request.GET.get('medecin')
        if medecin_id:
            queryset = queryset.filter(medecin_id=medecin_id)
        
        # Filtrer par patient si spécifié
        patient_id = self.request.GET.get('patient')
        if patient_id:
            queryset = queryset.filter(patient_id=patient_id)
        
        # Si l'utilisateur est un médecin, montrer seulement ses rendez-vous
        try:
            if self.request.user.personnel.role == 'MEDECIN':
                queryset = queryset.filter(medecin=self.request.user.personnel)
        except:
            pass
        
        # Filtrer par recherche si spécifiée
        query = self.request.GET.get('q')
        if query:
            queryset = queryset.filter(
                Q(patient__nom__icontains=query) | 
                Q(patient__prenom__icontains=query) | 
                Q(motif__icontains=query)
            )
        
        # Trier par date et heure (par défaut, les prochains rendez-vous d'abord)
        return queryset.order_by('date_heure')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Ajouter les filtres au contexte
        context['date_filtre'] = self.request.GET.get('date', '')
        context['statut_filtre'] = self.request.GET.get('statut', '')
        context['medecin_filtre'] = self.request.GET.get('medecin', '')
        context['patient_filtre'] = self.request.GET.get('patient', '')
        context['query'] = self.request.GET.get('q', '')
        
        # Listes pour les filtres dropdown
        context['statuts'] = RendezVous.STATUS_CHOICES
        context['medecins'] = Personnel.objects.filter(role='MEDECIN').order_by('user__last_name')
        
        # Vérifier le rôle de l'utilisateur pour les permissions
        try:
            role = self.request.user.personnel.role
            context['can_create'] = role in ['ADMIN', 'RECEPTION', 'MEDECIN']
            context['can_edit'] = role in ['ADMIN', 'RECEPTION', 'MEDECIN']
        except:
            context['can_create'] = self.request.user.is_superuser
            context['can_edit'] = self.request.user.is_superuser
        
        return context


class RendezVousCreateView(RoleRequiredMixin, CreateView):
    """
    Vue pour créer un nouveau rendez-vous.
    Accessible aux médecins, réceptionnistes et administrateurs.
    """
    model = RendezVous
    form_class = RendezVousForm
    template_name = 'rendezvous/formulaire.html'
    roles_allowed = ['ADMIN', 'RECEPTION', 'MEDECIN']
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['titre'] = 'Nouveau rendez-vous'
        context['action'] = 'Créer'
        
        # Préselectionner le patient si spécifié dans l'URL
        patient_id = self.request.GET.get('patient')
        if patient_id:
            try:
                patient = Patient.objects.get(pk=patient_id)
                context['patient_preselectionne'] = patient
            except Patient.DoesNotExist:
                pass
        
        # Préselectionner le médecin si l'utilisateur est un médecin
        try:
            if self.request.user.personnel.role == 'MEDECIN':
                context['medecin_preselectionne'] = self.request.user.personnel
        except:
            pass
        
        return context
    
    def get_initial(self):
        initial = super().get_initial()
        
        # Préselectionner le patient si spécifié dans l'URL
        patient_id = self.request.GET.get('patient')
        if patient_id:
            initial['patient'] = patient_id
        
        # Préselectionner le médecin si l'utilisateur est un médecin
        try:
            if self.request.user.personnel.role == 'MEDECIN':
                initial['medecin'] = self.request.user.personnel.id
        except:
            pass
        
        return initial
    
    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, "Le rendez-vous a été créé avec succès.")
        return response
    
    def get_success_url(self):
        # Rediriger vers la vue détaillée du rendez-vous ou la liste
        if 'stay' in self.request.POST:
            # Si l'utilisateur a cliqué sur "Enregistrer et ajouter un autre"
            return reverse('rendezvous_create')
        else:
            # Par défaut, rediriger vers la liste des rendez-vous
            return reverse('rendezvous_list')


class RendezVousUpdateView(RoleRequiredMixin, UpdateView):
    """
    Vue pour modifier un rendez-vous existant.
    Accessible aux médecins, réceptionnistes et administrateurs.
    """
    model = RendezVous
    form_class = RendezVousForm
    template_name = 'rendezvous/formulaire.html'
    roles_allowed = ['ADMIN', 'RECEPTION', 'MEDECIN']
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['titre'] = 'Modifier le rendez-vous'
        context['action'] = 'Enregistrer'
        context['is_update'] = True
        return context
    
    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, "Le rendez-vous a été mis à jour avec succès.")
        return response
    
    def get_success_url(self):
        # Rediriger vers la liste des rendez-vous ou le calendrier
        return_to = self.request.GET.get('return_to', 'list')
        if return_to == 'calendar':
            return reverse('rendezvous_calendrier')
        else:
            return reverse('rendezvous_list')


class RendezVousDuJourView(RoleRequiredMixin, ListView):
    """
    Vue pour afficher les rendez-vous du jour.
    Accessible aux médecins, infirmiers, réceptionnistes et administrateurs.
    """
    model = RendezVous
    template_name = 'rendezvous/jour.html'
    context_object_name = 'rendez_vous'
    roles_allowed = ['ADMIN', 'MEDECIN', 'INFIRMIER', 'RECEPTION']
    
    def get_queryset(self):
        # Date par défaut : aujourd'hui
        date = self.request.GET.get('date')
        if date:
            try:
                date_obj = datetime.strptime(date, '%Y-%m-%d').date()
            except ValueError:
                date_obj = timezone.now().date()
        else:
            date_obj = timezone.now().date()
        
        # Filtrer les rendez-vous pour cette date
        queryset = RendezVous.objects.filter(
            date_heure__date=date_obj
        )
        
        # Si l'utilisateur est un médecin, montrer seulement ses rendez-vous
        try:
            if self.request.user.personnel.role == 'MEDECIN':
                queryset = queryset.filter(medecin=self.request.user.personnel)
        except:
            pass
        
        # Trier par heure
        return queryset.order_by('date_heure')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Date affichée
        date = self.request.GET.get('date')
        if date:
            try:
                context['date_affichee'] = datetime.strptime(date, '%Y-%m-%d').date()
            except ValueError:
                context['date_affichee'] = timezone.now().date()
        else:
            context['date_affichee'] = timezone.now().date()
        
        # Calculer dates précédente et suivante pour la navigation
        date_affichee = context['date_affichee']
        context['date_precedente'] = date_affichee - timedelta(days=1)
        context['date_suivante'] = date_affichee + timedelta(days=1)
        
        # Vérifier si c'est aujourd'hui
        context['is_today'] = (date_affichee == timezone.now().date())
        
        # Regrouper les rendez-vous par heure
        rdv_par_heure = {}
        for rdv in self.object_list:
            heure = rdv.date_heure.strftime('%H:%M')
            if heure not in rdv_par_heure:
                rdv_par_heure[heure] = []
            rdv_par_heure[heure].append(rdv)
        
        context['rdv_par_heure'] = rdv_par_heure
        
        # Vérifier le rôle de l'utilisateur pour les permissions
        try:
            role = self.request.user.personnel.role
            context['can_create'] = role in ['ADMIN', 'RECEPTION', 'MEDECIN']
            context['can_edit'] = role in ['ADMIN', 'RECEPTION', 'MEDECIN']
        except:
            context['can_create'] = self.request.user.is_superuser
            context['can_edit'] = self.request.user.is_superuser
        
        return context


@login_required
@role_required(['ADMIN', 'RECEPTION', 'MEDECIN'])
def rendez_vous_create(request, patient_id=None):
    """
    Vue fonctionnelle pour créer un rendez-vous.
    Alternative à la vue basée sur classe.
    """
    if request.method == 'POST':
        form = RendezVousForm(request.POST)
        if form.is_valid():
            rendez_vous = form.save()
            messages.success(request, "Le rendez-vous a été créé avec succès.")
            
            # Redirection selon le bouton cliqué
            if 'stay' in request.POST:
                return redirect('rendezvous_create')
            else:
                return redirect('rendezvous_list')
    else:
        initial = {}
        
        # Préselectionner le patient si fourni
        if patient_id:
            try:
                patient = Patient.objects.get(pk=patient_id)
                initial['patient'] = patient
            except Patient.DoesNotExist:
                pass
        
        # Préselectionner le médecin si l'utilisateur est un médecin
        try:
            if request.user.personnel.role == 'MEDECIN':
                initial['medecin'] = request.user.personnel
        except:
            pass
        
        form = RendezVousForm(initial=initial)
    
    context = {
        'form': form,
        'titre': 'Nouveau rendez-vous',
        'action': 'Créer',
        'patient_id': patient_id
    }
    
    return render(request, 'rendezvous/formulaire.html', context)


@login_required
@role_required(['ADMIN', 'RECEPTION', 'MEDECIN'])
def rendez_vous_update_status(request, pk):
    """
    Vue fonctionnelle pour mettre à jour le statut d'un rendez-vous.
    Utilisé pour les actions rapides (marquer comme terminé, annulé, etc.)
    """
    if request.method == 'POST':
        rendez_vous = get_object_or_404(RendezVous, pk=pk)
        nouveau_statut = request.POST.get('statut')
        
        if nouveau_statut in dict(RendezVous.STATUS_CHOICES).keys():
            rendez_vous.statut = nouveau_statut
            rendez_vous.save()
            
            # Si c'est une requête AJAX, renvoyer un JSON
            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                return JsonResponse({
                    'success': True,
                    'message': f"Statut mis à jour : {rendez_vous.get_statut_display()}"
                })
            
            messages.success(request, f"Le statut du rendez-vous a été mis à jour : {rendez_vous.get_statut_display()}")
        else:
            # Si c'est une requête AJAX, renvoyer un JSON d'erreur
            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                return JsonResponse({
                    'success': False,
                    'message': "Statut invalide"
                }, status=400)
            
            messages.error(request, "Statut invalide")
    
    # Rediriger selon le paramètre return_to
    return_to = request.GET.get('return_to', 'list')
    if return_to == 'calendar':
        return redirect('rendezvous_calendrier')
    elif return_to == 'day':
        return redirect('rendezvous_jour')
    else:
        return redirect('rendezvous_list')


@login_required
@role_required(['ADMIN', 'MEDECIN', 'INFIRMIER', 'RECEPTION'])
def check_disponibilite(request):
    """
    Vue API pour vérifier la disponibilité d'un médecin à une date/heure donnée.
    Utilisé pour l'interface de prise de rendez-vous en AJAX.
    """
    if request.method == 'GET' and request.headers.get('x-requested-with') == 'XMLHttpRequest':
        medecin_id = request.GET.get('medecin')
        date_str = request.GET.get('date')
        heure_str = request.GET.get('heure')
        duree = int(request.GET.get('duree', 30))
        rdv_id = request.GET.get('rdv_id')  # Pour exclure le RDV en cours d'édition
        
        if not (medecin_id and date_str and heure_str):
            return JsonResponse({
                'disponible': False,
                'message': "Paramètres manquants"
            }, status=400)
        
        try:
            # Construire la date et l'heure
            date_heure = datetime.strptime(f"{date_str} {heure_str}", '%Y-%m-%d %H:%M')
            fin_rdv = date_heure + timedelta(minutes=duree)
            
            # Vérifier si la date est dans le passé
            if date_heure < timezone.now():
                return JsonResponse({
                    'disponible': False,
                    'message': "La date est dans le passé"
                })
            
            # Vérifier les conflits avec d'autres rendez-vous
            conflits = RendezVous.objects.filter(
                medecin_id=medecin_id,
                date_heure__lt=fin_rdv,
                statut__in=['PLANIFIE', 'CONFIRME']
            )
            
            # Exclure le RDV en cours d'édition
            if rdv_id:
                conflits = conflits.exclude(pk=rdv_id)
            
            for rdv in conflits:
                fin_existant = rdv.date_heure + timedelta(minutes=rdv.duree)
                if fin_existant > date_heure:
                    return JsonResponse({
                        'disponible': False,
                        'message': f"Le médecin a déjà un rendez-vous à cette heure avec {rdv.patient.nom} {rdv.patient.prenom}"
                    })
            
            # Si on arrive ici, c'est que la plage est disponible
            return JsonResponse({
                'disponible': True,
                'message': "Plage horaire disponible"
            })
            
        except ValueError:
            return JsonResponse({
                'disponible': False,
                'message': "Format de date ou heure invalide"
            }, status=400)
        except Exception as e:
            return JsonResponse({
                'disponible': False,
                'message': str(e)
            }, status=500)
    
    return JsonResponse({
        'disponible': False,
        'message': "Méthode non autorisée"
    }, status=405)