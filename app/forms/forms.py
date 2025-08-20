from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from django.utils import timezone
from ..models import (
    Patient, DossierMedical, ConsultationMedicale, RendezVous, 
    TypeExamen, ExamenLaboratoire, Medicament, StockMedicament, 
    MouvementStock, Prescription, LignePrescription, Facture, LigneFacture,
    Personnel
)

# --------------------------------------------------------
# Formulaires d'authentification et de gestion utilisateur
# --------------------------------------------------------

class LoginForm(forms.Form):
    """Formulaire de connexion"""
    username = forms.CharField(label="Nom d'utilisateur", 
                              widget=forms.TextInput(attrs={'class': 'form-control'}))
    password = forms.CharField(label="Mot de passe", 
                              widget=forms.PasswordInput(attrs={'class': 'form-control'}))


class UserRegistrationForm(UserCreationForm):
    """Formulaire d'enregistrement d'un nouvel utilisateur avec profil personnel"""
    ROLE_CHOICES = Personnel.ROLE_CHOICES
    
    email = forms.EmailField(required=True, widget=forms.EmailInput(attrs={'class': 'form-control'}))
    first_name = forms.CharField(required=True, label="Prénom", widget=forms.TextInput(attrs={'class': 'form-control'}))
    last_name = forms.CharField(required=True, label="Nom", widget=forms.TextInput(attrs={'class': 'form-control'}))
    role = forms.ChoiceField(choices=ROLE_CHOICES, required=True, label="Rôle", 
                            widget=forms.Select(attrs={'class': 'form-control'}))
    telephone = forms.CharField(required=False, label="Téléphone", widget=forms.TextInput(attrs={'class': 'form-control'}))
    adresse = forms.CharField(required=False, label="Adresse", widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 3}))
    
    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'email', 'password1', 'password2')
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control'}),
            'password1': forms.PasswordInput(attrs={'class': 'form-control'}),
            'password2': forms.PasswordInput(attrs={'class': 'form-control'}),
        }
    
    def save(self, commit=True):
        user = super().save(commit=True)
        personnel = Personnel(
            user=user,
            role=self.cleaned_data['role'],
            telephone=self.cleaned_data['telephone'],
            adresse=self.cleaned_data['adresse']
        )
        if commit:
            personnel.save()
        return user


class ProfileUpdateForm(forms.ModelForm):
    """Formulaire de mise à jour du profil utilisateur"""
    email = forms.EmailField(required=True)
    first_name = forms.CharField(required=True, label="Prénom")
    last_name = forms.CharField(required=True, label="Nom")
    
    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'email')
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
        }


class PersonnelUpdateForm(forms.ModelForm):
    """Formulaire de mise à jour du profil personnel"""
    class Meta:
        model = Personnel
        fields = ('telephone', 'adresse')
        widgets = {
            'telephone': forms.TextInput(attrs={'class': 'form-control'}),
            'adresse': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }


# --------------------------------------------------------
# Formulaires de gestion des patients
# --------------------------------------------------------

class PatientForm(forms.ModelForm):
    """Formulaire d'ajout/modification d'un patient"""
    class Meta:
        model = Patient
        fields = ('nom', 'prenom', 'date_naissance', 'sexe', 'adresse', 
                 'telephone', 'email', 'groupe_sanguin', 'allergies')
        widgets = {
            'nom': forms.TextInput(attrs={'class': 'form-control'}),
            'prenom': forms.TextInput(attrs={'class': 'form-control'}),
            'date_naissance': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'sexe': forms.Select(attrs={'class': 'form-control'}),
            'adresse': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'telephone': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'groupe_sanguin': forms.Select(attrs={'class': 'form-control'}),
            'allergies': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }
    
    def save(self, commit=True):
        patient = super().save(commit=commit)
        # Créer automatiquement un dossier médical si n'existe pas déjà
        if commit and not hasattr(patient, 'dossier_medical'):
            DossierMedical.objects.create(patient=patient)
        return patient


class PatientSearchForm(forms.Form):
    """Formulaire de recherche de patients"""
    query = forms.CharField(
        label="Rechercher un patient", 
        required=False, 
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Nom, prénom ou ID patient...'
        })
    )


# --------------------------------------------------------
# Formulaires de dossiers médicaux
# --------------------------------------------------------

