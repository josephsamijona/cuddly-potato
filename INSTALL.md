Voici un fichier **`INSTALL.md`** complet, clair et accessible en **français, anglais et créole haïtien**, spécialement conçu pour **KlinikLib**, ton système de gestion médical open source pour Haïti.

Ce guide permet à une clinique, un technicien ou un développeur de **installer KlinikLib localement ou sur un serveur** avec des étapes simples, sécurisées et bien expliquées.

---

```markdown
# 🛠️ Guide d’Installation de KlinikLib

Bienvenue dans le guide d’installation de **KlinikLib** — un logiciel libre de gestion de clinique médicale, conçu pour Haïti et les pays en développement.

Ce guide t’aide à installer KlinikLib **en mode développement ou production**, que tu sois un développeur ou un technicien de clinique.

---

## 🌍 Français

### ✅ Prérequis

Avant de commencer, assure-toi d’avoir :

- **Python 3.8 ou supérieur**  
  → Télécharge-le : https://www.python.org/downloads/

- **pip** (gestionnaire de paquets Python)  
  → Vérifie avec : `pip --version`

- **git** (pour cloner le projet)  
  → Télécharge-le : https://git-scm.com/

- **Un éditeur de code** (ex : VS Code, Sublime Text)

- **Optionnel (production)** :  
  - Un serveur web (Apache, Nginx)
  - Une base de données (PostgreSQL recommandé pour la production)

---

### 📦 Étapes d’installation

#### 1. Clone le dépôt

```bash
git clone https://github.com/ton-pseudo/KlinikLib.git
cd KlinikLib
```

> Remplace `ton-pseudo` par ton nom d’utilisateur GitHub.

#### 2. Crée un environnement virtuel

```bash
python -m venv venv
```

#### 3. Active l’environnement

- **Sur Windows** :
  ```bash
  venv\Scripts\activate
  ```

- **Sur macOS / Linux** :
  ```bash
  source venv/bin/activate
  ```

> Tu devrais voir `(venv)` au début de ta ligne de commande.

#### 4. Installe les dépendances

```bash
pip install -r requirements.txt
```

> Si tu n’as pas de fichier `requirements.txt`, crée-le avec :
> ```bash
> pip freeze > requirements.txt
> ```
> Ou installe Django manuellement :
> ```bash
> pip install django python-decouple
> ```

#### 5. Configure les variables d’environnement (optionnel mais recommandé)

Crée un fichier `.env` à la racine du projet :

```env
DEBUG=True
SECRET_KEY=tres_long_secret_key_ici
DATABASE_URL=sqlite:///db.sqlite3
```

> Pour la production, utilise une clé secrète forte et `DEBUG=False`.

> Tu peux générer une clé secrète ici :  
> https://djecrety.ir/

#### 6. Applique les migrations

```bash
python manage.py makemigrations
python manage.py migrate
```

#### 7. Crée un superutilisateur (admin)

```bash
python manage.py createsuperuser
```

> Suis les instructions pour créer un compte admin.

#### 8. Lance le serveur de développement

```bash
python manage.py runserver
```

#### 9. Accède à l’application

Ouvre ton navigateur et va sur :

👉 [http://127.0.0.1:8000](http://127.0.0.1:8000)  
👉 [http://127.0.0.1:8000/admin](http://127.0.0.1:8000/admin) pour l’interface admin

---

### 🏗️ Pour la production (recommandations)

1. **Utilise PostgreSQL** au lieu de SQLite
2. **Mets `DEBUG=False`** dans `.env`
3. **Configure un serveur web** comme Nginx + Gunicorn
4. **Utilise une base de données sécurisée** avec sauvegardes régulières
5. **Installe un certificat SSL** (Let’s Encrypt) pour HTTPS

---

### 🧩 Structure du projet (à savoir)

```
KlinikLib/
├── manage.py
├── requirements.txt
├── .env                  # variables d’environnement
├── myproject/            # configuration Django
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
└── myapp/                # ton application (ex: patients, dossier, etc.)
    ├── models.py
    ├── views.py
    └── ...
