export interface EntreeHistorique {
  date: string;
  patient: string;
  examens: string[];
  tempsTraitementSecondes: number;
  tauxReconnaissance: number;
  correctionsManuelles: number;
}

const CLE_STOCKAGE = "steros_historique_ordonnances";

export function ajouterEntreeHistorique(entree: EntreeHistorique) {
  const historiqueActuel = lireHistorique();
  historiqueActuel.unshift(entree);
  localStorage.setItem(CLE_STOCKAGE, JSON.stringify(historiqueActuel));
}

export function lireHistorique(): EntreeHistorique[] {
  if (typeof window === "undefined") return [];
  const donnees = localStorage.getItem(CLE_STOCKAGE);
  return donnees ? JSON.parse(donnees) : [];
}