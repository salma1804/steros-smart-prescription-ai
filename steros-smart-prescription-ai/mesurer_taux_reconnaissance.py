from pipeline_complet import traiter_ordonnance
from verite_terrain import ECHANTILLON_TEST


def similarite_simple(texte1, texte2):
    return texte1.strip().upper() == texte2.strip().upper()


def mesurer_taux_reconnaissance():
    total_images = len(ECHANTILLON_TEST)
    images_avec_zone_detectee = 0

    total_examens_sur_images_detectees = 0
    examens_corrects_sur_images_detectees = 0

    for cas_test in ECHANTILLON_TEST:
        resultats = traiter_ordonnance(cas_test["image"])

        if "examens_attendus" not in cas_test:
            continue

        zone_detectee = "zone_analyses" in resultats
        if zone_detectee:
            images_avec_zone_detectee += 1

            examens_obtenus = []
            if "examens_identifies" in resultats["zone_analyses"]:
                for ex in resultats["zone_analyses"]["examens_identifies"]:
                    examens_obtenus.append((ex.get("libelle_trouve") if isinstance(ex, dict) else str(ex)).upper())

            attendus = set(e.upper() for e in cas_test["examens_attendus"])
            obtenus = set(examens_obtenus)

            total_examens_sur_images_detectees += len(attendus)
            examens_corrects_sur_images_detectees += len(attendus & obtenus)

    print(f"\n===== RESULTATS DECOMPOSES (HONNETES) =====")
    print(f"Taux de détection de zone_analyses : {(images_avec_zone_detectee/total_images*100):.1f}% ({images_avec_zone_detectee}/{total_images} images)")
    if total_examens_sur_images_detectees > 0:
        print(f"Taux de reconnaissance QUAND la zone est détectée : "
              f"{(examens_corrects_sur_images_detectees/total_examens_sur_images_detectees*100):.1f}%")

if __name__ == "__main__":
    mesurer_taux_reconnaissance()