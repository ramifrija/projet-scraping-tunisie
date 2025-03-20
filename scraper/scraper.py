import requests
from bs4 import BeautifulSoup
import re
import psycopg2
from datetime import datetime
import time
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
import os
import json

DB_CONFIG = {
    "dbname": "scrapping",
    "user": "postgres",
    "password": "1",
    "host": "localhost",
    "port": "5432"
}

def setup_session():

    session = requests.Session()
    retry_strategy = Retry(
        total=3,
        backoff_factor=1,
        status_forcelist=[500, 502, 503, 504]
    )
    adapter = HTTPAdapter(max_retries=retry_strategy)
    session.mount("http://", adapter)
    session.mount("https://", adapter)
    return session

def scrape_details(url, session):
   
    try:
        response = session.get(url, headers={"User-Agent": "Mozilla/5.0"}, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        
        superficie = "N/A"
        contact = "N/A"
        
        desc = soup.select_one('td.TexteDetails')
        if desc:
            text = desc.get_text(strip=True)
            superficie_match = re.search(r"(\d+)\s*m²", text)
            if superficie_match:
                superficie = superficie_match.group(1)
            
            contact_match = re.search(r"\b\d{2}\s*\d{3}\s*\d{3}\b", text)
            if contact_match:
                contact = contact_match.group(0).replace(" ", "")
        
        return superficie, contact
    except (requests.RequestException, ValueError) as e:
        print(f"Erreur lors du scraping des détails {url}: {e}")
        return "N/A", "N/A"

def scrape_tunisie_annonce(page_num=1, session=None):
   
    if session is None:
        session = setup_session()
    
    url = f"http://www.tunisie-annonce.com/AnnoncesImmobilier.asp?rech_cod_cat=1&rech_order_by=31&rech_page_num={page_num}"
    try:
        response = session.get(url, headers={"User-Agent": "Mozilla/5.0"}, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')

        annonces = []
        for row in soup.select('tr.Tableau1'):
            cells = row.find_all('td')
            if len(cells) < 12:
                continue

            region = cells[1].find('a').text.strip() if cells[1].find('a') else "N/A"
            nature = cells[3].text.strip()
            type_bien = cells[5].text.strip()
            
            texte_annonce_tag = cells[7].find('a')
            titre = texte_annonce_tag.text.strip() if texte_annonce_tag else "N/A"
            onmouseover = texte_annonce_tag.get('onmouseover', '') if texte_annonce_tag else ''
            description_match = re.search(r"<b[^>]*>(.*?)</b><br/>(.*?)(?=<br/>|$)", onmouseover.replace(' ', ' '))
            description = description_match.group(2).strip() if description_match else "N/A"

            prix_text = cells[9].text.strip()
            prix = ''.join(filter(str.isdigit, prix_text)) if prix_text else "N/A"
            
            date_text = cells[11].text.strip()
            date_onmouseover = cells[11].get('onmouseover', '')
            date_pub_match = re.search(r"Insérée le</b> : (\d{2}/\d{2}/\d{4})", date_onmouseover)
            date_publication = date_pub_match.group(1) if date_pub_match else date_text

            lien = "http://www.tunisie-annonce.com/" + texte_annonce_tag['href'] if texte_annonce_tag else "N/A"

            try:
                date_obj = datetime.strptime(date_publication, '%d/%m/%Y')
                superficie, contact = scrape_details(lien, session)
                annonces.append({
                    "titre": titre,
                    "prix": prix,
                    "type_bien": type_bien,
                    "localisation": region,
                    "superficie": superficie,
                    "description": description,
                    "contact": contact,
                    "date_publication": date_publication,
                    "lien": lien
                })
            except ValueError:
                continue
            
            time.sleep(2)
        
        return annonces
    except requests.RequestException as e:
        print(f"Erreur lors du scraping de la page {page_num}: {e}")
        return []

def save_to_postgres(annonces):
  
    conn = None
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cur = conn.cursor()
        
        for annonce in annonces:
            cur.execute("""
                INSERT INTO tunisie_annonce (titre, prix, type_bien, localisation, superficie, description, contact, date_publication, lien)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (lien) DO NOTHING
            """, (
                annonce["titre"],
                annonce["prix"],
                annonce["type_bien"],
                annonce["localisation"],
                annonce["superficie"],
                annonce["description"],
                annonce["contact"],
                annonce["date_publication"],
                annonce["lien"]
            ))
        
        conn.commit()
        print(f"{len(annonces)} annonces insérées dans PostgreSQL.")
    except psycopg2.Error as e:
        print(f"Erreur PostgreSQL : {e}")
    finally:
        if conn:
            cur.close()
            conn.close()

def save_to_json(annonces, filename="data/annonces.json"):
    """Sauvegarde les annonces dans un fichier JSON."""
    os.makedirs(os.path.dirname(filename), exist_ok=True)  
    try:
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(annonces, f, ensure_ascii=False, indent=4)
        print(f"{len(annonces)} annonces sauvegardées dans {filename}.")
    except Exception as e:
        print(f"Erreur lors de la sauvegarde JSON : {e}")

if __name__ == "__main__":
    session = setup_session()
    all_annonces = []
    for page in range(1, 3):  
        print(f"Scraping page {page}...")
        page_annonces = scrape_tunisie_annonce(page, session)
        all_annonces.extend(page_annonces)
    
    print(f"Total annonces trouvées : {len(all_annonces)}")
    save_to_postgres(all_annonces)  
    save_to_json(all_annonces)     