class ConsultationForm(forms.ModelForm):
    """Formulaire de création/modification d'une consultation médicale"""
    class Meta:
        model = ConsultationMedicale
        fields = ('motif', 'symptomes', 'diagnostic', 'notes')
        widgets = {
            'motif': forms.TextInput(attrs={'class': 'form-control'}),
            'symptomes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'diagnostic': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }
    
    def __init__(self, *args, **kwargs):
        self.medecin = kwargs.pop('medecin', None)
        self.dossier = kwargs.pop('dossier', None)
        super().__init__(*args, **kwargs)
    
    def save(self, commit=True):
        consultation = super().save(commit=False)
        if self.medecin:
            consultation.medecin = self.medecin
        if self.dossier:
            consultation.dossier = self.dossier
        if commit:
            consultation.save()
        return consultation


# --------------------------------------------------------
# Formulaires de rendez-vous
# --------------------------------------------------------

class RendezVousForm(forms.ModelForm):
    """Formulaire de création/modification d'un rendez-vous"""
    class Meta:
        model = RendezVous
        fields = ('patient', 'medecin', 'date_heure', 'duree', 'motif', 'notes')
        widgets = {
            'patient': forms.Select(attrs={'class': 'form-control'}),
            'medecin': forms.Select(attrs={'class': 'form-control'}),
            'date_heure': forms.DateTimeInput(attrs={'class': 'form-control', 'type': 'datetime-local'}),
            'duree': forms.NumberInput(attrs={'class': 'form-control', 'min': '5', 'max': '120'}),
            'motif': forms.TextInput(attrs={'class': 'form-control'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Filtrer les médecins uniquement
        self.fields['medecin'].queryset = Personnel.objects.filter(role='MEDECIN')
        
    def clean_date_heure(self):
        date_heure = self.cleaned_data.get('date_heure')
        if date_heure and date_heure < timezone.now():
            raise forms.ValidationError("La date du rendez-vous ne peut pas être dans le passé.")
        return date_heure
    
    def clean(self):
        cleaned_data = super().clean()
        date_heure = cleaned_data.get('date_heure')
        duree = cleaned_data.get('duree')
        medecin = cleaned_data.get('medecin')
        
        if date_heure and duree and medecin:
            # Vérifier la disponibilité du médecin
            fin_rdv = date_heure + timezone.timedelta(minutes=duree)
            
            rdv_conflits = RendezVous.objects.filter(
                medecin=medecin,
                date_heure__lt=fin_rdv,
                statut__in=['PLANIFIE', 'CONFIRME']
            ).exclude(pk=self.instance.pk if self.instance.pk else None)
            
            for rdv in rdv_conflits:
                fin_existant = rdv.date_heure + timezone.timedelta(minutes=rdv.duree)
                if fin_existant > date_heure:
                    raise forms.ValidationError(
                        f"Le médecin a déjà un rendez-vous prévu à cette heure."
                    )
        
        return cleaned_data


# --------------------------------------------------------
# Formulaires d'examens de laboratoire
# --------------------------------------------------------

class TypeExamenForm(forms.ModelForm):
    """Formulaire de création/modification d'un type d'examen"""
    class Meta:
        model = TypeExamen
        fields = ('nom', 'description', 'prix')
        widgets = {
            'nom': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'prix': forms.NumberInput(attrs={'class': 'form-control', 'min': '0'}),
        }


class ExamenLaboratoireForm(forms.ModelForm):
    """Formulaire de demande d'examen de laboratoire"""
    class Meta:
        model = ExamenLaboratoire
        fields = ('patient', 'type_examen', 'notes')
        widgets = {
            'patient': forms.Select(attrs={'class': 'form-control'}),
            'type_examen': forms.Select(attrs={'class': 'form-control'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }
    
    def __init__(self, *args, **kwargs):
        self.medecin_demandeur = kwargs.pop('medecin_demandeur', None)
        super().__init__(*args, **kwargs)
    
    def save(self, commit=True):
        examen = super().save(commit=False)
        if self.medecin_demandeur:
            examen.medecin_demandeur = self.medecin_demandeur
        if commit:
            examen.save()
        return examen


class ResultatExamenForm(forms.ModelForm):
    """Formulaire de saisie des résultats d'un examen"""
    class Meta:
        model = ExamenLaboratoire
        fields = ('resultats', 'statut')
        widgets = {
            'resultats': forms.Textarea(attrs={'class': 'form-control', 'rows': 5}),
            'statut': forms.Select(attrs={'class': 'form-control'}),
        }
    
    def __init__(self, *args, **kwargs):
        self.technicien = kwargs.pop('technicien', None)
        super().__init__(*args, **kwargs)
        # Limiter les choix de statut
        self.fields['statut'].choices = [
            ('EN_COURS', 'En cours'),
            ('TERMINE', 'Terminé'),
            ('ANNULE', 'Annulé')
        ]
    
    def save(self, commit=True):
        examen = super().save(commit=False)
        if self.technicien:
            examen.technicien = self.technicien
        if examen.statut == 'TERMINE' and not examen.date_realisation:
            examen.date_realisation = timezone.now()
        if commit:
            examen.save()
        return examen


# --------------------------------------------------------
# Formulaires de pharmacie et gestion des stocks
# --------------------------------------------------------

class MedicamentForm(forms.ModelForm):
    """Formulaire d'ajout/modification d'un médicament"""
    stock_initial = forms.IntegerField(
        required=False,
        initial=0,
        min_value=0,
        label="Stock initial",
        widget=forms.NumberInput(attrs={'class': 'form-control'})
    )
    
    seuil_alerte = forms.IntegerField(
        required=False,
        initial=5,
        min_value=1,
        label="Seuil d'alerte",
        widget=forms.NumberInput(attrs={'class': 'form-control'})
    )
    
    class Meta:
        model = Medicament
        fields = ('nom', 'description', 'categorie', 'fabricant', 'prix_unitaire')
        widgets = {
            'nom': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'categorie': forms.TextInput(attrs={'class': 'form-control'}),
            'fabricant': forms.TextInput(attrs={'class': 'form-control'}),
            'prix_unitaire': forms.NumberInput(attrs={'class': 'form-control', 'min': '0', 'step': '0.01'}),
        }
    
    def save(self, commit=True):
        medicament = super().save(commit=True)
        
        # Créer ou mettre à jour le stock
        stock, created = StockMedicament.objects.get_or_create(
            medicament=medicament,
            defaults={
                'quantite': self.cleaned_data.get('stock_initial', 0),
                'seuil_alerte': self.cleaned_data.get('seuil_alerte', 5)
            }
        )
        
        if not created and 'stock_initial' in self.cleaned_data:
            stock.quantite = self.cleaned_data['stock_initial']
            stock.seuil_alerte = self.cleaned_data.get('seuil_alerte', 5)
            stock.save()
            
        return medicament


class MouvementStockForm(forms.ModelForm):
    """Formulaire d'entrée/sortie de stock"""
    class Meta:
        model = MouvementStock
        fields = ('medicament', 'quantite', 'type_mouvement', 'notes')
        widgets = {
            'medicament': forms.Select(attrs={'class': 'form-control'}),
            'quantite': forms.NumberInput(attrs={'class': 'form-control', 'min': '1'}),
            'type_mouvement': forms.Select(attrs={'class': 'form-control'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
        }
    
    def __init__(self, *args, **kwargs):
        self.personnel = kwargs.pop('personnel', None)
        super().__init__(*args, **kwargs)
    
    def clean(self):
        cleaned_data = super().clean()
        medicament = cleaned_data.get('medicament')
        quantite = cleaned_data.get('quantite')
        type_mouvement = cleaned_data.get('type_mouvement')
        
        if medicament and quantite and type_mouvement == 'SORTIE':
            try:
                stock = StockMedicament.objects.get(medicament=medicament)
                if stock.quantite < quantite:
                    raise forms.ValidationError(
                        f"Stock insuffisant. Quantité disponible : {stock.quantite}"
                    )
            except StockMedicament.DoesNotExist:
                raise forms.ValidationError("Ce médicament n'a pas de stock associé.")
        
        return cleaned_data
    
    def save(self, commit=True):
        mouvement = super().save(commit=False)
        if self.personnel:
            mouvement.personnel = self.personnel
        
        if commit:
            mouvement.save()
            
            # Mettre à jour le stock
            medicament = mouvement.medicament
            try:
                stock = StockMedicament.objects.get(medicament=medicament)
                
                if mouvement.type_mouvement == 'ENTREE':
                    stock.quantite += mouvement.quantite
                else:  # SORTIE
                    stock.quantite -= mouvement.quantite
                
                stock.save()
            except StockMedicament.DoesNotExist:
                if mouvement.type_mouvement == 'ENTREE':
                    StockMedicament.objects.create(
                        medicament=medicament,
                        quantite=mouvement.quantite,
                        seuil_alerte=5
                    )
        
        return mouvement


# --------------------------------------------------------
# Formulaires de prescriptions
# --------------------------------------------------------

class PrescriptionForm(forms.ModelForm):
    """Formulaire de création d'une prescription"""
    class Meta:
        model = Prescription
        fields = ('patient', 'notes')
        widgets = {
            'patient': forms.Select(attrs={'class': 'form-control'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }
    
    def __init__(self, *args, **kwargs):
        self.medecin = kwargs.pop('medecin', None)
        self.consultation = kwargs.pop('consultation', None)
        super().__init__(*args, **kwargs)
    
    def save(self, commit=True):
        prescription = super().save(commit=False)
        if self.medecin:
            prescription.medecin = self.medecin
        if self.consultation:
            prescription.consultation = self.consultation
        if commit:
            prescription.save()
        return prescription


class LignePrescriptionForm(forms.ModelForm):
    """Formulaire d'ajout d'un médicament à une prescription"""
    class Meta:
        model = LignePrescription
        fields = ('medicament', 'posologie', 'duree_traitement', 'quantite', 'instructions')
        widgets = {
            'medicament': forms.Select(attrs={'class': 'form-control'}),
            'posologie': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ex: 1 comprimé 3 fois par jour'}),
            'duree_traitement': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ex: 7 jours'}),
            'quantite': forms.NumberInput(attrs={'class': 'form-control', 'min': '1'}),
            'instructions': forms.Textarea(attrs={'class': 'form-control', 'rows': 2, 'placeholder': 'Instructions spéciales'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Filtrer pour n'afficher que les médicaments en stock
        self.fields['medicament'].queryset = Medicament.objects.filter(
            stock__quantite__gt=0
        ).order_by('nom')
        
    def clean(self):
        cleaned_data = super().clean()
        medicament = cleaned_data.get('medicament')
        quantite = cleaned_data.get('quantite')
        
        if medicament and quantite:
            try:
                stock = StockMedicament.objects.get(medicament=medicament)
                if stock.quantite < quantite:
                    raise forms.ValidationError(
                        f"Stock insuffisant pour {medicament.nom}. Disponible : {stock.quantite}"
                    )
            except StockMedicament.DoesNotExist:
                raise forms.ValidationError(f"Le médicament {medicament.nom} n'a pas de stock associé.")
        
        return cleaned_data


# Formulaire dynamique pour ajouter plusieurs médicaments à une prescription
class PrescriptionMedicamentsForm(forms.Form):
    """Formulaire dynamique pour prescrire plusieurs médicaments"""
    def __init__(self, *args, **kwargs):
        medicaments_en_stock = kwargs.pop('medicaments', None)
        super().__init__(*args, **kwargs)
        
        if not medicaments_en_stock:
            medicaments_en_stock = Medicament.objects.filter(
                stock__quantite__gt=0
            ).order_by('nom')
        
        # Créer des champs pour jusqu'à 5 médicaments
        for i in range(1, 6):
            self.fields[f'medicament_{i}'] = forms.ModelChoiceField(
                queryset=medicaments_en_stock,
                required=False,
                label=f"Médicament {i}",
                widget=forms.Select(attrs={'class': 'form-control'})
            )
            
            self.fields[f'posologie_{i}'] = forms.CharField(
                required=False,
                label=f"Posologie {i}",
                widget=forms.TextInput(attrs={
                    'class': 'form-control', 
                    'placeholder': 'Ex: 1 comprimé 3 fois par jour'
                })
            )
            
            self.fields[f'duree_{i}'] = forms.CharField(
                required=False,
                label=f"Durée {i}",
                widget=forms.TextInput(attrs={
                    'class': 'form-control', 
                    'placeholder': 'Ex: 7 jours'
                })
            )
            
            self.fields[f'quantite_{i}'] = forms.IntegerField(
                required=False,
                min_value=1,
                label=f"Quantité {i}",
                widget=forms.NumberInput(attrs={'class': 'form-control', 'min': '1'})
            )
            
            self.fields[f'instructions_{i}'] = forms.CharField(
                required=False,
                label=f"Instructions {i}",
                widget=forms.Textarea(attrs={
                    'class': 'form-control', 
                    'rows': 2, 
                    'placeholder': 'Instructions spéciales'
                })
            )
    
    def clean(self):
        cleaned_data = super().clean()
        
        # Vérifier qu'au moins un médicament est sélectionné
        medicament_present = False
        for i in range(1, 6):
            if cleaned_data.get(f'medicament_{i}'):
                medicament_present = True
                
                # Vérifier que les champs associés sont remplis
                if not cleaned_data.get(f'posologie_{i}'):
                    self.add_error(f'posologie_{i}', "Ce champ est obligatoire si un médicament est sélectionné.")
                
                if not cleaned_data.get(f'duree_{i}'):
                    self.add_error(f'duree_{i}', "Ce champ est obligatoire si un médicament est sélectionné.")
                
                if not cleaned_data.get(f'quantite_{i}'):
                    self.add_error(f'quantite_{i}', "Ce champ est obligatoire si un médicament est sélectionné.")
                
                # Vérifier le stock
                medicament = cleaned_data.get(f'medicament_{i}')
                quantite = cleaned_data.get(f'quantite_{i}', 0)
                if medicament and quantite:
                    try:
                        stock = StockMedicament.objects.get(medicament=medicament)
                        if stock.quantite < quantite:
                            self.add_error(
                                f'quantite_{i}', 
                                f"Stock insuffisant pour {medicament.nom}. Disponible : {stock.quantite}"
                            )
                    except StockMedicament.DoesNotExist:
                        self.add_error(
                            f'medicament_{i}', 
                            f"Le médicament {medicament.nom} n'a pas de stock associé."
                        )
        
        if not medicament_present:
            raise forms.ValidationError("Vous devez sélectionner au moins un médicament.")
        
        return cleaned_data


# --------------------------------------------------------
# Formulaires de facturation
# --------------------------------------------------------

class FactureForm(forms.ModelForm):
    """Formulaire de création d'une facture"""
    class Meta:
        model = Facture
        fields = ('patient', 'notes')
        widgets = {
            'patient': forms.Select(attrs={'class': 'form-control'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
        }


class LigneFactureForm(forms.ModelForm):
    """Formulaire d'ajout d'une ligne de facturation"""
    class Meta:
        model = LigneFacture
        fields = ('description', 'type_service', 'quantite', 'prix_unitaire')
        widgets = {
            'description': forms.TextInput(attrs={'class': 'form-control'}),
            'type_service': forms.Select(attrs={'class': 'form-control'}),
            'quantite': forms.NumberInput(attrs={'class': 'form-control', 'min': '1'}),
            'prix_unitaire': forms.NumberInput(attrs={'class': 'form-control', 'min': '0', 'step': '0.01'}),
        }


class PaiementForm(forms.Form):
    """Formulaire d'enregistrement de paiement"""
    MODES_PAIEMENT = [
        ('ESPECES', 'Espèces'),
        ('CARTE', 'Carte bancaire'),
        ('CHEQUE', 'Chèque'),
        ('MOBILE', 'Paiement mobile'),
        ('AUTRE', 'Autre'),
    ]
    
    montant_paye = forms.DecimalField(
        label="Montant payé",
        min_value=0.01,
        decimal_places=2,
        widget=forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'})
    )
    
    mode_paiement = forms.ChoiceField(
        label="Mode de paiement",
        choices=MODES_PAIEMENT,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    
    reference_paiement = forms.CharField(
        label="Référence (optionnel)",
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    
    notes = forms.CharField(
        label="Notes (optionnel)",
        required=False,
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 2})
    )
    
    def __init__(self, *args, **kwargs):
        self.facture = kwargs.pop('facture', None)
        super().__init__(*args, **kwargs)
        
        if self.facture:
            self.fields['montant_paye'].initial = self.facture.montant_total
            self.fields['montant_paye'].widget.attrs['max'] = self.facture.montant_total
    
    def clean_montant_paye(self):
        montant = self.cleaned_data.get('montant_paye')
        if self.facture and montant > self.facture.montant_total:
            raise forms.ValidationError(f"Le montant ne peut pas dépasser {self.facture.montant_total}.")
        return montant