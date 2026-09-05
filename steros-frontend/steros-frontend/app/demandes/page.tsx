import { Inbox } from "lucide-react";
import PageEnConstruction from "../components/PageEnConstruction";

export default function Demandes() {
  return (
    <PageEnConstruction
      titre="Demandes"
      description="Gestion des demandes en attente"
      icone={Inbox}
    />
  );
}