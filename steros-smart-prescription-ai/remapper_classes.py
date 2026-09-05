import os

# Mapping : ancien_index -> nouvel_index
# zone_analyses(0)->0, zone_cachet(1)->1, zone_commentaires(2)->0 (fusionné avec zone_analyses),
# zone_date(3)->2, zone_patient(4)->3, zone_prescripteur(5)->4
MAPPING = {
    0: 0,  # zone_analyses -> zone_analyses
    1: 1,  # zone_cachet -> zone_cachet
    2: 0,  # zone_commentaires -> fusionné dans zone_analyses
    3: 2,  # zone_date -> nouvel index 2
    4: 3,  # zone_patient -> nouvel index 3
    5: 4,  # zone_prescripteur -> nouvel index 4
}

DOSSIERS_LABELS = [
    "export_labelstudio_v4/labels",
]


def remapper_fichier(chemin_fichier):
    lignes_modifiees = []
    with open(chemin_fichier, "r") as f:
        for ligne in f:
            elements = ligne.strip().split()
            if not elements:
                continue
            ancien_index = int(elements[0])
            nouvel_index = MAPPING[ancien_index]
            elements[0] = str(nouvel_index)
            lignes_modifiees.append(" ".join(elements))

    with open(chemin_fichier, "w") as f:
        f.write("\n".join(lignes_modifiees) + "\n")


def remapper_tout():
    for dossier in DOSSIERS_LABELS:
        fichiers = [f for f in os.listdir(dossier) if f.endswith(".txt")]
        for nom_fichier in fichiers:
            remapper_fichier(os.path.join(dossier, nom_fichier))
        print(f"{len(fichiers)} fichiers remappés dans {dossier}")


if __name__ == "__main__":
    remapper_tout()