import { Users } from "lucide-react";
import PageEnConstruction from "../components/PageEnConstruction";

export default function Patients() {
  return (
    <PageEnConstruction
      titre="Patients"
      description="Gestion des dossiers patients"
      icone={Users}
    />
  );
}