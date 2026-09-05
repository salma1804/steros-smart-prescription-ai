from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
import shutil
import os
from pipeline_complet import traiter_ordonnance

app = FastAPI()

# Autorise les requêtes depuis ton frontend Next.js (qui tourne sur un port différent)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_methods=["*"],
    allow_headers=["*"],
)

DOSSIER_UPLOADS = "uploads_temporaires"
os.makedirs(DOSSIER_UPLOADS, exist_ok=True)


@app.post("/traiter-ordonnance")
async def traiter_ordonnance_endpoint(fichier: UploadFile = File(...)):
    """
    Reçoit une image d'ordonnance, la traite via le pipeline complet,
    et retourne les résultats structurés en JSON.
    """
    chemin_temporaire = os.path.join(DOSSIER_UPLOADS, fichier.filename)

    with open(chemin_temporaire, "wb") as f:
        shutil.copyfileobj(fichier.file, f)

    resultats = traiter_ordonnance(chemin_temporaire)

    return resultats


@app.get("/")
async def racine():
    return {"message": "API Steros Smart Prescription AI opérationnelle"}


from moteur_nlp import faire_correspondre_examen, TOUS_LES_LIBELLES, REFERENTIEL_NORMALISE
from rapidfuzz import process, fuzz


@app.get("/rechercher-examens")
async def rechercher_examens(q: str):
    """
    Recherche des examens dans le catalogue à partir d'un texte partiel
    (abréviation ou début de désignation). Retourne les meilleures correspondances.
    """
    if len(q.strip()) < 2:
        return {"resultats": []}

    resultats = process.extract(q, TOUS_LES_LIBELLES, scorer=fuzz.WRatio, limit=8)

    suggestions = [
        {"libelle": libelle, "score": score}
        for libelle, score, _ in resultats
        if score >= 40  # seuil bas ici : c'est une SUGGESTION pour l'humain, pas une auto-validation
    ]

    return {"resultats": suggestions}