```

---

### 🐞 Problèmes courants

| Problème | Solution |
|--------|----------|
| `Command 'python' not found` | Installe Python et vérifie ton PATH |
| `pip: command not found` | Installe pip avec `python -m ensurepip --upgrade` |
| Erreur de migration | Vérifie que la base de données est bien configurée |
| Page blanche après `runserver` | Vérifie que `DEBUG=True` et que les fichiers statiques sont servis |

---

> 💚 **Ansanm, nou kapab fè sa.**  
> Ensemble, rendons la santé numérique accessible en Haïti.

---

## 🌐 English

### ✅ Prerequisites

- **Python 3.8 or higher**  
  → Download: https://www.python.org/downloads/

- **pip** (Python package manager)  
  → Check with: `pip --version`

- **git**  
  → Download: https://git-scm.com/

- **A code editor** (e.g. VS Code)

- **Optional (production)**:  
  - Web server (Apache, Nginx)
  - Database (PostgreSQL recommended)

---

### 📦 Installation Steps

#### 1. Clone the repository

```bash
git clone https://github.com/your-username/KlinikLib.git
cd KlinikLib
```

#### 2. Create a virtual environment

```bash
python -m venv venv
```

#### 3. Activate it

- **Windows**:
  ```bash
  venv\Scripts\activate
  ```

- **macOS / Linux**:
  ```bash
  source venv/bin/activate
  ```

#### 4. Install dependencies

```bash
pip install -r requirements.txt
```

#### 5. Environment variables (recommended)

Create a `.env` file:

```env
DEBUG=True
SECRET_KEY=your_strong_secret_key_here
DATABASE_URL=sqlite:///db.sqlite3
```

#### 6. Run migrations

```bash
python manage.py makemigrations
python manage.py migrate
```

#### 7. Create a superuser

```bash
python manage.py createsuperuser
```

#### 8. Start the server

```bash
python manage.py runserver
```

#### 9. Access the app

👉 [http://127.0.0.1:8000](http://127.0.0.1:8000)  
👉 [http://127.0.0.1:8000/admin](http://127.0.0.1:8000/admin)

---

### 🏗️ Production Recommendations

- Use **PostgreSQL**
- Set `DEBUG=False`
- Use **Gunicorn + Nginx**
- Enable **HTTPS with SSL**
- Backup database regularly

---

> 💚 **Together, we can do this.**  
> Let’s make digital health accessible in Haiti.

---

## 🇭🇹 Kreyòl Ayisyen

### ✅ Pre-reqwa

- **Python 3.8 oswa pi wo**  
  → Download: https://www.python.org/downloads/

- **pip** (gestionnaire pakèt)  
  → Tcheke: `pip --version`

- **git**  
  → Download: https://git-scm.com/

- **Yon editè kòd** (ex: VS Code)

- **Opsyonèl (pwochenn)**:  
  - Sèvè wèb (Apache, Nginx)
  - Baz done (PostgreSQL pi bon pou pwochenn)

---

### 📦 Etap instalasyon

#### 1. Clone depo a

```bash
git clone https://github.com/pseudou/KlinikLib.git
cd KlinikLib
```

#### 2. Kreye yon venv

```bash
python -m venv venv
```

#### 3. Aktive l

- **Windows**:
  ```bash
  venv\Scripts\activate
  ```

- **macOS / Linux**:
  ```bash
  source venv/bin/activate
  ```

#### 4. Instale pakèt yo

```bash
pip install -r requirements.txt
```

#### 5. Konfigire varyab anviwònman

Kreye yon dosye `.env`:

```env
DEBUG=True
SECRET_KEY=klere_sekre_ou_ici
DATABASE_URL=sqlite:///db.sqlite3
```

#### 6. Aplike migrasyon yo

```bash
python manage.py makemigrations
python manage.py migrate
```

#### 7. Kreye yon admin

```bash
python manage.py createsuperuser
```

#### 8. Komanse sèvè a

```bash
python manage.py runserver
```

#### 9. Al nan aplikasyon an

👉 [http://127.0.0.1:8000](http://127.0.0.1:8000)  
👉 [http://127.0.0.1:8000/admin](http://127.0.0.1:8000/admin)

---

### 🏗️ Pou Pwochenn

- Itilize **PostgreSQL**
- Mete `DEBUG=False`
- Itilize **Gunicorn + Nginx**
- Mete **HTTPS (SSL)**
- Fè sokesyon regilyè

---

> 💚 **Ansanm, nou kapab fè sa.**  
> Ansanm, nou kapab fè sante nimerik la aksesib Ayiti.

---

## 📄 Notes

- Ce fichier suppose que ton projet utilise Django avec une structure classique.
- Si tu utilises `python3` au lieu de `python`, adapte les commandes.
- Pour un déploiement automatique, envisage Docker ou un script d’installation.

---

## 📞 Assistance

Besoin d’aide ?  
Contacte-nous :  
📧 josephsamueljonathan@gmail.com  
📞 +509 4752 0306
```

---

### ✅ Que faire maintenant ?

1. Sauve ce fichier sous le nom : `INSTALL.md`
2. Mets-le à la racine de ton projet
3. Ajoute un lien dans ton `README.md` :

```markdown
## 🛠️ Installation
Voir [INSTALL.md](INSTALL.md) pour les instructions d'installation.
```

---
