from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.views.generic import DetailView, CreateView, ListView
from django.urls import reverse_lazy, reverse
from django.utils import timezone
from django.http import HttpResponseRedirect
from django.db.models import Q

from ..models import Patient, DossierMedical, ConsultationMedicale
from forms.forms import ConsultationForm
from ..middleware.access_middleware import role_required, RoleRequiredMixin


class DossierMedicalView(RoleRequiredMixin, DetailView):
    """
    Vue pour consulter un dossier médical complet.
    Accessible aux médecins, infirmiers et administrateurs.
    """
    model = DossierMedical
    template_name = 'dossiers/dossier.html'
    context_object_name = 'dossier'
    roles_allowed = ['ADMIN', 'MEDECIN', 'INFIRMIER']
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        dossier = self.get_object()
        
        # Informations sur le patient
        context['patient'] = dossier.patient
        
        # Historique des consultations triées par date (les plus récentes d'abord)
        context['consultations'] = dossier.consultations.all().order_by('-date_consultation')
        
        # Vérifier si l'utilisateur est un médecin pour les permissions
        try:
            role = self.request.user.personnel.role
            context['is_medecin'] = role in ['ADMIN', 'MEDECIN']
        except:
            context['is_medecin'] = self.request.user.is_superuser
        
        return context


class ConsultationCreateView(RoleRequiredMixin, CreateView):
    """
    Vue pour créer une nouvelle consultation médicale.
    Accessible uniquement aux médecins et administrateurs.
    """
    model = ConsultationMedicale
    form_class = ConsultationForm
    template_name = 'dossiers/consultation_form.html'
    roles_allowed = ['ADMIN', 'MEDECIN']
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Récupérer le dossier médical
        dossier_id = self.kwargs.get('dossier_id')
        dossier = get_object_or_404(DossierMedical, id=dossier_id)
        context['dossier'] = dossier
        context['patient'] = dossier.patient
        context['titre'] = 'Nouvelle consultation'
        return context
    
    def form_valid(self, form):
        # Associer le médecin actuel
        form.instance.medecin = self.request.user.personnel
        
        # Associer le dossier médical
        dossier_id = self.kwargs.get('dossier_id')
        dossier = get_object_or_404(DossierMedical, id=dossier_id)
        form.instance.dossier = dossier
        
        # Définir la date de consultation
        if not form.instance.date_consultation:
            form.instance.date_consultation = timezone.now()
        
        # Sauvegarder
        response = super().form_valid(form)
        messages.success(self.request, "La consultation a été enregistrée avec succès.")
        return response
    
    def get_success_url(self):
        # Rediriger vers la vue détaillée de la consultation
        return reverse('consultation_detail', kwargs={'pk': self.object.pk})


class ConsultationDetailView(RoleRequiredMixin, DetailView):
    """
    Vue pour consulter les détails d'une consultation médicale.
    Accessible aux médecins, infirmiers et administrateurs.
    """
    model = ConsultationMedicale
    template_name = 'dossiers/consultation_detail.html'
    context_object_name = 'consultation'
    roles_allowed = ['ADMIN', 'MEDECIN', 'INFIRMIER']
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        consultation = self.get_object()
        
        # Informations sur le patient et le dossier
        context['patient'] = consultation.dossier.patient
        context['dossier'] = consultation.dossier
        
        # Vérifier si l'utilisateur est un médecin pour les permissions
        try:
            role = self.request.user.personnel.role
            context['is_medecin'] = role in ['ADMIN', 'MEDECIN']
            # Pour permettre au médecin qui a créé la consultation de la modifier
            context['is_author'] = (role in ['ADMIN', 'MEDECIN']) and (consultation.medecin == self.request.user.personnel)
        except:
            context['is_medecin'] = self.request.user.is_superuser
            context['is_author'] = self.request.user.is_superuser
        
        # Récupérer les prescriptions liées à cette consultation
        context['prescriptions'] = consultation.prescriptions.all()
        
        return context


