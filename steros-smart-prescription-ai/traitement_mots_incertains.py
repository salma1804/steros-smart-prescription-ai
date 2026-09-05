import cv2
import pytesseract
from pretraitement import pretraiter_image

pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'


def traiter_zone_avec_marqueurs_incertitude(image_zone_pretraitee, seuil_confiance=60):
    """
    Traite une zone mot par mot, marque les mots incertains,
    tout en préservant la structure des lignes d'origine.
    """
    donnees = pytesseract.image_to_data(image_zone_pretraitee, lang='fra', output_type=pytesseract.Output.DICT)

    lignes = {}

    for i in range(len(donnees['text'])):
        mot = donnees['text'][i].strip()
        confiance = int(donnees['conf'][i])

        if mot == "":
            continue

        cle_ligne = (donnees['block_num'][i], donnees['par_num'][i], donnees['line_num'][i])

        if confiance >= seuil_confiance:
            mot_final = mot
        else:
            mot_final = "[MOT_ILLISIBLE]"

        if cle_ligne not in lignes:
            lignes[cle_ligne] = []
        lignes[cle_ligne].append((donnees['left'][i], mot_final))

    lignes_triees = sorted(lignes.items(), key=lambda item: item[0])

    texte_final = []
    for cle_ligne, mots_de_la_ligne in lignes_triees:
        mots_de_la_ligne.sort(key=lambda m: m[0])
        texte_ligne = " ".join(mot for _, mot in mots_de_la_ligne)
        texte_final.append(texte_ligne)

    return "\n".join(texte_final)


if __name__ == "__main__":
    # Adapte ce chemin vers une image de zone découpée que tu as déjà
    # (générée par debug_analyses_original.jpg lors d'un test précédent du pipeline,
    #  ou n'importe quelle image de test contenant du texte imprimé + manuscrit)
    chemin_image_test = r"C:\Users\User\Desktop\steros-smart-prescription-ai\testData\Autre05_06_2025 09-57-14 .jpg"

    image_zone = cv2.imread(chemin_image_test)

    if image_zone is None:
        print(f"Impossible de charger {chemin_image_test} — vérifie le chemin.")
    else:
        image_pretraitee = pretraiter_image(image_zone)

        resultat = traiter_zone_avec_marqueurs_incertitude(image_pretraitee)

        print("===== TEXTE AVEC MARQUEURS D'INCERTITUDE =====\n")
        print(resultat)