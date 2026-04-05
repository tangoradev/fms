# FMS - Fleet Management System

## Présentation
FMS (Fleet Management System) est une application web moderne, innovante et responsive pour la gestion de flotte automobile. Elle vise à optimiser la gestion des véhicules, du carburant, de la maintenance, des assurances, des visites techniques, des courses et de la distribution de courrier.

## Caractéristiques
- **Gestion des utilisateurs** : Création et gestion des utilisateurs avec différents niveaux d'accès
- **Gestion des services** : Organisation des utilisateurs par services
- **Gestion des groupes** : Regroupement des utilisateurs par groupes fonctionnels
- **Interface responsive** : Accessible sur ordinateurs, tablettes et smartphones
- **Design moderne** : Interface utilisateur intuitive et agréable

## Technologies utilisées
- **Backend** : Django 4.2
- **Base de données** : SQLite (développement), MySQL (production)
- **Frontend** : HTML5, CSS3, JavaScript, Bootstrap 5
- **Langues** : Français

## Installation

### Prérequis
- Python 3.8 ou supérieur
- pip (gestionnaire de paquets Python)

### Étapes d'installation

1. Cloner le dépôt
```
git clone https://github.com/votre-organisation/fms.git
cd fms
```

2. Créer un environnement virtuel
```
python -m venv venv
```

3. Activer l'environnement virtuel
- Sous Windows :
```
venv\Scripts\activate
```
- Sous Linux/Mac :
```
source venv/bin/activate
```

4. Installer les dépendances
```
pip install -r requirements.txt
```

5. Effectuer les migrations de la base de données
```
python manage.py makemigrations
python manage.py migrate
```

6. Créer un superutilisateur
```
python manage.py createsuperuser
```

7. Lancer le serveur de développement
```
python manage.py runserver
```

8. Accéder à l'application
- Interface utilisateur : http://127.0.0.1:8000/
- Interface d'administration : http://127.0.0.1:8000/admin/

## Déploiement en production

Pour un déploiement en production, il est recommandé de :
- Utiliser MySQL comme base de données
- Configurer un serveur web comme Nginx ou Apache
- Utiliser Gunicorn comme serveur WSGI
- Activer HTTPS avec Let's Encrypt
- Désactiver le mode DEBUG

## Structure du projet

```
fms/
├── core/                  # Application principale
│   ├── migrations/        # Migrations de la base de données
│   ├── static/            # Fichiers statiques (CSS, JS, images)
│   ├── templates/         # Templates HTML
│   ├── admin.py           # Configuration de l'interface d'administration
│   ├── apps.py            # Configuration de l'application
│   ├── models.py          # Modèles de données
│   ├── tests.py           # Tests unitaires
│   └── views.py           # Vues et logique métier
├── fms/                   # Configuration du projet
│   ├── settings.py        # Paramètres du projet
│   ├── urls.py            # Configuration des URLs
│   ├── wsgi.py            # Configuration WSGI
│   └── asgi.py            # Configuration ASGI
├── manage.py              # Script de gestion Django
└── README.md              # Documentation du projet
```

## Droits de propriété
© 2025 - PNUD Côte d'Ivoire - Tous droits réservés
