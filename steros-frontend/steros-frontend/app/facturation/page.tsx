import { Receipt } from "lucide-react";
import PageEnConstruction from "../components/PageEnConstruction";

export default function Facturation() {
  return (
    <PageEnConstruction
      titre="Facturation"
      description="Gestion de la facturation patients"
      icone={Receipt}
    />
  );
}