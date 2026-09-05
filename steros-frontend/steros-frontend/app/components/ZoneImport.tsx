"use client";

import { useState } from "react";
import { Loader2 } from "lucide-react";
import { traiterOrdonnance, ResultatsOrdonnance } from "../lib/api";

interface ZoneImportProps {
  onResultats: (r: ResultatsOrdonnance) => void;
  onApercuImage: (url: string) => void;
  onChangementChargement: (enCours: boolean) => void;
}

export default function ZoneImport({ onResultats, onApercuImage, onChangementChargement }: ZoneImportProps) {
  const [fichierSelectionne, setFichierSelectionne] = useState<File | null>(null);
  const [enCoursDeTraitement, setEnCoursDeTraitement] = useState(false);
  const [etapeActuelle, setEtapeActuelle] = useState("");
  const [zoneSurvolee, setZoneSurvolee] = useState(false);

  const selectionnerFichier = (fichier: File) => {
    if (!fichier.type.startsWith("image/")) {
      alert("Merci de sélectionner un fichier image (PNG ou JPG).");
      return;
    }
    setFichierSelectionne(fichier);
    const urlApercu = URL.createObjectURL(fichier);
    onApercuImage(urlApercu);
  };

  const gererSelectionFichier = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      selectionnerFichier(e.target.files[0]);
    }
  };

  const gererDepot = (e: React.DragEvent<HTMLLabelElement>) => {
    e.preventDefault();
    setZoneSurvolee(false);
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      selectionnerFichier(e.dataTransfer.files[0]);
    }
  };

  const gererSurvol = (e: React.DragEvent<HTMLLabelElement>) => {
    e.preventDefault();
    setZoneSurvolee(true);
  };

  const gererSortieSurvol = (e: React.DragEvent<HTMLLabelElement>) => {
    e.preventDefault();
    setZoneSurvolee(false);
  };

  const gererClicTraiter = async () => {
    if (!fichierSelectionne) return;

    setEnCoursDeTraitement(true);
    onChangementChargement(true);

    const etapes = [
      "Détection des zones...",
      "Extraction du texte (OCR)...",
      "Correspondance avec le catalogue...",
    ];
    let indexEtape = 0;
    setEtapeActuelle(etapes[0]);
    const intervalle = setInterval(() => {
      indexEtape = Math.min(indexEtape + 1, etapes.length - 1);
      setEtapeActuelle(etapes[indexEtape]);
    }, 4000);

    try {
      const resultats = await traiterOrdonnance(fichierSelectionne);

      if (resultats.erreur) {
        alert(`Erreur lors du traitement : ${resultats.erreur}`);
        return;
      }

      onResultats(resultats);
    } catch (erreur) {
      console.error(erreur);
      alert("Erreur de connexion au serveur. Vérifiez que l'API est bien démarrée.");
    } finally {
      clearInterval(intervalle);
      setEnCoursDeTraitement(false);
      onChangementChargement(false);
      setEtapeActuelle("");
    }
  };

  return (
    <div className="bg-white rounded-xl shadow-sm p-6">
      <h2 className="text-sm font-semibold text-gray-700 mb-4">
        1. Ordonnance à importer
      </h2>

      <label
        htmlFor="fichier-ordonnance"
        onDrop={gererDepot}
        onDragOver={gererSurvol}
        onDragLeave={gererSortieSurvol}
        className={`flex flex-col items-center justify-center border-2 border-dashed rounded-lg h-80 transition-colors ${
          enCoursDeTraitement
            ? "border-[#00B4B8] bg-[#00B4B8]/5 cursor-wait"
            : zoneSurvolee
            ? "border-[#00B4B8] bg-[#00B4B8]/10 cursor-copy"
            : "border-gray-300 cursor-pointer hover:border-[#00B4B8]"
        }`}
      >
        {enCoursDeTraitement ? (
          <>
            <Loader2 size={40} className="mb-3 text-[#00B4B8] animate-spin" />
            <p className="text-gray-700 text-sm font-medium">{etapeActuelle}</p>
            <p className="text-gray-400 text-xs mt-1">Cela peut prendre quelques secondes</p>
          </>
        ) : (
          <>
            <span className="text-4xl mb-3">📄</span>
            <p className="text-gray-500 text-sm">
              {fichierSelectionne ? fichierSelectionne.name : "Cliquez pour importer une image (PNG/JPG)"}
            </p>
            <p className="text-gray-400 text-xs mt-1">
              {zoneSurvolee ? "Déposez le fichier ici" : "ou glissez-déposez le fichier ici"}
            </p>
          </>
        )}
        <input
          id="fichier-ordonnance"
          type="file"
          accept="image/png, image/jpeg"
          className="hidden"
          onChange={gererSelectionFichier}
          disabled={enCoursDeTraitement}
        />
      </label>

      <button
        onClick={gererClicTraiter}
        disabled={!fichierSelectionne || enCoursDeTraitement}
        className="w-full mt-6 bg-[#0F1B2D] text-white py-3 rounded-lg font-medium hover:bg-[#1a2b45] transition-colors disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2"
      >
        {enCoursDeTraitement && <Loader2 size={16} className="animate-spin" />}
        {enCoursDeTraitement ? "Traitement en cours..." : "Traiter l'ordonnance"}
      </button>
    </div>
  );
}