class ConsultationListView(RoleRequiredMixin, ListView):
    """
    Vue pour afficher la liste des consultations.
    Accessible aux médecins, infirmiers et administrateurs.
    """
    model = ConsultationMedicale
    template_name = 'dossiers/consultation_liste.html'
    context_object_name = 'consultations'
    paginate_by = 15
    ordering = ['-date_consultation']
    roles_allowed = ['ADMIN', 'MEDECIN', 'INFIRMIER']
    
    def get_queryset(self):
        queryset = super().get_queryset()
        
        # Filtrer par patient si spécifié
        patient_id = self.kwargs.get('patient_id')
        if patient_id:
            queryset = queryset.filter(dossier__patient__id=patient_id)
        
        # Filtrer par médecin si l'utilisateur est un médecin
        try:
            if self.request.user.personnel.role == 'MEDECIN':
                queryset = queryset.filter(medecin=self.request.user.personnel)
        except:
            pass
        
        # Filtrer par recherche si spécifié
        query = self.request.GET.get('q')
        if query:
            queryset = queryset.filter(
                Q(motif__icontains=query) | 
                Q(diagnostic__icontains=query) | 
                Q(dossier__patient__nom__icontains=query) |
                Q(dossier__patient__prenom__icontains=query)
            )
        
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Filtrer par patient si spécifié
        patient_id = self.kwargs.get('patient_id')
        if patient_id:
            patient = get_object_or_404(Patient, id=patient_id)
            context['patient'] = patient
            context['filtered_by_patient'] = True
        
        # Vérifier si l'utilisateur est un médecin pour les permissions
        try:
            role = self.request.user.personnel.role
            context['is_medecin'] = role in ['ADMIN', 'MEDECIN']
        except:
            context['is_medecin'] = self.request.user.is_superuser
        
        # Informations pour la recherche
        context['query'] = self.request.GET.get('q', '')
        
        return context


@login_required
@role_required(['ADMIN', 'MEDECIN'])
def consultation_create(request, patient_id):
    """
    Vue fonctionnelle pour créer une consultation depuis la fiche patient.
    Accessible uniquement aux médecins et administrateurs.
    """
    # Récupérer le patient et son dossier médical
    patient = get_object_or_404(Patient, id=patient_id)
    
    # Vérifier si le dossier existe, sinon le créer
    dossier, created = DossierMedical.objects.get_or_create(patient=patient)
    
    if request.method == 'POST':
        form = ConsultationForm(request.POST)
        if form.is_valid():
            consultation = form.save(commit=False)
            consultation.medecin = request.user.personnel
            consultation.dossier = dossier
            consultation.date_consultation = timezone.now()
            consultation.save()
            
            messages.success(request, "La consultation a été enregistrée avec succès.")
            return redirect('consultation_detail', pk=consultation.id)
    else:
        form = ConsultationForm()
    
    context = {
        'form': form,
        'patient': patient,
        'dossier': dossier,
        'titre': 'Nouvelle consultation'
    }
    
    return render(request, 'dossiers/consultation_form.html', context)


@login_required
@role_required(['ADMIN', 'MEDECIN'])
def consultation_update(request, pk):
    """
    Vue fonctionnelle pour modifier une consultation existante.
    Accessible uniquement aux médecins et administrateurs,
    et uniquement le médecin qui a créé la consultation peut la modifier.
    """
    consultation = get_object_or_404(ConsultationMedicale, id=pk)
    
    # Vérifier si l'utilisateur est autorisé à modifier cette consultation
    is_author = (consultation.medecin == request.user.personnel)
    is_admin = (request.user.personnel.role == 'ADMIN' or request.user.is_superuser)
    
    if not (is_author or is_admin):
        messages.error(request, "Vous n'êtes pas autorisé à modifier cette consultation.")
        return redirect('consultation_detail', pk=consultation.id)
    
    if request.method == 'POST':
        form = ConsultationForm(request.POST, instance=consultation)
        if form.is_valid():
            form.save()
            messages.success(request, "La consultation a été mise à jour avec succès.")
            return redirect('consultation_detail', pk=consultation.id)
    else:
        form = ConsultationForm(instance=consultation)
    
    context = {
        'form': form,
        'patient': consultation.dossier.patient,
        'dossier': consultation.dossier,
        'consultation': consultation,
        'titre': 'Modifier la consultation',
        'is_update': True
    }
    
    return render(request, 'dossiers/consultation_form.html', context)