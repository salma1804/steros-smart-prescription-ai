# mch kasamnha data annote dans yolo l train 85% w val 15%
import os
import random
import shutil

DOSSIER_EXPORT = "export_labelstudio_v4"
DOSSIER_FINAL = "dataset_zones_v4"
RATIO_TRAIN = 0.85

random.seed(42)

images_dir = os.path.join(DOSSIER_EXPORT, "images")
labels_dir = os.path.join(DOSSIER_EXPORT, "labels")

fichiers_images = [f for f in os.listdir(images_dir) if f.lower().endswith((".jpg", ".jpeg", ".png"))]
random.shuffle(fichiers_images)

nb_train = int(len(fichiers_images) * RATIO_TRAIN)
images_train = fichiers_images[:nb_train]
images_val = fichiers_images[nb_train:]

for sous_ensemble, nom_dossier in [(images_train, "train"), (images_val, "val")]:
    os.makedirs(os.path.join(DOSSIER_FINAL, "images", nom_dossier), exist_ok=True)
    os.makedirs(os.path.join(DOSSIER_FINAL, "labels", nom_dossier), exist_ok=True)

    for nom_image in sous_ensemble:
        nom_label = os.path.splitext(nom_image)[0] + ".txt"

        chemin_label_source = os.path.join(labels_dir, nom_label)
        if not os.path.exists(chemin_label_source):
            print(f"Attention : pas de label trouvé pour {nom_image}, ignoré.")
            continue

        shutil.copy(
            os.path.join(images_dir, nom_image),
            os.path.join(DOSSIER_FINAL, "images", nom_dossier, nom_image)
        )
        shutil.copy(
            chemin_label_source,
            os.path.join(DOSSIER_FINAL, "labels", nom_dossier, nom_label)
        )

print(f"Train : {len(images_train)} images")
print(f"Val : {len(images_val)} images")