import cv2
import pytesseract
from ultralytics import YOLO
from pretraitement import pretraiter_image
from ocr_extraction import extraire_texte_avec_confiance
from ocr_easyocr import extraire_texte_easyocr
from ocr_ppocrv6 import extraire_texte_ppocrv6
from moteur_nlp import analyser_texte_complet
from concurrent.futures import ThreadPoolExecutor

CHEMIN_MODELE = "C:/Users/User/runs/detect/runs_entrainement/zones_ordonnances_v4/weights/best.pt"
NOMS_CLASSES = ["zone_analyses", "zone_cachet", "zone_date", "zone_patient", "zone_prescripteur"]
SEUIL_CONFIANCE_DETECTION = 0.15
SEUIL_CONFIANCE_OCR = 60

PSM_PAR_ZONE = {
    "zone_date": 7,
    "zone_patient": 7,
    "zone_prescripteur": 6,
    "zone_cachet": 6,
    "zone_analyses": 6,
}

ZONES_AVEC_TABLEAU = {"zone_analyses"}

model = YOLO(CHEMIN_MODELE)


def corriger_rotation_90(image):
    try:
        osd = pytesseract.image_to_osd(image)
        lignes = osd.split("\n")

        angle_detecte = int([l for l in lignes if "Rotate" in l][0].split(":")[1].strip())
        confiance_orientation = float([l for l in lignes if "Orientation confidence" in l][0].split(":")[1].strip())

        print(f"DEBUG - Rotation détectée : {angle_detecte}°, confiance : {confiance_orientation}")

        # Si la confiance est trop faible, Tesseract n'est pas sûr — ne rien corriger automatiquement
        if confiance_orientation < 1.0:
            print("DEBUG - Confiance d'orientation trop faible, aucune correction appliquée.")
            return image

    except Exception as e:
        print(f"DEBUG - OSD a échoué : {e}")
        return image

    if angle_detecte == 0:
        return image
    if angle_detecte == 90:
        return cv2.rotate(image, cv2.ROTATE_90_CLOCKWISE)
    elif angle_detecte == 180:
        return cv2.rotate(image, cv2.ROTATE_180)
    elif angle_detecte == 270:
        return cv2.rotate(image, cv2.ROTATE_90_COUNTERCLOCKWISE)
    return image


def calculer_iou(boite1, boite2):
    x1_i, y1_i, x2_i, y2_i = boite1
    x1_j, y1_j, x2_j, y2_j = boite2
    x_gauche, y_haut = max(x1_i, x1_j), max(y1_i, y1_j)
    x_droite, y_bas = min(x2_i, x2_j), min(y2_i, y2_j)
    if x_droite < x_gauche or y_bas < y_haut:
        return 0.0
    aire_intersection = (x_droite - x_gauche) * (y_bas - y_haut)
    aire_boite1 = (x2_i - x1_i) * (y2_i - y1_i)
    aire_boite2 = (x2_j - x1_j) * (y2_j - y1_j)
    return aire_intersection / float(aire_boite1 + aire_boite2 - aire_intersection)


def dedupliquer_zones(zones, seuil_iou=0.7):
    zones_triees = sorted(zones, key=lambda z: z["confiance_detection"], reverse=True)
    zones_gardees = []
    for zone in zones_triees:
        est_doublon = any(
            zone["classe"] == zg["classe"] and calculer_iou(zone["coordonnees"], zg["coordonnees"]) > seuil_iou
            for zg in zones_gardees
        )
        if not est_doublon:
            zones_gardees.append(zone)
    return zones_gardees


