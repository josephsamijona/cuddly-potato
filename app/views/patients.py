from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.views.generic import ListView, DetailView, CreateView, UpdateView
from django.urls import reverse_lazy, reverse
from django.db.models import Q
from django.utils import timezone
from django.http import JsonResponse

from ..models import Patient, DossierMedical, ConsultationMedicale, RendezVous, ExamenLaboratoire, Prescription
from ..forms import PatientForm, PatientSearchForm
from ..middleware.access_middleware import role_required, RoleRequiredMixin


class PatientListView(RoleRequiredMixin, ListView):
    """Vue pour afficher la liste des patients"""
    model = Patient
    template_name = 'patients/liste.html'
    context_object_name = 'patients'
    paginate_by = 15
    ordering = ['-date_enregistrement']
    roles_allowed = ['ADMIN', 'MEDECIN', 'INFIRMIER', 'RECEPTION']
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['search_form'] = PatientSearchForm()
        context['total_patients'] = Patient.objects.count()
        
        # Vérifier s'il existe un filtre
        query = self.request.GET.get('q')
        if query:
            context['query'] = query
            
        return context
    
    def get_queryset(self):
        queryset = super().get_queryset()
        
        # Filtrer par terme de recherche si présent
        query = self.request.GET.get('q')
        if query:
            queryset = queryset.filter(
                Q(nom__icontains=query) | 
                Q(prenom__icontains=query) | 
                Q(id_patient__icontains=query) |
                Q(telephone__icontains=query)
            )
            
        return queryset


class PatientDetailView(RoleRequiredMixin, DetailView):
    """Vue pour afficher les détails d'un patient"""
    model = Patient
    template_name = 'patients/fiche.html'
    context_object_name = 'patient'
    roles_allowed = ['ADMIN', 'MEDECIN', 'INFIRMIER', 'RECEPTION']
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        patient = self.get_object()
        
        # Vérifier si le patient a un dossier médical
        try:
            dossier = patient.dossier_medical
            context['dossier_medical'] = dossier
            
            # Consultations médicales
            context['consultations'] = ConsultationMedicale.objects.filter(
                dossier=dossier
            ).order_by('-date_consultation')[:5]
            
        except DossierMedical.DoesNotExist:
            context['dossier_medical'] = None
            context['consultations'] = []
        
        # Rendez-vous
        context['rendez_vous'] = RendezVous.objects.filter(
            patient=patient
        ).order_by('-date_heure')[:5]
        
        # Prochains rendez-vous
        context['prochains_rdv'] = RendezVous.objects.filter(
            patient=patient,
            date_heure__gte=timezone.now()
        ).order_by('date_heure')[:3]
        
        # Examens de laboratoire
        context['examens'] = ExamenLaboratoire.objects.filter(
            patient=patient
        ).order_by('-date_demande')[:5]
        
        # Prescriptions
        context['prescriptions'] = Prescription.objects.filter(
            patient=patient
        ).order_by('-date_prescription')[:5]
        
        # Accès aux fonctionnalités selon le rôle
        try:
            role = self.request.user.personnel.role
            context['can_edit'] = role in ['ADMIN', 'RECEPTION']
            context['is_medecin'] = role == 'MEDECIN'
        except:
            context['can_edit'] = self.request.user.is_superuser
            context['is_medecin'] = False
            
        return context


class PatientCreateView(RoleRequiredMixin, CreateView):
    """Vue pour créer un nouveau patient"""
    model = Patient
    form_class = PatientForm
    template_name = 'patients/formulaire.html'
    success_url = reverse_lazy('patient_list')
    roles_allowed = ['ADMIN', 'RECEPTION']
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['titre'] = 'Ajouter un nouveau patient'
        context['action'] = 'Créer'
        return context
    
    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, f"Le patient {form.instance.nom} {form.instance.prenom} a été créé avec succès.")
        
        # Créer automatiquement un dossier médical pour le patient
        DossierMedical.objects.create(patient=self.object)
        
        return response


class PatientUpdateView(RoleRequiredMixin, UpdateView):
    """Vue pour modifier les informations d'un patient"""
    model = Patient
    form_class = PatientForm
    template_name = 'patients/formulaire.html'
    roles_allowed = ['ADMIN', 'RECEPTION']
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['titre'] = 'Modifier les informations du patient'
        context['action'] = 'Enregistrer'
        context['patient'] = self.get_object()
        return context
    
    def get_success_url(self):
        return reverse('patient_detail', kwargs={'pk': self.object.pk})
    
    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, f"Les informations du patient {form.instance.nom} {form.instance.prenom} ont été mises à jour.")
        return response


@login_required
@role_required(['ADMIN', 'MEDECIN', 'INFIRMIER', 'RECEPTION'])
def patient_search_view(request):
    """Vue pour rechercher des patients"""
    if request.method == 'GET':
        form = PatientSearchForm(request.GET)
        query = request.GET.get('query', '')
        
        if query:
            # Recherche de patients correspondant au critère
            patients = Patient.objects.filter(
                Q(nom__icontains=query) | 
                Q(prenom__icontains=query) | 
                Q(id_patient__icontains=query) |
                Q(telephone__icontains=query)
            ).order_by('nom', 'prenom')
        else:
            patients = Patient.objects.none()
            
        # Si c'est une requête AJAX, renvoyer JSON
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            data = []
            for patient in patients[:10]:  # Limiter à 10 résultats
                item = {
                    'id': patient.id,
                    'nom': patient.nom,
                    'prenom': patient.prenom,
                    'id_patient': patient.id_patient,
                    'date_naissance': patient.date_naissance.strftime('%d/%m/%Y'),
                    'url': reverse('patient_detail', kwargs={'pk': patient.id})
                }
                data.append(item)
            return JsonResponse(data, safe=False)
        
        # Sinon afficher la page de résultats
        context = {
            'form': form,
            'patients': patients,
            'query': query,
            'total_results': patients.count()
        }
        return render(request, 'patients/recherche.html', context)
    
    # Si méthode POST ou autre, rediriger vers formulaire vide
    return redirect('patient_search')


@login_required
@role_required(['ADMIN', 'RECEPTION'])
def patient_create(request):
    """Vue fonctionnelle alternative pour créer un patient"""
    if request.method == 'POST':
        form = PatientForm(request.POST)
        if form.is_valid():
            patient = form.save()
            
            # Créer un dossier médical si non existant
            DossierMedical.objects.get_or_create(patient=patient)
            
            messages.success(request, f"Le patient {patient.nom} {patient.prenom} a été ajouté avec succès.")
            return redirect('patient_detail', pk=patient.id)
    else:
        form = PatientForm()
    
    context = {
        'form': form,
        'titre': 'Ajouter un nouveau patient',
        'action': 'Créer'
    }
    return render(request, 'patients/formulaire.html', context)