import cv2
import json
import os
import numpy as np

coordonnees_capturees = []
image_affichage = None
facteur_echelle = 1.0


# mch nkhdmo bl technique orb : mch ncalibriw tswira ta test al tswira l repere li khtarneha orb yatini les pnt cle :kima ktiba kbira wala carre w bad ikis l transation w rotation w yapplikihm 


def on_click(event, x, y, flags, param):
    global coordonnees_capturees, image_affichage, facteur_echelle
    if event == cv2.EVENT_LBUTTONDOWN:
        x_reel = int(x / facteur_echelle)
        y_reel = int(y / facteur_echelle)

        libelle = input(f"Libellé pour la case à ({x_reel},{y_reel}) : ")
        if libelle.strip() == "":
            print("Libellé vide, case ignorée.")
            return
        coordonnees_capturees.append({"x": x_reel, "y": y_reel, "libelle": libelle})
        cv2.circle(image_affichage, (x, y), 5, (0, 255, 0), -1)
        cv2.imshow("Calibration", image_affichage)


def calibrer_template(chemin_image, nom_template, hauteur_max_ecran=850):
    global image_affichage, coordonnees_capturees, facteur_echelle

    chemin_json = f"templates/{nom_template}.json"
    if os.path.exists(chemin_json):
        with open(chemin_json, "r", encoding="utf-8") as f:
            coordonnees_capturees = json.load(f)
        print(f"{len(coordonnees_capturees)} cases déjà enregistrées, chargées.")
    else:
        coordonnees_capturees = []

    image_originale = cv2.imread(chemin_image)
    if image_originale is None:
        print(f"Impossible de charger {chemin_image}")
        return

    hauteur_originale = image_originale.shape[0]
    facteur_echelle = min(1.0, hauteur_max_ecran / hauteur_originale)

    nouvelle_largeur = int(image_originale.shape[1] * facteur_echelle)
    nouvelle_hauteur = int(image_originale.shape[0] * facteur_echelle)

    image_affichage = cv2.resize(image_originale, (nouvelle_largeur, nouvelle_hauteur))

    for case in coordonnees_capturees:
        x_affiche = int(case["x"] * facteur_echelle)
        y_affiche = int(case["y"] * facteur_echelle)
        cv2.circle(image_affichage, (x_affiche, y_affiche), 5, (0, 255, 0), -1)

    cv2.namedWindow("Calibration", cv2.WINDOW_NORMAL)
    cv2.imshow("Calibration", image_affichage)
    cv2.setMouseCallback("Calibration", on_click)

    print(f"Image affichée à {facteur_echelle*100:.0f}% de sa taille réelle.")
    print("Clique sur chaque NOUVELLE case, tape le libellé exact dans le terminal après chaque clic.")
    print("Une fois terminé, clique sur la fenêtre image et appuie sur 'q'.")

    while True:
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cv2.destroyAllWindows()

    os.makedirs("templates", exist_ok=True)
    with open(chemin_json, "w", encoding="utf-8") as f:
        json.dump(coordonnees_capturees, f, ensure_ascii=False, indent=2)

    print(f"\n{len(coordonnees_capturees)} cases enregistrées au total dans {chemin_json}")


def charger_template(nom_template):
    with open(f"templates/{nom_template}.json", "r", encoding="utf-8") as f:
        return json.load(f)
    

#taille — contrôle la GRANDEUR de la zone examinée
#C'est la distance (en pixels) qu'on regarde autour du point calibré (x, y), dans les 4 directions (haut, bas, gauche, droite).  
# 
# seuil — contrôle À PARTIR DE QUAND on considère que c'est "rempli"  


def case_est_cochee_a_position(image_grise, x, y, taille=15, seuil=0.10):
    y1, y2 = max(0, y - taille), y + taille
    x1, x2 = max(0, x - taille), x + taille
    region = image_grise[y1:y2, x1:x2]

    if region.size == 0:
        return False

    _, binaire = cv2.threshold(region, 180, 255, cv2.THRESH_BINARY_INV)
    proportion_sombre = np.sum(binaire > 0) / binaire.size
    return proportion_sombre > seuil