def detecter_zones(chemin_image, debug=False):
    resultats = model(chemin_image, verbose=False)[0]
    zones = []
    for box in resultats.boxes:
        confiance = float(box.conf[0])
        if confiance < SEUIL_CONFIANCE_DETECTION:
            continue
        classe_id = int(box.cls[0])
        x1, y1, x2, y2 = map(int, box.xyxy[0].tolist())
        zones.append({
            "classe": NOMS_CLASSES[classe_id],
            "confiance_detection": confiance,
            "coordonnees": (x1, y1, x2, y2),
        })
    zones = dedupliquer_zones(zones)
    if debug:
        print("----- Détections finales -----")
        for z in zones:
            print(f"  {z['classe']} : confiance = {z['confiance_detection']:.2f}")
        print("------------------------------\n")
    return zones


def decouper_zone(image_complete, coordonnees):
    x1, y1, x2, y2 = coordonnees
    return image_complete[y1:y2, x1:x2]


def texte_semble_coherent(texte, nom_classe):
    caracteres_alphanumeriques = sum(1 for c in texte if c.isalnum())
    if caracteres_alphanumeriques < 3:
        return False

    if nom_classe == "zone_date":
        return sum(1 for c in texte if c in "_{}[]<>\\|~^#*") == 0
    elif nom_classe == "zone_patient":
        return sum(1 for c in texte if c in "_{}[]<>\\|~^#*") <= 1
    else:
        return sum(1 for c in texte if c in "_{}[]<>\\|~^") <= 2





def traiter_zone_ocr(image_zone, image_zone_pretraitee, nom_classe):
    with ThreadPoolExecutor(max_workers=3) as executor:
        futur_tesseract = executor.submit(
            extraire_texte_avec_confiance, image_zone_pretraitee, PSM_PAR_ZONE.get(nom_classe, 6)
        )
        futur_easyocr = executor.submit(extraire_texte_easyocr, image_zone)
        futur_ppocr = executor.submit(extraire_texte_ppocrv6, image_zone)

        texte_tesseract, confiance_tesseract = futur_tesseract.result()
        texte_easyocr, confiance_easyocr = futur_easyocr.result()
        texte_ppocr, confiance_ppocr = futur_ppocr.result()

    candidats = [
        (texte_tesseract, confiance_tesseract, "tesseract"),
        (texte_easyocr, confiance_easyocr, "easyocr"),
        (texte_ppocr, confiance_ppocr, "ppocrv6"),
    ]

    candidats_valides = [
        (texte, conf, moteur) for (texte, conf, moteur) in candidats
        if texte.strip() != "" and texte_semble_coherent(texte, nom_classe)
    ]

    if candidats_valides:
        texte_principal, confiance_principale, moteur_principal = max(candidats_valides, key=lambda c: c[1])
    else:
        texte_principal, confiance_principale, moteur_principal = max(candidats, key=lambda c: c[1])

    return {
        "texte_principal": texte_principal,
        "confiance_principale": confiance_principale,
        "moteur_principal": moteur_principal,
    }

def fusionner_candidats_analyses(image_zone, image_zone_pretraitee, nom_classe):
    texte_tesseract, confiance_tesseract = extraire_texte_avec_confiance(
        image_zone_pretraitee, psm=PSM_PAR_ZONE.get(nom_classe, 6)
    )
    texte_easyocr, confiance_easyocr = extraire_texte_easyocr(image_zone)
    texte_ppocr, confiance_ppocr = extraire_texte_ppocrv6(image_zone)

    print(f"DEBUG zone_analyses - Tesseract : '{texte_tesseract}' ({confiance_tesseract:.1f}%)")
    print(f"DEBUG zone_analyses - EasyOCR : '{texte_easyocr}' ({confiance_easyocr:.1f}%)")
    print(f"DEBUG zone_analyses - PPOCR : '{texte_ppocr}' ({confiance_ppocr:.1f}%)")

    texte_combine = f"{texte_tesseract} {texte_easyocr} {texte_ppocr}"
    return texte_combine, max(confiance_tesseract, confiance_easyocr, confiance_ppocr)


