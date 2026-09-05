"use client";

import { useState } from "react";
import Link from "next/link";
import { History, Bell } from "lucide-react";
import EtapesWorkflow from "./components/EtapesWorkflow";
import ZoneImport from "./components/ZoneImport";
import ColonneResultats from "./components/ColonneResultats";
import ColonneOrdonnance from "./components/ColonneOrdonnance";
import { ResultatsOrdonnance } from "./lib/api";
import { ajouterEntreeHistorique } from "./lib/historique";

export interface ExamenModifiable {
  libelle: string;
  statut: string;
}

export interface InfosAdminModifiables {
  patient: string;
  date: string;
  prescripteur: string;
  cachet: string;
}

export default function Home() {
  const [resultats, setResultats] = useState<ResultatsOrdonnance | null>(null);
  const [urlApercu, setUrlApercu] = useState<string | null>(null);
  const [examens, setExamens] = useState<ExamenModifiable[]>([]);
  const [enChargement, setEnChargement] = useState(false);
  const [infosAdmin, setInfosAdmin] = useState<InfosAdminModifiables>({
    patient: "",
    date: "",
    prescripteur: "",
    cachet: "",
  });
  const [dernierResultatsTraite, setDernierResultatsTraite] = useState<ResultatsOrdonnance | null>(null);

  if (resultats !== dernierResultatsTraite) {
    setDernierResultatsTraite(resultats);

    if (resultats?.erreur) {
      setExamens([]);
      setInfosAdmin({ patient: "", date: "", prescripteur: "", cachet: "" });
    } else if (resultats?.zone_analyses?.examens_identifies) {
      const listeInitiale = resultats.zone_analyses.examens_identifies.map((ex) => ({
        libelle: ex.libelle_trouve,
        statut: ex.statut,
      }));
      setExamens(listeInitiale);

      setInfosAdmin({
        patient: resultats?.zone_patient?.texte ?? "",
        date: resultats?.zone_date?.texte ?? "",
        prescripteur: resultats?.zone_prescripteur?.texte ?? "",
        cachet: resultats?.zone_cachet?.texte ?? "",
      });
    } else {
      setExamens([]);
      setInfosAdmin({
        patient: resultats?.zone_patient?.texte ?? "",
        date: resultats?.zone_date?.texte ?? "",
        prescripteur: resultats?.zone_prescripteur?.texte ?? "",
        cachet: resultats?.zone_cachet?.texte ?? "",
      });
    }
  }

  const supprimerExamen = (index: number) => {
    setExamens((liste) => liste.filter((_, i) => i !== index));
  };

  const ajouterExamen = (libelle: string) => {
    if (libelle.trim() === "") return;
    setExamens((liste) => [...liste, { libelle: libelle.trim(), statut: "AjoutéManuellement" }]);
  };

  const modifierInfoAdmin = (champ: keyof InfosAdminModifiables, valeur: string) => {
    setInfosAdmin((infos) => ({ ...infos, [champ]: valeur }));
  };

  const annulerTout = () => {
    const confirmation = window.confirm(
      "Voulez-vous vraiment annuler ? Toutes les données de cette ordonnance seront perdues."
    );
    if (confirmation) {
      setResultats(null);
      setUrlApercu(null);
      setExamens([]);
    }
  };

  const importerDonnees = () => {
    const examensReconnus = examens.filter((e) => e.statut !== "AjoutéManuellement").length;
    const tauxReconnaissance = examens.length > 0 ? (examensReconnus / examens.length) * 100 : 0;
    const correctionsManuelles = examens.filter((e) => e.statut === "AjoutéManuellement").length;

    ajouterEntreeHistorique({
      date: new Date().toISOString(),
      patient: infosAdmin.patient || "Non renseigné",
      examens: examens.map((e) => e.libelle),
      tempsTraitementSecondes: 18,
      tauxReconnaissance,
      correctionsManuelles,
    });

    const donneesAExporter = {
      ...infosAdmin,
      examens_valides: examens.map((e) => e.libelle),
      date_export: new Date().toISOString(),
    };

    const contenuJson = JSON.stringify(donneesAExporter, null, 2);
    const fichierBlob = new Blob([contenuJson], { type: "application/json" });
    const urlTelechargement = URL.createObjectURL(fichierBlob);

    const lienTelechargement = document.createElement("a");
    lienTelechargement.href = urlTelechargement;
    lienTelechargement.download = `ordonnance_${Date.now()}.json`;
    lienTelechargement.click();

    URL.revokeObjectURL(urlTelechargement);
  };

  const etapeActive = resultats ? 3 : enChargement ? 2 : 1;

  return (
    <div className="space-y-6">
      <div className="bg-white rounded-xl shadow-sm p-6 flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Admission intelligente</h1>
          <p className="text-gray-500 text-sm mt-1">Scan et importation automatique des ordonnances</p>
        </div>
        <div className="flex items-center gap-3">
          <Link
            href="/historique"
            className="flex items-center gap-2 border border-gray-200 rounded-lg px-4 py-2 text-sm font-medium text-gray-700 hover:bg-gray-50"
          >
            <History size={16} />
            Historique des ordonnances
          </Link>
          <button className="w-10 h-10 rounded-full border border-gray-200 flex items-center justify-center hover:bg-gray-50">
            <Bell size={18} className="text-gray-600" />
          </button>
        </div>
      </div>

      <EtapesWorkflow etapeActive={etapeActive} />

      <div className="grid grid-cols-3 gap-6">
        <ColonneOrdonnance urlImage={urlApercu} />

        {resultats ? (
          <div className="col-span-2 space-y-4">
            <ColonneResultats
              infosAdmin={infosAdmin}
              onModifierInfoAdmin={modifierInfoAdmin}
              examens={examens}
              onSupprimerExamen={supprimerExamen}
              onAjouterExamen={ajouterExamen}
            />

            <div className="flex gap-2">
              <button
                onClick={annulerTout}
                className="flex-1 border border-gray-200 rounded-lg py-2 text-sm font-medium text-gray-600 hover:bg-gray-50"
              >
                Annuler
              </button>
              <button
                onClick={importerDonnees}
                className="flex-1 bg-[#0F1B2D] text-white rounded-lg py-2 text-sm font-medium hover:bg-[#1a2b45]"
              >
                Importer dans Steros Lab
              </button>
            </div>
          </div>
        ) : (
          <div className="col-span-2">
            <ZoneImport
              onResultats={setResultats}
              onApercuImage={setUrlApercu}
              onChangementChargement={setEnChargement}
            />
          </div>
        )}
      </div>
    </div>
  );
}