def aligner_image_sur_reference(image_a_aligner, image_reference, seuil_inliers_minimum=15):
    gris_reference = cv2.cvtColor(image_reference, cv2.COLOR_BGR2GRAY)
    gris_a_aligner = cv2.cvtColor(image_a_aligner, cv2.COLOR_BGR2GRAY)

    orb = cv2.ORB_create(nfeatures=2000)

    points_ref, descripteurs_ref = orb.detectAndCompute(gris_reference, None)
    points_new, descripteurs_new = orb.detectAndCompute(gris_a_aligner, None)

    print(f"DEBUG - Points-clés trouvés : référence={len(points_ref)}, nouvelle image={len(points_new)}")

    matcher = cv2.BFMatcher(cv2.NORM_HAMMING, crossCheck=True)
    correspondances = matcher.match(descripteurs_new, descripteurs_ref)
    correspondances = sorted(correspondances, key=lambda x: x.distance)

    nb_bonnes_correspondances = int(len(correspondances) * 0.15)
    bonnes_correspondances = correspondances[:nb_bonnes_correspondances]

    print(f"DEBUG - Correspondances totales : {len(correspondances)}, bonnes gardées : {len(bonnes_correspondances)}")

    if len(bonnes_correspondances) < 10:
        print("DEBUG - Échec : pas assez de bonnes correspondances")
        return None

    points_source = np.float32([points_new[m.queryIdx].pt for m in bonnes_correspondances]).reshape(-1, 1, 2)
    points_destination = np.float32([points_ref[m.trainIdx].pt for m in bonnes_correspondances]).reshape(-1, 1, 2)

    matrice_homographie, mask = cv2.findHomography(points_source, points_destination, cv2.RANSAC, 5.0)

    if matrice_homographie is None:
        print("DEBUG - Échec : homographie non calculable")
        return None

    inliers = int(np.sum(mask)) if mask is not None else 0
    print(f"DEBUG - Inliers RANSAC : {inliers}")

    if inliers < seuil_inliers_minimum:
        print(f"DEBUG - Alignement jugé peu fiable ({inliers} < {seuil_inliers_minimum})")
        return None

    hauteur, largeur = image_reference.shape[:2]
    image_alignee = cv2.warpPerspective(image_a_aligner, matrice_homographie, (largeur, hauteur))

    return image_alignee

def sauvegarder_debug_alignement(image_alignee, template):
    image_debug = image_alignee.copy()
    image_grise = cv2.cvtColor(image_alignee, cv2.COLOR_BGR2GRAY)

    for case in template:
        x, y = case["x"], case["y"]
        est_cochee = case_est_cochee_a_position(image_grise, x, y)
        couleur = (0, 255, 0) if est_cochee else (0, 0, 255)
        cv2.circle(image_debug, (x, y), 6, couleur, 2)

    cv2.imwrite("debug_alignement_template.jpg", image_debug)
    print("Image de debug sauvegardée : debug_alignement_template.jpg")


def extraire_analyses_via_template(image_originale_complete, nom_template, image_reference):
    image_alignee = aligner_image_sur_reference(image_originale_complete, image_reference)

    if image_alignee is None:
        return None

    template = charger_template(nom_template)

    sauvegarder_debug_alignement(image_alignee, template)

    image_grise = cv2.cvtColor(image_alignee, cv2.COLOR_BGR2GRAY)

    examens_coches = []
    for case in template:
        if case_est_cochee_a_position(image_grise, case["x"], case["y"]):
            examens_coches.append(case["libelle"])

    return examens_coches


if __name__ == "__main__":
    image_reference = cv2.imread("test/testordonnance.jpg")
    image_nouvelle = cv2.imread(r'C:\Users\User\Desktop\steros-smart-prescription-ai\test\Autre02_06_2025 06-56-47 .jpg')

    resultats = extraire_analyses_via_template(image_nouvelle, "lam_examens_laboratoire", image_reference)
    print(f"Examens détectés : {resultats}")