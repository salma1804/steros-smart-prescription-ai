import os
import shutil

DOSSIER_POOL_COMPLET = "data/ordonnances"
DOSSIER_LOT1 = "data/echantillon_annotation"
DOSSIER_LOT2 = "data/nouvelle_echantillon_annotation"
DOSSIER_NON_SELECTIONNE = "data/nonselectionne"


def isoler_non_selectionnees():
    # Ensemble des images déjà utilisées dans les 2 lots
    images_lot1 = set(os.listdir(DOSSIER_LOT1)) if os.path.exists(DOSSIER_LOT1) else set()
    images_lot2 = set(os.listdir(DOSSIER_LOT2)) if os.path.exists(DOSSIER_LOT2) else set()
    images_deja_utilisees = images_lot1 | images_lot2  # union des deux ensembles

    toutes_les_images = [
        f for f in os.listdir(DOSSIER_POOL_COMPLET)
        if f.lower().endswith((".jpg", ".jpeg", ".png"))
    ]

    images_non_selectionnees = [
        f for f in toutes_les_images if f not in images_deja_utilisees
    ]

    print(f"Pool complet : {len(toutes_les_images)} images")
    print(f"Déjà utilisées (lot1 + lot2) : {len(images_deja_utilisees)} images")
    print(f"Non sélectionnées : {len(images_non_selectionnees)} images")

    os.makedirs(DOSSIER_NON_SELECTIONNE, exist_ok=True)

    for nom_fichier in images_non_selectionnees:
        shutil.copy(
            os.path.join(DOSSIER_POOL_COMPLET, nom_fichier),
            os.path.join(DOSSIER_NON_SELECTIONNE, nom_fichier)
        )

    print(f"{len(images_non_selectionnees)} images copiées dans {DOSSIER_NON_SELECTIONNE}")


if __name__ == "__main__":
    isoler_non_selectionnees()