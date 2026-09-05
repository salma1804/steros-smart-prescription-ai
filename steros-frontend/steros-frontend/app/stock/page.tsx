import { Package } from "lucide-react";
import PageEnConstruction from "../components/PageEnConstruction";

export default function Stock() {
  return (
    <PageEnConstruction
      titre="Stock"
      description="Gestion des stocks et consommables"
      icone={Package}
    />
  );
}