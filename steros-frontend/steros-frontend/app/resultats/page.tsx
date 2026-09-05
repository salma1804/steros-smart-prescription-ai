import { ClipboardCheck } from "lucide-react";
import PageEnConstruction from "../components/PageEnConstruction";

export default function Resultats() {
  return (
    <PageEnConstruction
      titre="Résultats"
      description="Consultation des résultats d'analyses"
      icone={ClipboardCheck}
    />
  );
}