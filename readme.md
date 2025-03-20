# Projet Scraping Tunisie Annonce

## Description
Ce projet est une solution de scraping permettant d'extraire les annonces immobilières du site tunisie-annonce.com. Il collecte les données, les stocke dans une base de données PostgreSQL dont une exportation est disponible sous le nom scrapping.sql ainsi et dans un fichier JSON (data/annonces.json). De plus, ces données sont exposées via une API REST développée avec FastAPI.

## Fonctionnalités
- **Scraping** : Extraction des annonces (titre, prix, type de bien, localisation, superficie, description, contact, date de publication, lien).
- **Stockage** :
  - Base PostgreSQL (Scrapping.sql)
  - Fichier JSON 
- **API** : Interface REST pour consulter les annonces ou relancer le scraping.

## Prérequis
- Python 
- PostgreSQL 
- Git 

## Installation
1. **Cloner le dépôt** :
   
   git clone https://github.com/ramifrija/projet-scraping-tunisie
   cd projet-scraping-tunisie

## Dependencies
   Consultez requirements.txt pour la liste complète.
