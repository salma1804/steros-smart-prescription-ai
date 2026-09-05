export interface ResultatZone {
  texte: string;
  moteur_principal?: string;
  confiance_tesseract?: number;
  confiance_easyocr?: number;
  statut: string;
  examens_identifies?: Array<{
    texte_detecte?: string;
    libelle_trouve: string;
    statut: string;
    methode?: string;
  }>;
  methode_analyses?: string;
}

export interface ResultatsOrdonnance {
  zone_analyses?: ResultatZone;
  zone_cachet?: ResultatZone;
  zone_date?: ResultatZone;
  zone_patient?: ResultatZone;
  zone_prescripteur?: ResultatZone;
  erreur?: string;
}

const API_URL = "http://localhost:8001";

export interface SuggestionExamen {
  libelle: string;
  score: number;
}

export async function rechercherExamens(recherche: string): Promise<SuggestionExamen[]> {
  if (recherche.trim().length < 2) return [];

  const reponse = await fetch(`${API_URL}/rechercher-examens?q=${encodeURIComponent(recherche)}`);
  if (!reponse.ok) return [];

  const donnees = await reponse.json();
  return donnees.resultats;
}

export async function traiterOrdonnance(fichier: File): Promise<ResultatsOrdonnance> {
  const formData = new FormData();
  formData.append("fichier", fichier);

  const reponse = await fetch(`${API_URL}/traiter-ordonnance`, {
    method: "POST",
    body: formData,
  });

  if (!reponse.ok) {
    throw new Error("Erreur lors du traitement de l'ordonnance");
  }

  return reponse.json();
}