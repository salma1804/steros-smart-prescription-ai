import cv2
import numpy as np
import pytesseract

pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'


def detecter_cases(image_grise, taille_min=8, taille_max=30):
    _, binaire = cv2.threshold(image_grise, 200, 255, cv2.THRESH_BINARY_INV)
    contours, _ = cv2.findContours(binaire, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)

    cases = []
    for contour in contours:
        x, y, w, h = cv2.boundingRect(contour)

        if not (taille_min <= w <= taille_max and taille_min <= h <= taille_max):
            continue

        ratio = w / h
        if not (0.7 <= ratio <= 1.3):
            continue

        perimetre = cv2.arcLength(contour, True)
        approx = cv2.approxPolyDP(contour, 0.04 * perimetre, True)
        if not (4 <= len(approx) <= 6):
            continue

        cases.append((x, y, w, h))

    return cases


def case_est_cochee(image_grise, case, seuil_remplissage=0.25):
    x, y, w, h = case
    marge = max(1, w // 5)
    interieur = image_grise[y + marge: y + h - marge, x + marge: x + w - marge]

    if interieur.size == 0:
        return False

    _, interieur_binaire = cv2.threshold(interieur, 180, 255, cv2.THRESH_BINARY_INV)
    proportion_sombre = np.sum(interieur_binaire > 0) / interieur_binaire.size

    return proportion_sombre > seuil_remplissage


def extraire_lignes_de_texte(image_grise):
    donnees = pytesseract.image_to_data(image_grise, lang='fra', output_type=pytesseract.Output.DICT)

    lignes = {}
    for i in range(len(donnees['text'])):
        mot = donnees['text'][i].strip()
        if mot == "":
            continue

        cle_ligne = (donnees['block_num'][i], donnees['par_num'][i], donnees['line_num'][i])
        x, y, w, h = donnees['left'][i], donnees['top'][i], donnees['width'][i], donnees['height'][i]

        if cle_ligne not in lignes:
            lignes[cle_ligne] = []
        lignes[cle_ligne].append((x, y, w, h, mot))

    for cle in lignes:
        lignes[cle].sort(key=lambda m: m[0])

    return list(lignes.values())


def associer_texte_aux_cases_cochees(image_grise, cases_cochees):
    lignes = extraire_lignes_de_texte(image_grise)
    libelles_coches = []

    for (cx, cy, cw, ch) in cases_cochees:
        centre_y_case = cy + ch / 2

        ligne_correspondante = None
        for ligne in lignes:
            y_min_ligne = min(m[1] for m in ligne)
            y_max_ligne = max(m[1] + m[3] for m in ligne)
            if y_min_ligne - 5 <= centre_y_case <= y_max_ligne + 5:
                ligne_correspondante = ligne
                break

        if ligne_correspondante is None:
            continue

        mots_apres_case = [m for m in ligne_correspondante if m[0] > cx]

        if not mots_apres_case:
            continue

        libelle = []
        derniere_position_fin = cx + cw
        for (mx, my, mw, mh, mot) in mots_apres_case:
            espace = mx - derniere_position_fin
            if espace > 60:
                break
            if len(mot) >= 2:
                libelle.append(mot)
            derniere_position_fin = mx + mw

        if libelle:
            libelles_coches.append(" ".join(libelle))

    return libelles_coches


def sauvegarder_debug_cases(image_couleur_originale, cases, cases_cochees):
    image_debug = image_couleur_originale.copy()
    for (x, y, w, h) in cases:
        couleur = (0, 0, 255)
        if (x, y, w, h) in cases_cochees:
            couleur = (0, 255, 0)
        cv2.rectangle(image_debug, (x, y), (x + w, y + h), couleur, 1)
    cv2.imwrite("debug_cases_detectees.jpg", image_debug)


def extraire_analyses_cochees(image_zone_analyses):
    if len(image_zone_analyses.shape) == 3:
        image_grise = cv2.cvtColor(image_zone_analyses, cv2.COLOR_BGR2GRAY)
    else:
        image_grise = image_zone_analyses

    toutes_les_cases = detecter_cases(image_grise)
    cases_cochees = [case for case in toutes_les_cases if case_est_cochee(image_grise, case)]

    sauvegarder_debug_cases(image_zone_analyses, toutes_les_cases, cases_cochees)

    libelles = associer_texte_aux_cases_cochees(image_grise, cases_cochees)
    return libelles


if __name__ == "__main__":
    image_test = cv2.imread("debug_analyses_original.jpg")
    if image_test is not None:
        resultats = extraire_analyses_cochees(image_test)
        print(f"Examens cochés détectés : {resultats}")
    else:
        print("Image de test introuvable.")