# FoodFlex

FoodFlex est une application web Django moderne pour découvrir des restaurants et des plats.

## Fonctionnalités

- Interface utilisateur moderne avec animations Three.js
- Affichage des restaurants par ville
- Catalogue de plats
- Panneau d'administration pour gérer le contenu

## Technologies utilisées

- Django
- Three.js
- GSAP
- JavaScript
- HTML/CSS

## Installation

1. Cloner le dépôt
```bash
git clone https://github.com/votre-username/foodflex.git
cd foodflex
```

2. Créer un environnement virtuel
```bash
python -m venv env
source env/bin/activate  # Sur Windows: env\Scripts\activate
```

3. Installer les dépendances
```bash
pip install -r requirements.txt
```

4. Effectuer les migrations
```bash
python manage.py migrate
```

5. Créer un superutilisateur (pour l'administration)
```bash
python manage.py createsuperuser
```

6. Lancer le serveur
```bash
python manage.py runserver
```

7. Accéder à l'application sur [http://127.0.0.1:8000](http://127.0.0.1:8000)

## Administration

L'interface d'administration est accessible à l'adresse [http://127.0.0.1:8000/admin](http://127.0.0.1:8000/admin)

Identifiants par défaut:
- Utilisateur: admin
- Mot de passe: admin123

## Captures d'écran

*Des captures d'écran seront ajoutées prochainement* 