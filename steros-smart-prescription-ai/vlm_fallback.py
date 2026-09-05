from transformers import AutoModelForCausalLM, AutoTokenizer
import torch

NOM_MODELE = "vikhyatk/moondream2"

print("Chargement de Moondream2 (VLM local, sur CPU pour économiser la VRAM)...")
tokenizer = AutoTokenizer.from_pretrained(NOM_MODELE, trust_remote_code=True)
modele_vlm = AutoModelForCausalLM.from_pretrained(
    NOM_MODELE, trust_remote_code=True, torch_dtype=torch.float32
).to("cpu")
print("Moondream2 chargé (CPU).")


def demander_au_vlm(image_pil, question):
    encodage_image = modele_vlm.encode_image(image_pil)
    reponse = modele_vlm.answer_question(encodage_image, question, tokenizer)
    return reponse


def extraire_tout_via_vlm(image_pil):
    """
    Extrait TOUS les champs principaux via le VLM, indépendamment du pipeline OCR.
    Utile pour une vue comparative (ex. bouton dédié côté frontend).
    """
    questions = {
        "zone_patient": "What is the patient's full name written on this medical document? Answer with just the name.",
        "zone_date": "What is the date written on this medical prescription? Answer with just the date.",
        "zone_prescripteur": "What is the name of the doctor who wrote this prescription? Answer with just the name.",
    }

    resultats_vlm = {}
    for nom_champ, question in questions.items():
        reponse = demander_au_vlm(image_pil, question)
        resultats_vlm[nom_champ] = reponse

    return resultats_vlm

#hethy vlm ijewbna a la demande mch dima 

def obtenir_vue_alternative_vlm(chemin_image):
    """
    Calcule la vue alternative complète via VLM, à appeler SEULEMENT si l'utilisateur
    clique sur le bouton dédié côté frontend — pas automatiquement à chaque traitement.
    """
    image_complete = cv2.imread(chemin_image)
    if image_complete is None:
        return {"erreur": f"Impossible de charger l'image {chemin_image}"}

    image_pil_complete = Image.fromarray(cv2.cvtColor(image_complete, cv2.COLOR_BGR2RGB))
    return extraire_tout_via_vlm(image_pil_complete)    


if __name__ == "__main__":
    from PIL import Image
    image_test = Image.open("test/ordonnanceTestAvecTab.jpg")
    reponse = demander_au_vlm(image_test, "What is the patient's name on this document?")
    print(f"Réponse VLM : {reponse}")