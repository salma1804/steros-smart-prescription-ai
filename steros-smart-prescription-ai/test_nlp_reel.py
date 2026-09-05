from pipeline_complet import traiter_ordonnance
from moteur_nlp import analyser_texte_complet


def tester_nlp_sur_ordonnance(chemin_image):
    print(f"===== Traitement de {chemin_image} =====\n")

    resultats_ocr = traiter_ordonnance(chemin_image)

    if "zone_analyses" not in resultats_ocr:
        print("zone_analyses non détectée par YOLO26.")
        return

    zone_analyses = resultats_ocr["zone_analyses"]

    # --- Cas 1 : template matching a réussi -> ce sont les VRAIS examens, pas besoin du NLP sur le texte brut ---
    if "examens_coches_precis" in zone_analyses:
        print("----- Examens demandés (via template matching, source fiable) -----")
        for examen in zone_analyses["examens_coches_precis"]:
            print(f"  - {examen}")
        return  # on s'arrête là, le NLP sur le texte complet n'apporterait rien d'utile ici

    # --- Cas 2 : pas de template, on analyse le texte OCR brut avec le NLP ---
    texte_brut = zone_analyses.get("texte", "")
    print(f"----- Texte brut (aucun template applicable, ordonnance libre) -----")
    print(texte_brut)
    print()

    print(f"----- Examens identifiés par le NLP -----")
    resultats_nlp = analyser_texte_complet(texte_brut)
    for r in resultats_nlp:
        print(f"  '{r['texte_detecte']}' -> {r['libelle_trouve']} (statut: {r['statut']})")


if __name__ == "__main__":
    chemin_test = "test/ordonnancetest.jpg"  # adapte avec l'image que tu veux tester
    tester_nlp_sur_ordonnance(r'C:\Users\User\Desktop\steros-smart-prescription-ai\testData\Autre09_06_2025 15-32-17 .jpg')