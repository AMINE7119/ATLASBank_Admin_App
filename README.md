# 🏦 ATLASBank Admin Application

Une application d'administration bancaire robuste et sécurisée construite avec Flask, permettant la gestion complète des comptes clients et des opérations bancaires.

![Licence](https://img.shields.io/badge/Licence-MIT-blue.svg)
![Python](https://img.shields.io/badge/Python-3.8+-brightgreen.svg)
![Flask](https://img.shields.io/badge/Flask-2.0+-yellow.svg)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-13+-blue.svg)

## 📋 Table des Matières

- [Fonctionnalités](#-fonctionnalités)
- [Architecture](#-architecture)
- [Technologies](#-technologies)
- [Installation](#-installation)
- [Configuration](#-configuration)
- [Utilisation](#-utilisation)
- [Structure du Projet](#-structure-du-projet)
- [Sécurité](#-sécurité)
- [Auteur](#-auteur)

## ✨ Fonctionnalités

### Gestion des Comptes
- Création de nouveaux comptes (épargne et courant)
- Modification des informations des comptes
- Consultation des détails des comptes
- Désactivation/Suppression de comptes

### Opérations Bancaires
- Dépôts
- Retraits
- Transferts entre comptes
- Génération de relevés bancaires détaillés

### Tableau de Bord Analytique
- Visualisation des tendances des transactions
- Analyses démographiques des clients
- Métriques de performance bancaire
- Graphiques et statistiques en temps réel

### Administration
- Interface sécurisée pour les administrateurs
- Gestion des droits d'accès
- Journal d'audit des opérations
- Recherche avancée de comptes

## 🏗 Architecture

L'application suit une architecture MVC (Model-View-Controller) avec une séparation claire des responsabilités :

```
app/
├── controllers/    # Logique de contrôle
├── models/        # Modèles de données
├── services/      # Logique métier
├── dal/           # Couche d'accès aux données
├── templates/     # Vues HTML
├── static/        # Assets (CSS, JS)
```

## 🛠 Technologies

- **Backend:** Python, Flask
- **Base de données:** PostgreSQL
- **ORM:** psycopg2
- **Frontend:** HTML5, CSS3
- **Conteneurisation:** Docker
- **Visualisation:** Matplotlib, Pandas
- **Logging:** Python logging

## 💻 Installation

1. Clonez le dépôt :
```bash
git clone https://github.com/votre-username/ATLASBank_Admin_App.git
cd ATLASBank_Admin_App
```

2. Créez un environnement virtuel :
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# ou
venv\Scripts\activate     # Windows
```

3. Installez les dépendances :
```bash
pip install -r requirements.txt
```

4. Lancez avec Docker :
```bash
docker-compose up --build
```

## ⚙ Configuration

1. Créez un fichier `.env` à la racine du projet :
```env
DB_HOST=localhost
DB_PORT=5432
DB_NAME=bank_db
DB_USER=your_username
DB_PASSWORD=your_password
```

2. Initialisez la base de données :
```bash
psql -U postgres -f database.sql
```

## 📱 Utilisation

1. Accédez à l'application :
```
http://localhost:5000
```

2. Connectez-vous avec les identifiants par défaut :
```
Username: admin
Password: admin123
```

## 📁 Structure du Projet

```
ATLASBank_Admin_App/
├── app/
│   ├── controllers/
│   ├── models/
│   ├── services/
│   ├── dal/
│   ├── templates/
│   └── static/
├── tests/
├── database.sql
├── docker-compose.yml
├── Dockerfile
└── requirements.txt
```

## 🔒 Sécurité

- Authentification requise pour toutes les opérations
- Protection contre les injections SQL
- Validation des données entrantes
- Sessions sécurisées
- Journalisation des activités
- Gestion des erreurs robuste

## 👤 Auteur

- **AMINE** - *Développeur Principal* - [GitHub](https://github.com/AMINE7119)

