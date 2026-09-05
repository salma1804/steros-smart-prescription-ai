import { ShieldCheck } from "lucide-react";
import PageEnConstruction from "../components/PageEnConstruction";

export default function Qualite() {
  return (
    <PageEnConstruction
      titre="Qualité"
      description="Suivi qualité et conformité"
      icone={ShieldCheck}
    />
  );
}