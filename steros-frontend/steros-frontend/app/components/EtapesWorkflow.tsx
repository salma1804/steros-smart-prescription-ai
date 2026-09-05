const etapes = [
  { numero: 1, titre: "Acquisition", sousTitre: "Importer l'ordonnance" },
  { numero: 2, titre: "Traitement", sousTitre: "OCR et analyse IA" },
  { numero: 3, titre: "Vérification", sousTitre: "Contrôle et validation" },
  { numero: 4, titre: "Importation", sousTitre: "Enregistrement" },
];

export default function EtapesWorkflow({ etapeActive }: { etapeActive: number }) {
  return (
    <div className="flex items-center bg-white rounded-xl p-6 shadow-sm">
      {etapes.map((etape, index) => (
        <div key={etape.numero} className="flex items-center flex-1">
          <div className="flex items-center gap-3">
            <div
              className={`w-9 h-9 rounded-full flex items-center justify-center font-semibold text-sm ${
                etape.numero <= etapeActive
                  ? "bg-[#00B4B8] text-white"
                  : "bg-gray-200 text-gray-400"
              }`}
            >
              {etape.numero}
            </div>
            <div>
              <p
                className={`text-sm font-semibold ${
                  etape.numero <= etapeActive ? "text-gray-900" : "text-gray-400"
                }`}
              >
                {etape.titre}
              </p>
              <p className="text-xs text-gray-400">{etape.sousTitre}</p>
            </div>
          </div>

          {index < etapes.length - 1 && (
            <div className="flex-1 border-t-2 border-dashed border-gray-200 mx-4" />
          )}
        </div>
      ))}
    </div>
  );
}