import pytesseract
import cv2

# Chemin vers Tesseract (Windows) — adapte si besoin, comme vu précédemment
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'


def extraire_texte(image_pretraitee):
    """
    Extrait le texte brut d'une image déjà prétraitée (niveaux de gris + binarisée).
    Retourne le texte extrait sous forme de chaîne de caractères.
    """
    # lang='fra' = on indique à Tesseract que le texte est en français
    texte = pytesseract.image_to_string(image_pretraitee, lang='fra')
    return texte


def extraire_texte_avec_confiance(image_pretraitee, psm=6):
    config = f'--psm {psm}'
    donnees = pytesseract.image_to_data(
        image_pretraitee, lang='fra', config=config, output_type=pytesseract.Output.DICT
    )

    mots = []
    confiances = []

    for i in range(len(donnees['text'])):
        mot = donnees['text'][i].strip()
        confiance = int(donnees['conf'][i])

        if mot != "" and confiance > 0:
            mots.append(mot)
            confiances.append(confiance)

    texte_complet = " ".join(mots)
    confiance_moyenne = sum(confiances) / len(confiances) if confiances else 0

    return texte_complet, confiance_moyenne

if __name__ == "__main__":
    from acquisition import charger_image
    from pretraitement import pretraiter_image

    image = charger_image("data/ordonnances/exemple1.jpg")  # adapte le nom

    if image is not None:
        image_traitee = pretraiter_image(image)

        texte, confiance = extraire_texte_avec_confiance(image_traitee)

        print("----- TEXTE EXTRAIT -----")
        print(texte)
        print("--------------------------")
        print(f"Confiance moyenne OCR : {confiance:.1f}%")