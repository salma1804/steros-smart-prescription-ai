import "./globals.css";
import Sidebar from "./components/Sidebar";

export const metadata = {
  title: "Steros Lab - Smart Prescription AI",
  description: "Module de reconnaissance intelligente des ordonnances médicales",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="fr" className="bg-gray-50">
      <body className="flex min-h-screen bg-gray-50 m-0">
        <Sidebar />
        <main className="ml-64 flex-1 p-8">{children}</main>
      </body>
    </html>
  );
}