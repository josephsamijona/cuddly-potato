# 🏥 KlinikLib – Logiciel Libre de Gestion de Clinique

![License](https://img.shields.io/badge/license-MIT-blue.svg) ![Version](https://img.shields.io/badge/version-0.1-orange.svg)

**KlinikLib** est une solution open source et libre pour la gestion efficace des cliniques, conçue avec et pour Haïti.  
Notre mission : rendre l’accès aux logiciels médicaux **gratuits, faciles, et accessibles à tous**.

---

## 🌍 Français

### 🎯 Objectif
KlinikLib vise à offrir un système de gestion médicale **open source, modulaire et évolutif**, spécialement adapté aux besoins des cliniques en Haïti.  
Nous commençons par une version de base (v0.1), mais nous avons pour ambition d’évoluer vers des **versions spécialisées** :
- Cliniques générales
- Hôpitaux
- Centres de santé communautaires
- Pharmacies autonomes
- Laboratoires médicaux

Notre objectif est simple : **aucune clinique ne devrait être pénalisée par le coût d’un logiciel.**

### 🔓 Logiciel Libre
KlinikLib est **100 % libre** :
- ✅ Gratuit d’utilisation
- ✅ Code ouvert (tu peux voir, modifier, améliorer)
- ✅ Tu peux le déployer où tu veux
- ✅ Tu peux le traduire, l’adapter à ton contexte

👉 Tu es **libre de soutenir, d’utiliser, de contribuer** à ce projet.  
Chaque contribution compte : code, traduction, documentation, design, ou simplement un retour d’expérience.

### 🧩 Fonctionnalités (v0.1)
Voici les modules et vues disponibles dans cette version initiale :

#### 🔐 Authentification
| Vue | Description | Accès |
|-----|-------------|-------|
| `LoginView` | Connexion utilisateur | Tous |
| `LogoutView` | Déconnexion | Tous |
| `ProfileView` | Profil utilisateur | Tous (utilisateur connecté) |
| `PasswordChangeView` | Changement de mot de passe | Tous (utilisateur connecté) |

#### 📊 Tableau de Bord
| Vue | Description | Accès |
|-----|-------------|-------|
| `DashboardView` | Tableau de bord principal | Tous (adapté selon le rôle) |

#### 👥 Patients
| Vue | Description | Accès |
|-----|-------------|-------|
| `PatientListView` | Liste des patients | ADMIN, MEDECIN, INFIRMIER, RECEPTION |
| `PatientDetailView` | Fiche détaillée patient | ADMIN, MEDECIN, INFIRMIER, RECEPTION |
| `PatientCreateView` | Ajout nouveau patient | ADMIN, RECEPTION |
| `PatientUpdateView` | Modification patient | ADMIN, RECEPTION |
| `PatientSearchView` | Recherche de patients | ADMIN, MEDECIN, INFIRMIER, RECEPTION |

#### 📁 Dossiers Médicaux
| Vue | Description | Accès |
|-----|-------------|-------|
| `DossierMedicalView` | Consultation dossier | ADMIN, MEDECIN, INFIRMIER |
| `ConsultationCreateView` | Création consultation | ADMIN, MEDECIN |
| `ConsultationDetailView` | Détail consultation | ADMIN, MEDECIN, INFIRMIER |
| `ConsultationListView` | Liste consultations | ADMIN, MEDECIN, INFIRMIER |

#### 🗓️ Rendez-vous
| Vue | Description | Accès |
|-----|-------------|-------|
| `CalendrierRendezVousView` | Calendrier des RDV | ADMIN, MEDECIN, INFIRMIER, RECEPTION |
| `RendezVousListView` | Liste des RDV | ADMIN, MEDECIN, INFIRMIER, RECEPTION |
| `RendezVousCreateView` | Création de RDV | ADMIN, RECEPTION, MEDECIN |
| `RendezVousUpdateView` | Modification de RDV | ADMIN, RECEPTION, MEDECIN |
| `RendezVousDuJourView` | RDV du jour | ADMIN, MEDECIN, INFIRMIER, RECEPTION |

#### 🔬 Examens de Laboratoire
| Vue | Description | Accès |
|-----|-------------|-------|
| `ExamenListView` | Liste des examens | ADMIN, MEDECIN, LABORANTIN |
| `ExamenCreateView` | Demande d'examen | ADMIN, MEDECIN |
| `ExamenDetailView` | Détail d'un examen | ADMIN, MEDECIN, LABORANTIN |
| `ResultatExamenCreateView` | Saisie résultats | ADMIN, LABORANTIN |
| `ResultatExamenView` | Consultation résultats | ADMIN, MEDECIN, LABORANTIN |

#### 💊 Pharmacie & Stock
| Vue | Description | Accès |
|-----|-------------|-------|
| `MedicamentListView` | Liste des médicaments | ADMIN, PHARMACIEN |
| `MedicamentCreateView` | Ajout médicament | ADMIN, PHARMACIEN |
| `StockView` | État des stocks | ADMIN, PHARMACIEN |
| `MouvementStockCreateView` | Entrée/Sortie stock | ADMIN, PHARMACIEN |
| `MouvementStockListView` | Historique mouvements | ADMIN, PHARMACIEN |
| `POSView` | Point de vente | ADMIN, PHARMACIEN |

#### 🧾 Prescriptions
| Vue | Description | Accès |
|-----|-------------|-------|
| `PrescriptionListView` | Liste prescriptions | ADMIN, MEDECIN, PHARMACIEN |
| `PrescriptionCreateView` | Création prescription | ADMIN, MEDECIN |
| `PrescriptionDetailView` | Détail prescription | ADMIN, MEDECIN, PHARMACIEN |
| `PrescriptionPrintView` | Impression ordonnance | ADMIN, MEDECIN, PHARMACIEN |

#### 💵 Facturation
| Vue | Description | Accès |
|-----|-------------|-------|
| `FactureListView` | Liste des factures | ADMIN, RECEPTION, PHARMACIEN |
| `FactureCreateView` | Création facture | ADMIN, RECEPTION |
| `FactureDetailView` | Détail facture | ADMIN, RECEPTION |
| `FacturePrintView` | Impression facture | ADMIN, RECEPTION |
| `PaiementCreateView` | Enregistrement paiement | ADMIN, RECEPTION |

#### ⚙️ Administration
| Vue | Description | Accès |
|-----|-------------|-------|
| `UserListView` | Liste utilisateurs | ADMIN |
| `UserCreateView` | Création utilisateur | ADMIN |
| `UserUpdateView` | Modification utilisateur | ADMIN |
| `TypeExamenListView` | Gestion types examens | ADMIN |

### 👤 Niveaux d'accès
- **ADMIN** : Accès complet à toutes les fonctionnalités
- **MEDECIN** : Dossiers patients, consultations, prescriptions
- **INFIRMIER** : Dossiers patients, consultations, RDV
- **LABORANTIN** : Examens de laboratoire uniquement
- **PHARMACIEN** : Pharmacie, stock, prescriptions
- **RECEPTION** : Patients, RDV, facturation

---

## 🌐 English

### 🎯 Mission
**KlinikLib** is an open-source medical clinic management system designed for Haiti.  
Our goal is to make **free, accessible, and easy-to-use software** available to every clinic, no matter their resources.

We start with version 0.1, but we plan to grow into **specialized versions** for:
- General clinics
- Hospitals
- Community health centers
- Standalone pharmacies
- Medical labs

No clinic should be held back by expensive software.

### 🔓 Open Source & Free
KlinikLib is **100% free and open source**:
- ✅ Free to use
- ✅ Open code (you can view, modify, improve)
- ✅ Deploy anywhere
- ✅ Translate and adapt freely

👉 You are **free to support, use, and contribute**.  
Every contribution counts: code, translation, documentation, design, or feedback.

### 🧩 Features (v0.1)
See the full list of modules and views above (in French section).

### 👤 Access Roles
Same as above.

---

## 🇭🇹 Kreyòl Ayisyen

### 🎯 Misyon
**KlinikLib** se yon solisyon **lòt kay** pou jere klinik medikal, kreye pou Ayiti.  
Nou vle fè **lojisyèl medikal gratis, senp ak aksesib** pou tout moun.

Nou komanse avèk vèsyon 0.1, men nou gen gwo plan: fè **vèsyon espesyalize** pou:
- Klinik jeneral
- Ospital
- Sante kominote
- Fwatmasy
- Labo medikal

Pa gen okenn klinik ki dwe pati pou pri yon lojisyèl.

### 🔓 Lojisyèl Lib
KlinikLib se **100% lib**:
- ✅ Gratis pou itilize
- ✅ Kod ouvè (ou ka wè, modifye, amelyore)
- ✅ Ou kapab itilize l kote ou vle
- ✅ Ou kapab tradui l, adapte l

👉 Ou **lib pou sipoete, itilize oswa kontribye**.  
Chak kontribisyon enpotan: kod, tradiksyon, dokimantasyon, desen, oswa yon senp kòmantè.

### 🧩 Fonksyonalite (v0.1)
Gade lis modil ak vyew yo pi wo (nan seksyon franse).

### 👤 Nivo aksè
Menm ke pi wo.

---

## 🤝 Comment Contribuer ?

1. 🍴 **Fork** ce dépôt
2. 🛠️ Fais des modifications
3. 📤 Ouvre une **Pull Request**

Tu peux aussi :
- 📝 Améliorer la documentation
- 🌐 Traduire dans d'autres langues
- 🐞 Signaler des bogues
- 💡 Proposer des fonctionnalités

---

## 📞 Contact

**Joseph Samuel Jonathan**  
📞 +509 4752 0306  
📧 josephsamueljonathan@gmail.com  

---

## 📜 Licence
Ce projet est publié sous licence **MIT**.  
Utilise-le, partage-le, améliore-le — librement.

> 💚 **Ansanm, nou kapab fè sa.**  
> Ensemble, nous pouvons le faire.