import { ExamenModifiable, InfosAdminModifiables } from "../page";
import { useState, useRef } from "react";
import { X } from "lucide-react";
import { rechercherExamens, SuggestionExamen } from "../lib/api";

function ChampEditable({
  label,
  valeur,
  onChange,
}: {
  label: string;
  valeur: string;
  onChange: (v: string) => void;
}) {
  return (
    <div>
      <p className="text-xs text-gray-400 mb-1">{label}</p>
      <input
        type="text"
        value={valeur}
        onChange={(e) => onChange(e.target.value)}
        placeholder="Non détecté"
        className="w-full text-sm text-gray-900 border border-gray-200 rounded-lg px-2 py-1.5 focus:border-[#00B4B8] focus:outline-none"
      />
    </div>
  );
}

function badgeStatut(statut: string) {
  const styles: Record<string, string> = {
    Reconnu: "bg-green-50 text-green-600",
    Incertain: "bg-orange-50 text-orange-600",
    AjoutéManuellement: "bg-blue-50 text-blue-600",
  };

  const libelles: Record<string, string> = {
    Reconnu: "Fiable",
    Incertain: "À vérifier",
    AjoutéManuellement: "Ajouté",
  };

  const style = styles[statut] || "bg-gray-50 text-gray-500";
  const libelle = libelles[statut] || statut;

  return (
    <span className={`text-xs font-medium px-2 py-0.5 rounded-full ${style}`}>
      {libelle}
    </span>
  );
}

interface ColonneResultatsProps {
  infosAdmin: InfosAdminModifiables;
  onModifierInfoAdmin: (champ: keyof InfosAdminModifiables, valeur: string) => void;
  examens: ExamenModifiable[];
  onSupprimerExamen: (index: number) => void;
  onAjouterExamen: (libelle: string) => void;
}

export default function ColonneResultats({
  infosAdmin,
  onModifierInfoAdmin,
  examens,
  onSupprimerExamen,
  onAjouterExamen,
}: ColonneResultatsProps) {
  const [nouvelExamen, setNouvelExamen] = useState("");
  const [suggestions, setSuggestions] = useState<SuggestionExamen[]>([]);
  const [suggestionsVisibles, setSuggestionsVisibles] = useState(false);
  const delaiRecherche = useRef<ReturnType<typeof setTimeout> | null>(null);

  const gererChangementRecherche = (valeur: string) => {
    setNouvelExamen(valeur);
    setSuggestionsVisibles(true);

    if (delaiRecherche.current) clearTimeout(delaiRecherche.current);

    if (valeur.trim().length < 2) {
      setSuggestions([]);
      return;
    }

    delaiRecherche.current = setTimeout(async () => {
      const resultats = await rechercherExamens(valeur);
      setSuggestions(resultats);
    }, 300);
  };

  const choisirSuggestion = (libelle: string) => {
    onAjouterExamen(libelle);
    setNouvelExamen("");
    setSuggestions([]);
    setSuggestionsVisibles(false);
  };

  const gererAjout = () => {
    onAjouterExamen(nouvelExamen);
    setNouvelExamen("");
    setSuggestions([]);
  };

  return (
    <div className="grid grid-cols-2 gap-6">
      <div className="bg-white rounded-xl shadow-sm p-5">
        <h2 className="text-sm font-semibold text-gray-700 mb-4">Informations extraites</h2>
        <div className="space-y-3">
          <ChampEditable
            label="Patient"
            valeur={infosAdmin.patient}
            onChange={(v) => onModifierInfoAdmin("patient", v)}
          />
          <ChampEditable
            label="Date de prescription"
            valeur={infosAdmin.date}
            onChange={(v) => onModifierInfoAdmin("date", v)}
          />
          <ChampEditable
            label="Prescripteur"
            valeur={infosAdmin.prescripteur}
            onChange={(v) => onModifierInfoAdmin("prescripteur", v)}
          />
          <ChampEditable
            label="Cachet"
            valeur={infosAdmin.cachet}
            onChange={(v) => onModifierInfoAdmin("cachet", v)}
          />
        </div>
      </div>

      <div className="bg-white rounded-xl shadow-sm p-5">
        <h2 className="text-sm font-semibold text-gray-700 mb-4">Analyses reconnues par l&apos;IA</h2>

        {examens.length === 0 ? (
          <p className="text-sm text-gray-400 mb-4">Aucun examen identifié</p>
        ) : (
          <div className="space-y-2 mb-4">
            {examens.map((examen, index) => (
              <div key={index} className="flex items-center justify-between text-sm py-2 border-b border-gray-50">
                <div className="flex items-center gap-2">
                  <span className="text-green-500">✔</span>
                  <p className="font-medium text-gray-900">{examen.libelle}</p>
                </div>
                <div className="flex items-center gap-2">
                  {badgeStatut(examen.statut)}
                  <button onClick={() => onSupprimerExamen(index)} className="text-gray-400 hover:text-red-500">
                    <X size={16} />
                  </button>
                </div>
              </div>
            ))}
          </div>
        )}

        <div className="relative">
          <div className="flex gap-2">
            <input
              type="text"
              value={nouvelExamen}
              onChange={(e) => gererChangementRecherche(e.target.value)}
              onFocus={() => setSuggestionsVisibles(true)}
              placeholder="Ajouter un examen (ex: NFS, CRP...)"
              className="flex-1 border border-gray-200 rounded-lg px-3 py-2 text-sm"
            />
            <button
              onClick={gererAjout}
              className="bg-[#00B4B8] text-white px-4 py-2 rounded-lg text-sm font-medium"
            >
              Ajouter
            </button>
          </div>

          {suggestionsVisibles && suggestions.length > 0 && (
            <div className="absolute z-10 w-full mt-1 bg-white border border-gray-200 rounded-lg shadow-lg max-h-48 overflow-auto">
              {suggestions.map((suggestion, index) => (
                <button
                  key={index}
                  onClick={() => choisirSuggestion(suggestion.libelle)}
                  className="w-full text-left px-3 py-2 text-sm hover:bg-gray-50 border-b border-gray-50 last:border-0"
                >
                  {suggestion.libelle}
                </button>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}