import { Settings } from "lucide-react";
import PageEnConstruction from "../components/PageEnConstruction";

export default function Parametres() {
  return (
    <PageEnConstruction
      titre="Paramètres"
      description="Configuration du système"
      icone={Settings}
    />
  );
}