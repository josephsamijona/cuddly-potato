from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
import uuid

# Utilisateurs du système
class Personnel(models.Model):
    ROLE_CHOICES = [
        ('MEDECIN', 'Médecin'),
        ('INFIRMIER', 'Infirmier/Infirmière'),
        ('LABORANTIN', 'Laborantin'),
        ('PHARMACIEN', 'Pharmacien'),
        ('RECEPTION', 'Réceptionniste'),
        ('ADMIN', 'Administrateur'),
    ]
    
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES)
    telephone = models.CharField(max_length=15, blank=True)
    adresse = models.TextField(blank=True)
    date_embauche = models.DateField(default=timezone.now)
    
    def __str__(self):
        return f"{self.user.get_full_name()} - {self.get_role_display()}"

# Patients
class Patient(models.Model):
    SEXE_CHOICES = [
        ('M', 'Masculin'),
        ('F', 'Féminin'),
        ('A', 'Autre'),
    ]
    
    GROUPE_SANGUIN_CHOICES = [
        ('A+', 'A+'),
        ('A-', 'A-'),
        ('B+', 'B+'),
        ('B-', 'B-'),
        ('AB+', 'AB+'),
        ('AB-', 'AB-'),
        ('O+', 'O+'),
        ('O-', 'O-'),
    ]
    
    id_patient = models.CharField(max_length=10, unique=True, default=uuid.uuid4)
    nom = models.CharField(max_length=100)
    prenom = models.CharField(max_length=100)
    date_naissance = models.DateField()
    sexe = models.CharField(max_length=1, choices=SEXE_CHOICES)
    adresse = models.TextField()
    telephone = models.CharField(max_length=15)
    email = models.EmailField(blank=True, null=True)
    groupe_sanguin = models.CharField(max_length=3, choices=GROUPE_SANGUIN_CHOICES, blank=True, null=True)
    allergies = models.TextField(blank=True)
    date_enregistrement = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.nom} {self.prenom} (ID: {self.id_patient})"
    
    def age(self):
        today = timezone.now().date()
        return today.year - self.date_naissance.year - ((today.month, today.day) < (self.date_naissance.month, self.date_naissance.day))

# Dossiers médicaux
class DossierMedical(models.Model):
    patient = models.OneToOneField(Patient, on_delete=models.CASCADE, related_name='dossier_medical')
    date_creation = models.DateTimeField(auto_now_add=True)
    derniere_mise_a_jour = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"Dossier de {self.patient}"

class ConsultationMedicale(models.Model):
    dossier = models.ForeignKey(DossierMedical, on_delete=models.CASCADE, related_name='consultations')
    medecin = models.ForeignKey(Personnel, on_delete=models.CASCADE)
    date_consultation = models.DateTimeField(default=timezone.now)
    motif = models.CharField(max_length=255)
    symptomes = models.TextField()
    diagnostic = models.TextField()
    notes = models.TextField(blank=True)
    
    def __str__(self):
        return f"Consultation du {self.date_consultation.strftime('%d/%m/%Y')} - {self.patient}"
    
    @property
    def patient(self):
        return self.dossier.patient

# Rendez-vous
class RendezVous(models.Model):
    STATUS_CHOICES = [
        ('PLANIFIE', 'Planifié'),
        ('CONFIRME', 'Confirmé'),
        ('TERMINE', 'Terminé'),
        ('ANNULE', 'Annulé'),
    ]
    
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name='rendez_vous')
    medecin = models.ForeignKey(Personnel, on_delete=models.CASCADE, related_name='rendez_vous')
    date_heure = models.DateTimeField()
    duree = models.PositiveIntegerField(default=30, help_text="Durée en minutes")
    motif = models.CharField(max_length=255)
    statut = models.CharField(max_length=10, choices=STATUS_CHOICES, default='PLANIFIE')
    notes = models.TextField(blank=True)
    
    def __str__(self):
        return f"RDV: {self.patient} avec Dr. {self.medecin.user.last_name} le {self.date_heure.strftime('%d/%m/%Y à %H:%M')}"

# Examens de laboratoire
class TypeExamen(models.Model):
    nom = models.CharField(max_length=100)
    description = models.TextField()
    prix = models.DecimalField(max_digits=10, decimal_places=2)
    
    def __str__(self):
        return self.nom

class ExamenLaboratoire(models.Model):
    STATUS_CHOICES = [
        ('DEMANDE', 'Demandé'),
        ('EN_COURS', 'En cours'),
        ('TERMINE', 'Terminé'),
        ('ANNULE', 'Annulé'),
    ]
    
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name='examens')
    type_examen = models.ForeignKey(TypeExamen, on_delete=models.CASCADE)
    medecin_demandeur = models.ForeignKey(Personnel, on_delete=models.CASCADE, related_name='examens_demandes')
    technicien = models.ForeignKey(Personnel, on_delete=models.CASCADE, related_name='examens_realises', null=True, blank=True)
    date_demande = models.DateTimeField(auto_now_add=True)
    date_realisation = models.DateTimeField(null=True, blank=True)
    resultats = models.TextField(blank=True)
    statut = models.CharField(max_length=10, choices=STATUS_CHOICES, default='DEMANDE')
    notes = models.TextField(blank=True)
    
    def __str__(self):
        return f"Examen {self.type_examen.nom} pour {self.patient} ({self.get_statut_display()})"

