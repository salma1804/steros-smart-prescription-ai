"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import {
  LayoutDashboard, Users, FileText, FlaskConical, ClipboardCheck,
  Inbox, Package, Receipt, ShieldCheck, Settings, ChevronDown,
} from "lucide-react";

const liens = [
  { label: "Tableau de bord", icon: LayoutDashboard, href: "/tableau-de-bord" },
  { label: "Patients", icon: Users, href: "/patients" },
  { label: "Prescriptions", icon: FileText, href: "/" },
  { label: "Analyses", icon: FlaskConical, href: "/analyses" },
  { label: "Résultats", icon: ClipboardCheck, href: "/resultats" },
  { label: "Demandes", icon: Inbox, href: "/demandes" },
  { label: "Stock", icon: Package, href: "/stock" },
  { label: "Facturation", icon: Receipt, href: "/facturation" },
  { label: "Qualité", icon: ShieldCheck, href: "/qualite" },
  { label: "Paramètres", icon: Settings, href: "/parametres" },
];

export default function Sidebar() {
  const cheminActuel = usePathname();

  return (
    <aside className="w-64 bg-[#0F1B2D] text-white flex flex-col fixed h-screen">
      <div className="px-6 py-6 border-b border-white/10">
        <h1 className="text-2xl font-bold leading-tight">
          Steros<br /><span className="text-[#00B4B8]">Lab</span>
        </h1>
      </div>

      <nav className="flex-1 px-3 py-4 space-y-1">
        {liens.map(({ label, icon: Icon, href }) => {
          const estActif = cheminActuel === href;
          return (
            <Link
              key={label}
              href={href}
              className={`flex items-center gap-3 px-4 py-2.5 rounded-lg cursor-pointer text-sm transition-colors ${
                estActif ? "bg-[#00B4B8] text-white font-medium" : "text-gray-300 hover:bg-white/5"
              }`}
            >
              <Icon size={18} />
              {label}
            </Link>
          );
        })}
      </nav>

      <div className="border-t border-white/10 px-4 py-4 flex items-center gap-3">
        <div className="w-9 h-9 rounded-full bg-gray-500 flex items-center justify-center text-sm font-semibold">
          AB
        </div>
        <div className="flex-1">
          <p className="text-sm font-medium">Ahmed Benali</p>
          <p className="text-xs text-gray-400">Secrétaire</p>
        </div>
        <ChevronDown size={16} className="text-gray-400" />
      </div>
    </aside>
  );
}