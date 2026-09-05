import { LucideIcon } from "lucide-react";

export default function PageEnConstruction({
  titre,
  description,
  icone: Icone,
}: {
  titre: string;
  description: string;
  icone: LucideIcon;
}) {
  return (
    <div className="space-y-6">
      <div className="bg-white rounded-xl shadow-sm p-6">
        <h1 className="text-2xl font-bold text-gray-900">{titre}</h1>
        <p className="text-gray-500 text-sm mt-1">{description}</p>
      </div>

      <div className="bg-white rounded-xl shadow-sm p-12 text-center">
        <Icone size={48} className="mx-auto text-gray-300 mb-4" />
        <p className="text-gray-500 font-medium">Module en cours de développement</p>
        <p className="text-gray-400 text-sm mt-1">
          Cette section sera disponible dans une prochaine version.
        </p>
      </div>
    </div>
  );
}