from fastapi import FastAPI
import psycopg2
import json
from scraper.scraper import scrape_tunisie_annonce, save_to_postgres, save_to_json

app = FastAPI()

DB_CONFIG = {
    "dbname": "scrapping",
    "user": "postgres",
    "password": "1",
    "host": "localhost",
    "port": "5432"
}

def load_annonces_from_db():
   
    conn = None
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cur = conn.cursor()
        cur.execute("SELECT titre, prix, type_bien, localisation, superficie, description, contact, date_publication, lien FROM tunisie_annonce")
        rows = cur.fetchall()
        annonces = [
            {
                "titre": row[0],
                "prix": row[1],
                "type_bien": row[2],
                "localisation": row[3],
                "superficie": row[4],
                "description": row[5],
                "contact": row[6],
                "date_publication": row[7],
                "lien": row[8]
            } for row in rows
        ]
        return annonces
    except psycopg2.Error as e:
        print(f"Erreur PostgreSQL : {e}")
        return []
    finally:
        if conn:
            cur.close()
            conn.close()

def load_annonces_from_json(filename="data/annonces.json"):
  
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"Fichier {filename} non trouvé.")
        return []
    except Exception as e:
        print(f"Erreur lors du chargement JSON : {e}")
        return []

@app.get("/")
async def root():
    return {"message": "Bienvenue sur l'API Tunisie Annonce."}

@app.get("/annonces")
async def get_annonces(source: str = "db"): 
    if source == "json":
        annonces = load_annonces_from_json()
    else:
        annonces = load_annonces_from_db()
    return {"annonces": annonces, "count": len(annonces)}

@app.post("/scrape")
async def start_scrape():
    all_annonces = []
    for page in range(1, 3): 
        page_annonces = scrape_tunisie_annonce(page)
        all_annonces.extend(page_annonces)
    save_to_postgres(all_annonces)
    save_to_json(all_annonces)  
    return {"message": "Scraping terminé", "count": len(all_annonces)}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)