import cv2
from ocr_manuscrit import extraire_texte_manuscrit
from ocr_ppocrv6 import extraire_texte_ppocrv6


def comparer_sur_image(chemin_image):
    image = cv2.imread(chemin_image)
    if image is None:
        print(f"Impossible de charger {chemin_image}")
        return

    print(f"===== Comparaison sur {chemin_image} =====\n")

    # --- TrOCR (français) ---
    print("----- TrOCR (français) -----")
    texte_trocr = extraire_texte_manuscrit(image)
    print(f"Texte : {texte_trocr}\n")

    # --- PP-OCRv6 ---
    print("----- PP-OCRv6 -----")
    texte_ppocr, confiance_ppocr = extraire_texte_ppocrv6(image)
    print(f"Texte : {texte_ppocr}")
    print(f"Confiance moyenne : {confiance_ppocr:.1f}%\n")


if __name__ == "__main__":
    chemin_test = r"C:\Users\User\Desktop\steros-smart-prescription-ai\test\ordonnanceManiscrit.jpg"  # adapte avec le chemin réel
    comparer_sur_image(chemin_test)