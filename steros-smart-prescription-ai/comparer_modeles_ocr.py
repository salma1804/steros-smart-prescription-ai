import cv2
import pytesseract

pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'


def tester_avec_modele(image, dossier_tessdata=None, label=""):
    config = f'--tessdata-dir {dossier_tessdata}' if dossier_tessdata else ''

    donnees = pytesseract.image_to_data(image, lang='fra', config=config, output_type=pytesseract.Output.DICT)

    mots = []
    confiances = []
    for i in range(len(donnees['text'])):
        mot = donnees['text'][i].strip()
        conf = int(donnees['conf'][i])
        if mot != "" and conf > 0:
            mots.append(mot)
            confiances.append(conf)

    texte = " ".join(mots)
    confiance_moyenne = sum(confiances) / len(confiances) if confiances else 0

    print(f"----- {label} -----")
    print(f"Texte : {texte}")
    print(f"Confiance moyenne : {confiance_moyenne:.1f}%\n")
if __name__ == "__main__":
    from pretraitement import pretraiter_image

    chemin_image = r"C:\Users\User\Desktop\steros-smart-prescription-ai\testData\Autre10_06_2025 10-56-43 .jpg"  # adapte avec l'image/zone que tu veux comparer
    image = cv2.imread(chemin_image)

    if image is None:
        print(f"Image introuvable : {chemin_image}")
    else:
        image_pretraitee = pretraiter_image(image)

        # Modèle "best" (déjà en place par défaut dans tessdata)
        tester_avec_modele(image_pretraitee, dossier_tessdata=None, label="MODELE BEST (actuel)")

        # Modèle "standard" (ancien, via dossier séparé)
        tester_avec_modele(image_pretraitee, dossier_tessdata="C:/tessdata_standard", label="MODELE STANDARD (ancien)")