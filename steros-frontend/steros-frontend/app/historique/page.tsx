"use client";

import { useState } from "react";
import { FileText } from "lucide-react";
import { lireHistorique, EntreeHistorique } from "../lib/historique";

function formaterDate(dateIso: string) {
  const date = new Date(dateIso);
  return date.toLocaleDateString("fr-FR", {
    day: "2-digit",
    month: "2-digit",
    year: "numeric",
    hour: "2-digit",
    minute: "2-digit",
  });
}

export default function HistoriqueOrdonnances() {
  const [historique] = useState<EntreeHistorique[]>(() => lireHistorique());

  return (
    <div className="space-y-6">
      <div className="bg-white rounded-xl shadow-sm p-6">
        <h1 className="text-2xl font-bold text-gray-900">Historique des ordonnances</h1>
        <p className="text-gray-500 text-sm mt-1">
          {historique.length} ordonnance{historique.length > 1 ? "s" : ""} traitée
          {historique.length > 1 ? "s" : ""}
        </p>
      </div>

      {historique.length === 0 ? (
        <div className="bg-white rounded-xl shadow-sm p-10 text-center">
          <FileText size={40} className="mx-auto text-gray-300 mb-3" />
          <p className="text-gray-400 text-sm">Aucune ordonnance traitée pour le moment.</p>
        </div>
      ) : (
        <div className="bg-white rounded-xl shadow-sm overflow-hidden">
          <table className="w-full text-sm">
            <thead>
              <tr className="border-b border-gray-100 text-left text-gray-400">
                <th className="px-5 py-3 font-medium">Date</th>
                <th className="px-5 py-3 font-medium">Patient</th>
                <th className="px-5 py-3 font-medium">Examens</th>
                <th className="px-5 py-3 font-medium">Taux reconnaissance</th>
                <th className="px-5 py-3 font-medium">Corrections</th>
              </tr>
            </thead>
            <tbody>
              {historique.map((entree, index) => (
                <tr key={index} className="border-b border-gray-50 last:border-0">
                  <td className="px-5 py-3 text-gray-600">{formaterDate(entree.date)}</td>
                  <td className="px-5 py-3 font-medium text-gray-900">{entree.patient}</td>
                  <td className="px-5 py-3 text-gray-600">
                    {entree.examens.length > 0 ? entree.examens.join(", ") : "—"}
                  </td>
                  <td className="px-5 py-3">
                    <span
                      className={`font-medium ${
                        entree.tauxReconnaissance >= 80 ? "text-green-600" : "text-orange-500"
                      }`}
                    >
                      {entree.tauxReconnaissance.toFixed(0)}%
                    </span>
                  </td>
                  <td className="px-5 py-3 text-gray-600">{entree.correctionsManuelles}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}