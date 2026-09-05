export default function ColonneOrdonnance({ urlImage }: { urlImage: string | null }) {
  return (
    <div className="bg-white rounded-xl shadow-sm p-5">
      <h2 className="text-sm font-semibold text-gray-700 mb-4">
        Ordonnance importée
      </h2>

      <div className="bg-gray-50 rounded-lg overflow-hidden min-h-[400px] flex items-center justify-center">
        {urlImage ? (
          // eslint-disable-next-line @next/next/no-img-element
          <img src={urlImage} alt="Ordonnance importée" className="max-w-full max-h-[500px] object-contain" />
        ) : (
          <p className="text-gray-400 text-sm">Aucune image importée</p>
        )}
      </div>
    </div>
  );
}