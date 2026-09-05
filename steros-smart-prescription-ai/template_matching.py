import json
import cv2
import numpy as np


def charger_template(nom_template):
    with open(f"templates/{nom_template}.json", "r", encoding="utf-8") as f:
        return json.load(f)


def case_est_cochee_a_position(image_grise, x, y, taille=12, seuil=0.20):
    """Vérifie si la case autour de (x, y) est cochée."""
    y1, y2 = max(0, y - taille), y + taille
    x1, x2 = max(0, x - taille), x + taille
    region = image_grise[y1:y2, x1:x2]

    if region.size == 0:
        return False

    _, binaire = cv2.threshold(region, 180, 255, cv2.THRESH_BINARY_INV)
    proportion_sombre = np.sum(binaire > 0) / binaire.size
    return proportion_sombre > seuil


def extraire_analyses_via_template(image_originale_complete, nom_template):
    """
    Utilise un template calibré pour extraire précisément les examens cochés.
    ATTENTION : les coordonnées du template sont relatives à l'IMAGE COMPLÈTE
    (pas à la zone_analyses découpée par YOLO26), puisque la calibration a été
    faite sur testordonnance.jpg en entier.
    """
    template = charger_template(nom_template)

    if len(image_originale_complete.shape) == 3:
        image_grise = cv2.cvtColor(image_originale_complete, cv2.COLOR_BGR2GRAY)
    else:
        image_grise = image_originale_complete

    examens_coches = []
    for case in template:
        if case_est_cochee_a_position(image_grise, case["x"], case["y"]):
            examens_coches.append(case["libelle"])

    return examens_coches

if __name__ == "__main__":
    image_test = cv2.imread(r'C:\Users\User\Desktop\steros-smart-prescription-ai\test\Autre02_06_2025 06-49-06 .jpg')
    resultats = extraire_analyses_via_template(image_test, "lam_examens_laboratoire")
    print(f"Examens cochés détectés : {resultats}")