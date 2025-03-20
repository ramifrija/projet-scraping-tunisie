# Projet Scraping Tunisie Annonce

## Description
Ce projet est une solution de scraping pour extraire les annonces immobilières du site `tunisie-annonce.com`. Il scrape les données, les stocke à la fois dans une base de données PostgreSQL (`scrapping`, table `tunisie_annonce`) et dans un fichier JSON (`data/annonces.json`), et les expose via une API REST construite avec FastAPI .

## Fonctionnalités
- **Scraping** : Extraction des annonces (titre, prix, type de bien, localisation, superficie, description, contact, date de publication, lien).
- **Stockage** :
  - Base PostgreSQL (Scrapping.sql)
  - Fichier JSON 
- **API** : Interface REST pour consulter les annonces ou relancer le scraping.

## Prérequis
- Python 
- PostgreSQL installé et configuré
- Git pour cloner le dépôt

## Installation
1. **Cloner le dépôt** :
   ```bash
   git clone https://github.com/ramifrija/projet-scraping-tunisie
   cd projet-scraping-tunisie

## Dependencies
   Consultez requirements.txt pour la liste complète.
