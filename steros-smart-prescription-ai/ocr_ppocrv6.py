from paddleocr import PaddleOCR

print("Chargement de PP-OCRv6...")
lecteur_ppocr = PaddleOCR(
    use_doc_orientation_classify=False,
    use_doc_unwarping=False,
    use_textline_orientation=True,
    lang='fr',
    enable_mkldnn=False,  # ← désactive l'accélération oneDNN qui plante
)
print("PP-OCRv6 chargé.")


def extraire_texte_ppocrv6(image_cv2):
    """
    Extrait le texte avec PP-OCRv6. Retourne (texte, confiance_moyenne_pourcentage).
    """
    resultats = lecteur_ppocr.predict(image_cv2)

    if not resultats or len(resultats) == 0:
        return "", 0

    textes = []
    confiances = []

    for res in resultats:
        if "rec_texts" in res and "rec_scores" in res:
            for texte, score in zip(res["rec_texts"], res["rec_scores"]):
                textes.append(texte)
                confiances.append(score * 100)

    texte_complet = " ".join(textes)
    confiance_moyenne = sum(confiances) / len(confiances) if confiances else 0

    return texte_complet, confiance_moyenne


if __name__ == "__main__":
    import cv2
    image_test = cv2.imread("test/testordonnance.jpg")  # adapte avec une image manuscrite
    if image_test is not None:
        texte, confiance = extraire_texte_ppocrv6(image_test)
        print(f"Texte extrait : {texte}")
        print(f"Confiance moyenne : {confiance:.1f}%")