import easyocr

print("Chargement d'EasyOCR...")
lecteur_easyocr = easyocr.Reader(['fr'], gpu=True)
print("EasyOCR chargé.")


def extraire_texte_easyocr(image_cv2):
    """Extrait le texte avec EasyOCR. Retourne (texte, confiance_moyenne_pourcentage)."""
    resultats = lecteur_easyocr.readtext(image_cv2, detail=1)

    if not resultats:
        return "", 0

    textes = [texte for (_, texte, confiance) in resultats]
    confiances = [confiance * 100 for (_, texte, confiance) in resultats]

    texte_complet = " ".join(textes)
    confiance_moyenne = sum(confiances) / len(confiances)

    return texte_complet, confiance_moyenne