# Gestion des médicaments et pharmacie
class Medicament(models.Model):
    nom = models.CharField(max_length=100)
    description = models.TextField()
    categorie = models.CharField(max_length=100)
    fabricant = models.CharField(max_length=100)
    prix_unitaire = models.DecimalField(max_digits=10, decimal_places=2)
    
    def __str__(self):
        return self.nom

class StockMedicament(models.Model):
    medicament = models.OneToOneField(Medicament, on_delete=models.CASCADE, related_name='stock')
    quantite = models.PositiveIntegerField(default=0)
    seuil_alerte = models.PositiveIntegerField(default=5)
    date_mise_a_jour = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.medicament.nom} - Stock: {self.quantite}"
    
    def en_rupture(self):
        return self.quantite <= 0
    
    def alerte_stock_bas(self):
        return 0 < self.quantite <= self.seuil_alerte

class MouvementStock(models.Model):
    TYPE_CHOICES = [
        ('ENTREE', 'Entrée en stock'),
        ('SORTIE', 'Sortie de stock'),
    ]
    
    medicament = models.ForeignKey(Medicament, on_delete=models.CASCADE, related_name='mouvements')
    quantite = models.PositiveIntegerField()
    type_mouvement = models.CharField(max_length=10, choices=TYPE_CHOICES)
    date_mouvement = models.DateTimeField(auto_now_add=True)
    personnel = models.ForeignKey(Personnel, on_delete=models.CASCADE)
    notes = models.TextField(blank=True)
    
    def __str__(self):
        return f"{self.get_type_mouvement_display()} de {self.quantite} {self.medicament.nom}"

# Prescriptions
class Prescription(models.Model):
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name='prescriptions')
    medecin = models.ForeignKey(Personnel, on_delete=models.CASCADE, related_name='prescriptions')
    consultation = models.ForeignKey(ConsultationMedicale, on_delete=models.CASCADE, related_name='prescriptions', null=True, blank=True)
    date_prescription = models.DateTimeField(auto_now_add=True)
    notes = models.TextField(blank=True)
    
    def __str__(self):
        return f"Prescription pour {self.patient} par Dr. {self.medecin.user.last_name} le {self.date_prescription.strftime('%d/%m/%Y')}"

class LignePrescription(models.Model):
    prescription = models.ForeignKey(Prescription, on_delete=models.CASCADE, related_name='lignes')
    medicament = models.ForeignKey(Medicament, on_delete=models.CASCADE)
    posologie = models.CharField(max_length=255)
    duree_traitement = models.CharField(max_length=100)
    quantite = models.PositiveIntegerField()
    instructions = models.TextField(blank=True)
    
    def __str__(self):
        return f"{self.medicament.nom} - {self.posologie} ({self.duree_traitement})"

# Facturation
class Facture(models.Model):
    STATUS_CHOICES = [
        ('EN_ATTENTE', 'En attente'),
        ('PAYEE', 'Payée'),
        ('ANNULEE', 'Annulée'),
    ]
    
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name='factures')
    numero_facture = models.CharField(max_length=20, unique=True)
    date_emission = models.DateTimeField(auto_now_add=True)
    date_paiement = models.DateTimeField(null=True, blank=True)
    montant_total = models.DecimalField(max_digits=10, decimal_places=2)
    statut = models.CharField(max_length=10, choices=STATUS_CHOICES, default='EN_ATTENTE')
    notes = models.TextField(blank=True)
    
    def __str__(self):
        return f"Facture #{self.numero_facture} - {self.patient} ({self.get_statut_display()})"
    
    def save(self, *args, **kwargs):
        if not self.numero_facture:
            self.numero_facture = f"F{timezone.now().strftime('%Y%m%d')}-{uuid.uuid4().hex[:6].upper()}"
        super().save(*args, **kwargs)

class LigneFacture(models.Model):
    TYPE_CHOICES = [
        ('CONSULTATION', 'Consultation'),
        ('EXAMEN', 'Examen de laboratoire'),
        ('MEDICAMENT', 'Médicament'),
        ('AUTRE', 'Autre service'),
    ]
    
    facture = models.ForeignKey(Facture, on_delete=models.CASCADE, related_name='lignes')
    description = models.CharField(max_length=255)
    type_service = models.CharField(max_length=15, choices=TYPE_CHOICES)
    quantite = models.PositiveIntegerField(default=1)
    prix_unitaire = models.DecimalField(max_digits=10, decimal_places=2)
    
    def __str__(self):
        return f"{self.description} - {self.prix_unitaire} x {self.quantite}"
    
    @property
    def montant(self):
        return self.prix_unitaire * self.quantite