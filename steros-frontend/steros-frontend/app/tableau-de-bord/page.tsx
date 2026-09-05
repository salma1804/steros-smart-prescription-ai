"use client";

import { useState, useEffect } from "react";
import { FileText, Clock, TrendingUp, Edit3 } from "lucide-react";
import { lireHistorique, EntreeHistorique } from "../lib/historique";




function CarteIndicateur({
  titre,
  valeur,
  sousTitre,
  icone: Icone,
}: {
  titre: string;
  valeur: string;
  sousTitre: string;
  icone: typeof FileText;
}) {
  return (
    <div className="bg-white rounded-xl shadow-sm p-5 flex items-center justify-between">
      <div>
        <p className="text-xs text-gray-400 mb-1">{titre}</p>
        <p className="text-2xl font-bold text-gray-900">{valeur}</p>
        <p className="text-xs text-gray-400 mt-1">{sousTitre}</p>
      </div>
      <div className="w-10 h-10 rounded-lg bg-[#00B4B8]/10 flex items-center justify-center">
        <Icone size={20} className="text-[#00B4B8]" />
      </div>
    </div>
  );
}

export default function TableauDeBord() {
  const [historique] = useState<EntreeHistorique[]>(() => lireHistorique());

  const nombreOrdonnances = historique.length;
  const tempsMoyen =
    nombreOrdonnances > 0
      ? historique.reduce((acc, e) => acc + e.tempsTraitementSecondes, 0) / nombreOrdonnances
      : 0;
  const tauxMoyen =
    nombreOrdonnances > 0
      ? historique.reduce((acc, e) => acc + e.tauxReconnaissance, 0) / nombreOrdonnances
      : 0;
  const totalCorrections = historique.reduce((acc, e) => acc + e.correctionsManuelles, 0);

  return (
    <div className="space-y-6">
      <div className="bg-white rounded-xl shadow-sm p-6">
        <h1 className="text-2xl font-bold text-gray-900">Tableau de bord</h1>
        <p className="text-gray-500 text-sm mt-1">Indicateurs de performance du module</p>
      </div>

      <div className="grid grid-cols-4 gap-4">
        <CarteIndicateur
          titre="Ordonnances traitées"
          valeur={nombreOrdonnances.toString()}
          sousTitre="Total"
          icone={FileText}
        />
        <CarteIndicateur
          titre="Temps moyen de traitement"
          valeur={`${tempsMoyen.toFixed(0)} sec`}
          sousTitre="Par ordonnance"
          icone={Clock}
        />
        <CarteIndicateur
          titre="Taux de reconnaissance"
          valeur={`${tauxMoyen.toFixed(0)}%`}
          sousTitre="Moyenne"
          icone={TrendingUp}
        />
        <CarteIndicateur
          titre="Corrections manuelles"
          valeur={totalCorrections.toString()}
          sousTitre="Total"
          icone={Edit3}
        />
      </div>

      {nombreOrdonnances === 0 && (
        <div className="bg-white rounded-xl shadow-sm p-6 text-center text-gray-400 text-sm">
          Aucune ordonnance traitée pour le moment. Les indicateurs apparaîtront après le premier import.
        </div>
      )}
    </div>
  );
}