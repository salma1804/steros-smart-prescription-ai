import cv2
import os

def charger_image(chemin_image: str):
    """
    Charge une image depuis un chemin de fichier.
    Retourne l'image sous forme de tableau numpy (format OpenCV), ou None si erreur.
    """
    if not os.path.exists(chemin_image):
        print(f"Erreur : le fichier {chemin_image} n'existe pas.")
        return None

    image = cv2.imread(chemin_image)

    if image is None:
        print(f"Erreur : impossible de lire l'image {chemin_image} (fichier corrompu ou format non supporté).")
        return None

    print(f"Image chargée avec succès : {chemin_image} — dimensions : {image.shape}")
    return image


def lister_ordonnances(dossier: str):
    """
    Liste tous les fichiers image (.jpg, .jpeg) présents dans un dossier.
    """
    extensions_valides = (".jpg", ".jpeg")
    fichiers = [
        os.path.join(dossier, f)
        for f in os.listdir(dossier)
        if f.lower().endswith(extensions_valides)
    ]
    return fichiers


if __name__ == "__main__":
    dossier_ordonnances = "data/ordonnances"
    fichiers = lister_ordonnances(dossier_ordonnances)

    print(f"{len(fichiers)} ordonnance(s) trouvée(s) :")
    for f in fichiers:
        print(" -", f)

    # Test de chargement de la première image trouvée
    if fichiers:
        image_test = charger_image(fichiers[0])