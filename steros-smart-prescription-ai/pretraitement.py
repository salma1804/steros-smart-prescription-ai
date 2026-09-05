import cv2
import numpy as np


def convertir_niveaux_de_gris(image):
    """Convertit l'image en niveaux de gris (nécessaire pour la plupart des traitements OCR)."""
    return cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)


def reduire_bruit(image_grise):
    """Réduit le bruit tout en préservant les contours du texte."""
    return cv2.fastNlMeansDenoising(image_grise, h=10)


def ameliorer_contraste(image_grise):
    """Améliore le contraste localement (CLAHE)."""
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
    return clahe.apply(image_grise)


def accentuer_nettete(image_grise):
    """Applique un filtre de netteté (unsharp mask) pour accentuer les contours du texte."""
    flou = cv2.GaussianBlur(image_grise, (0, 0), sigmaX=3)
    nette = cv2.addWeighted(image_grise, 1.5, flou, -0.5, 0)
    return nette


def binariser(image_grise):
    """Convertit en noir et blanc pur (binarisation adaptative)."""
    return cv2.adaptiveThreshold(
        image_grise, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
        cv2.THRESH_BINARY, blockSize=31, C=15,
    )


def corriger_orientation(image_grise):
    """Détecte et corrige une rotation légère du document."""
    contours = cv2.Canny(image_grise, 50, 150)
    lignes = cv2.HoughLinesP(contours, 1, np.pi / 180, threshold=100, minLineLength=100, maxLineGap=10)

    if lignes is None:
        return image_grise

    lignes = lignes.reshape(-1, 4)
    angles = []
    for x1, y1, x2, y2 in lignes:
        angle = np.degrees(np.arctan2(y2 - y1, x2 - x1))
        angles.append(angle)

    angle_median = np.median(angles)

    if abs(angle_median) < 0.5 or abs(angle_median) > 45:
        return image_grise

    (h, w) = image_grise.shape[:2]
    centre = (w // 2, h // 2)
    matrice_rotation = cv2.getRotationMatrix2D(centre, angle_median, 1.0)
    image_corrigee = cv2.warpAffine(
        image_grise, matrice_rotation, (w, h), flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_REPLICATE
    )
    return image_corrigee


def supprimer_lignes_tableau(image_grise):
    """Détecte et supprime les lignes horizontales/verticales d'un tableau."""
    noyau_horizontal = cv2.getStructuringElement(cv2.MORPH_RECT, (25, 1))
    lignes_h = cv2.morphologyEx(image_grise, cv2.MORPH_OPEN, noyau_horizontal, iterations=2)

    noyau_vertical = cv2.getStructuringElement(cv2.MORPH_RECT, (1, 25))
    lignes_v = cv2.morphologyEx(image_grise, cv2.MORPH_OPEN, noyau_vertical, iterations=2)

    lignes = cv2.add(lignes_h, lignes_v)
    resultat = cv2.subtract(255 - image_grise, lignes)
    return 255 - resultat


def redimensionner_pour_ocr(image, facteur=3):
    """Agrandit l'image pour améliorer la précision de l'OCR."""
    hauteur, largeur = image.shape[:2]
    return cv2.resize(image, (largeur * facteur, hauteur * facteur), interpolation=cv2.INTER_CUBIC)


def pretraiter_image(image, supprimer_tableau=False, redimensionner=True):
    """
    Enchaîne toutes les étapes de prétraitement dans l'ordre.

    Args:
        image: image d'entrée (BGR, couleur)
        supprimer_tableau: si True, supprime les lignes de tableau (pour zone_analyses en tableau)
        redimensionner: si True (par défaut), agrandit l'image avant traitement
    """
    if redimensionner:
        image = redimensionner_pour_ocr(image, facteur=3)

    grise = convertir_niveaux_de_gris(image)
    orientee = corriger_orientation(grise)
    debruitee = reduire_bruit(orientee)
    contrastee = ameliorer_contraste(debruitee)
    nette = accentuer_nettete(contrastee)
    binaire = binariser(nette)

    if supprimer_tableau:
        binaire = supprimer_lignes_tableau(binaire)

    return binaire