def traiter_ordonnance(chemin_image):
    """
    Pipeline complet : détection de zones (YOLO26)
    -> pour zone_analyses : fusion des mots de 3 moteurs OCR (le NLP triera)
    -> pour les autres zones : sélection du meilleur moteur cohérent
    -> analyse NLP (correspondance au catalogue Steros Lab).

    Note : le template matching pour le format LAM a été retiré (demande encadreur,
    non nécessaire et ralentissait l'exécution). Toutes les analyses passent désormais
    systématiquement par le moteur NLP.
    """
    image_complete = cv2.imread(chemin_image)
    if image_complete is None:
        return {"erreur": f"Impossible de charger l'image {chemin_image}"}

    image_complete = corriger_rotation_90(image_complete)

    zones_detectees = detecter_zones(chemin_image, debug=True)
    resultats_par_zone = {}

    for zone in zones_detectees:
        nom_classe = zone["classe"]
        image_zone = decouper_zone(image_complete, zone["coordonnees"])

        if image_zone.size == 0:
            continue

        supprimer_tableau = nom_classe in ZONES_AVEC_TABLEAU
        image_zone_pretraitee = pretraiter_image(image_zone, supprimer_tableau=supprimer_tableau)

        if nom_classe == "zone_analyses":
            # DEBUG : sauvegarde l'image découpée pour vérifier visuellement le placement du rectangle
            cv2.imwrite("debug_zone_analyses_actuelle.jpg", image_zone)

            texte_principal, confiance_principale = fusionner_candidats_analyses(
                image_zone, image_zone_pretraitee, nom_classe
            )
            moteur_principal = "fusion_multi_moteurs"
        else:
            resultat_ocr = traiter_zone_ocr(image_zone, image_zone_pretraitee, nom_classe)
            texte_principal = resultat_ocr["texte_principal"]
            confiance_principale = resultat_ocr["confiance_principale"]
            moteur_principal = resultat_ocr["moteur_principal"]

        if texte_principal.strip() == "":
            continue

        statut = "fiable" if confiance_principale >= SEUIL_CONFIANCE_OCR else "a_verifier"

        resultat_detection = {
            "texte": texte_principal,
            "moteur_principal": moteur_principal,
            "statut": statut,
        }

        if nom_classe not in resultats_par_zone:
            resultats_par_zone[nom_classe] = resultat_detection
        else:
            resultats_par_zone[nom_classe]["texte"] += " | " + texte_principal

    # --- NLP : toujours appliqué sur zone_analyses ---
    if "zone_analyses" in resultats_par_zone:
        texte_analyses = resultats_par_zone["zone_analyses"]["texte"]
        resultats_par_zone["zone_analyses"]["examens_identifies"] = analyser_texte_complet(texte_analyses)
        resultats_par_zone["zone_analyses"]["methode_analyses"] = "nlp"

    return resultats_par_zone


if __name__ == "__main__":
    chemin_test = r"C:\Users\User\Desktop\steros-smart-prescription-ai\data\nv_echantillon_annotation\Autre04_06_2025 15-00-10 .jpg"
    resultats = traiter_ordonnance(chemin_test)

    print(f"\n===== RÉSULTATS pour {chemin_test} =====\n")
    for nom_classe in NOMS_CLASSES:
        if nom_classe in resultats:
            infos = resultats[nom_classe]
            print(f"[{nom_classe}]")
            print(f"  Texte : {infos.get('texte')}")
            print(f"  Moteur : {infos.get('moteur_principal')}")
            print(f"  Statut : {infos.get('statut')}")
            if "examens_identifies" in infos:
                print(f"  Méthode analyses : {infos.get('methode_analyses')}")
                print(f"  Examens identifiés :")
                for ex in infos["examens_identifies"]:
                    if isinstance(ex, dict):
                        print(f"    - {ex.get('libelle_trouve')} (statut: {ex.get('statut')})")
                    else:
                        print(f"    - {ex}")
        else:
            print(f"[{nom_classe}] NON DÉTECTÉE")
        print()