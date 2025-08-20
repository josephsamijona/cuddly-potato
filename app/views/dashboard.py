from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.db.models import Count, Sum, Q, F
from django.views.generic import View
from django.utils.decorators import method_decorator

from datetime import timedelta
from ..models import (
    Patient, RendezVous, ConsultationMedicale, ExamenLaboratoire,
    Facture, StockMedicament, MouvementStock, Prescription
)

@method_decorator(login_required, name='dispatch')
class DashboardView(View):
    """
    Vue du tableau de bord principal, adaptée selon le rôle de l'utilisateur.
    Accessible à tous les utilisateurs connectés.
    """
    template_name = 'dashboard.html'
    
    def get(self, request):
        # Date d'aujourd'hui et période récente pour les statistiques
        today = timezone.now().date()
        start_week = today - timedelta(days=today.weekday())
        end_week = start_week + timedelta(days=6)
        start_month = today.replace(day=1)
        
        # Informations générales disponibles pour tous les rôles
        context = {
            'today': today,
            'start_week': start_week,
            'end_week': end_week,
        }
        
        # Récupérer le rôle de l'utilisateur
        try:
            role = request.user.personnel.role
        except:
            # Si c'est un superadmin sans profil personnel
            if request.user.is_superuser:
                role = 'ADMIN'
            else:
                # Cas rare: utilisateur sans profil ni droits admin
                context['error_message'] = "Votre compte n'a pas de rôle attribué. Contactez l'administrateur."
                return render(request, self.template_name, context)
        
        # Ajouter le rôle au contexte
        context['role'] = role
        
        # ========================================
        # Données spécifiques pour chaque rôle
        # ========================================
        
        # Admin: Vue globale du système
        if role == 'ADMIN':
            # Statistiques patients
            context['total_patients'] = Patient.objects.count()
            context['nouveaux_patients_mois'] = Patient.objects.filter(
                date_enregistrement__gte=start_month
            ).count()
            
            # Statistiques rendez-vous
            context['rdv_aujourdhui'] = RendezVous.objects.filter(
                date_heure__date=today
            ).count()
            context['rdv_semaine'] = RendezVous.objects.filter(
                date_heure__date__range=[start_week, end_week]
            ).count()
            
            # Statistiques consultations
            context['consultations_aujourd_hui'] = ConsultationMedicale.objects.filter(
                date_consultation__date=today
            ).count()
            context['consultations_semaine'] = ConsultationMedicale.objects.filter(
                date_consultation__date__range=[start_week, end_week]
            ).count()
            
            # Statistiques examens
            context['examens_en_attente'] = ExamenLaboratoire.objects.filter(
                statut='DEMANDE'
            ).count()
            context['examens_en_cours'] = ExamenLaboratoire.objects.filter(
                statut='EN_COURS'
            ).count()
            
            # Statistiques facturation
            context['factures_non_payees'] = Facture.objects.filter(
                statut='EN_ATTENTE'
            ).count()
            total_factures = Facture.objects.filter(
                date_emission__date__gte=start_month, 
                statut='PAYEE'
            ).aggregate(total=Sum('montant_total'))
            context['revenu_mois'] = total_factures['total'] or 0
            
            # Alertes stock
            context['produits_stock_bas'] = StockMedicament.objects.filter(
                quantite__lte=F('seuil_alerte')
            ).count()
            
            # Récupérer les dernières activités
            context['derniers_patients'] = Patient.objects.order_by('-date_enregistrement')[:5]
            context['derniers_rdv'] = RendezVous.objects.filter(
                date_heure__date__gte=today
            ).order_by('date_heure')[:5]
            context['dernieres_factures'] = Facture.objects.order_by('-date_emission')[:5]
        
        # Médecin: Consultations, rendez-vous et patients
        elif role == 'MEDECIN':
            # ID du médecin connecté
            medecin_id = request.user.personnel.id
            
            # Rendez-vous du médecin
            context['rdv_aujourdhui'] = RendezVous.objects.filter(
                medecin_id=medecin_id,
                date_heure__date=today
            ).order_by('date_heure')
            
            context['rdv_a_venir'] = RendezVous.objects.filter(
                medecin_id=medecin_id,
                date_heure__date__gt=today,
                date_heure__date__lte=end_week
            ).order_by('date_heure')
            
            # Statistiques consultations
            context['consultations_aujourd_hui'] = ConsultationMedicale.objects.filter(
                medecin_id=medecin_id,
                date_consultation__date=today
            ).count()
            
            context['consultations_semaine'] = ConsultationMedicale.objects.filter(
                medecin_id=medecin_id,
                date_consultation__date__range=[start_week, end_week]
            ).count()
            
            # Examens demandés
            context['examens_en_attente'] = ExamenLaboratoire.objects.filter(
                medecin_demandeur_id=medecin_id,
                statut__in=['DEMANDE', 'EN_COURS']
            ).order_by('-date_demande')
            
            # Derniers patients consultés
            context['derniers_patients'] = Patient.objects.filter(
                dossier_medical__consultations__medecin_id=medecin_id
            ).distinct().order_by('-dossier_medical__consultations__date_consultation')[:5]
            
            # Prescriptions récentes
            context['prescriptions_recentes'] = Prescription.objects.filter(
                medecin_id=medecin_id
            ).order_by('-date_prescription')[:5]
        
        # Infirmier: Patients et rendez-vous
        elif role == 'INFIRMIER':
            # Statistiques patients
            context['total_patients_jour'] = ConsultationMedicale.objects.filter(
                date_consultation__date=today
            ).count()
            
            # Rendez-vous du jour
            context['rdv_aujourdhui'] = RendezVous.objects.filter(
                date_heure__date=today
            ).order_by('date_heure')
            
            # Patients récemment consultés
            context['derniers_patients'] = Patient.objects.filter(
                dossier_medical__consultations__date_consultation__date=today
            ).distinct().order_by('-dossier_medical__consultations__date_consultation')
        
        # Laborantin: Examens à réaliser
        elif role == 'LABORANTIN':
            # Examens à traiter
            context['examens_a_traiter'] = ExamenLaboratoire.objects.filter(
                statut='DEMANDE'
            ).order_by('-date_demande')
            
            context['examens_en_cours'] = ExamenLaboratoire.objects.filter(
                statut='EN_COURS'
            ).order_by('-date_demande')
            
            # Statistiques d'examens
            context['total_examens_jour'] = ExamenLaboratoire.objects.filter(
                date_demande__date=today
            ).count()
            
            context['examens_termines_jour'] = ExamenLaboratoire.objects.filter(
                date_realisation__date=today,
                statut='TERMINE'
            ).count()
            
            # Examens récemment terminés
            context['examens_recents'] = ExamenLaboratoire.objects.filter(
                statut='TERMINE'
            ).order_by('-date_realisation')[:5]
        
        # Pharmacien: Stock et ventes
        elif role == 'PHARMACIEN':
            # Alertes de stock
            context['produits_stock_bas'] = StockMedicament.objects.filter(
                quantite__lte=F('seuil_alerte')
            ).select_related('medicament').order_by('quantite')
            
            context['produits_rupture'] = StockMedicament.objects.filter(
                quantite=0
            ).count()
            
            # Mouvements récents
            context['mouvements_recents'] = MouvementStock.objects.order_by(
                '-date_mouvement'
            )[:10]
            
            # Ventes du jour
            ventes_jour = MouvementStock.objects.filter(
                type_mouvement='SORTIE',
                date_mouvement__date=today
            )
            context['total_ventes_jour'] = ventes_jour.count()
            
            # Prescriptions à servir
            context['prescriptions_recentes'] = Prescription.objects.filter(
                date_prescription__date__gte=start_week
            ).order_by('-date_prescription')[:5]
        
        # Réceptionniste: Patients, rendez-vous et facturation
        elif role == 'RECEPTION':
            # Rendez-vous du jour
            context['rdv_aujourdhui'] = RendezVous.objects.filter(
                date_heure__date=today
            ).order_by('date_heure')
            
            context['rdv_demain'] = RendezVous.objects.filter(
                date_heure__date=today + timedelta(days=1)
            ).order_by('date_heure')
            
            # Factures non payées
            context['factures_non_payees'] = Facture.objects.filter(
                statut='EN_ATTENTE'
            ).order_by('-date_emission')
            
            # Patients récemment enregistrés
            context['nouveaux_patients'] = Patient.objects.order_by(
                '-date_enregistrement'
            )[:5]
            
            # Statistiques du jour
            context['nouveaux_patients_jour'] = Patient.objects.filter(
                date_enregistrement__date=today
            ).count()
            
            context['rdv_crees_jour'] = RendezVous.objects.filter(
                date_heure__date=today
            ).count()
            
            context['factures_creees_jour'] = Facture.objects.filter(
                date_emission__date=today
            ).count()
        
        return render(request, self.template_name, context)


# Vue simplifiée comme point d'entrée
@login_required
def index(request):
    """Point d'entrée du système qui redirige vers le tableau de bord"""
    return redirect('dashboard')