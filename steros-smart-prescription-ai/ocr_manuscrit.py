from transformers import TrOCRProcessor, VisionEncoderDecoderModel, AutoTokenizer
from PIL import Image
import cv2

NOM_PROCESSOR = "microsoft/trocr-large-handwritten"  # le processor reste celui de Microsoft
NOM_MODELE_FR = "agomberto/trocr-large-handwritten-fr"  # le modèle, lui, est français

print("Chargement du modèle TrOCR français (peut prendre du temps la première fois)...")
processor = TrOCRProcessor.from_pretrained(NOM_PROCESSOR)
model_trocr = VisionEncoderDecoderModel.from_pretrained(NOM_MODELE_FR)
tokenizer = AutoTokenizer.from_pretrained(NOM_MODELE_FR)
print("Modèle TrOCR français chargé.")


def extraire_texte_manuscrit(image_cv2):
    image_rgb = cv2.cvtColor(image_cv2, cv2.COLOR_BGR2RGB)
    image_pil = Image.fromarray(image_rgb)

    pixel_values = processor(images=image_pil, return_tensors="pt").pixel_values
    ids_generes = model_trocr.generate(pixel_values)
    texte = tokenizer.batch_decode(ids_generes, skip_special_tokens=True)[0]

    return texte


if __name__ == "__main__":
    image_test = cv2.imread("debug_zone_date_original.jpg")
    if image_test is not None:
        resultat = extraire_texte_manuscrit(image_test)
        print(f"Texte manuscrit détecté : {resultat}")