# STEROS Smart Prescription AI

Module intelligent de digitalisation d'ordonnances médicales — détection automatique des zones d'intérêt, extraction de texte par OCR multi-moteurs, et correspondance sémantique avec le catalogue d'examens de laboratoire.

Projet de Fin d'Année (PFA) réalisé dans le cadre d'un stage chez **Steros Technologies**.

---

## Sommaire

- [Aperçu](#aperçu)
- [Architecture](#architecture)
- [Fonctionnalités](#fonctionnalités)
- [Stack technique](#stack-technique)
- [Structure du projet](#structure-du-projet)
- [Installation](#installation)
- [Utilisation](#utilisation)
- [Résultats et performances](#résultats-et-performances)
- [Limites connues](#limites-connues)
- [Pistes d'amélioration](#pistes-damélioration)

---

## Aperçu

Ce projet vise à automatiser la saisie d'ordonnances médicales papier dans le système d'information de laboratoire Steros Lab. Une secrétaire scanne ou photographie une ordonnance ; le système :

1. **Détecte** les zones d'intérêt sur l'image (patient, prescripteur, cachet, date, analyses demandées)
2. **Extrait** le texte de chaque zone via OCR
3. **Identifie** les examens demandés en les faisant correspondre au catalogue officiel du laboratoire
4. **Présente** les résultats dans une interface web pour validation/correction humaine avant import

Le contrôle humain systématique est un principe central de l'architecture : le système **propose**, la secrétaire **valide**.

---

## Architecture

```
┌─────────────┐      ┌──────────────┐      ┌─────────────────────┐
│   Next.js    │─────▶│   FastAPI    │─────▶│  Pipeline Python     │
│  (Frontend)  │◀─────│   (API)      │◀─────│  YOLO26 + OCR + NLP  │
└─────────────┘      └──────────────┘      └─────────────────────┘
```

- **Frontend** : Next.js (React, TypeScript, App Router, Tailwind CSS)
- **Backend** : FastAPI, exposant le pipeline via une route HTTP
- **Détection de zones** : YOLO26 (Ultralytics), 5 classes annotées
- **OCR** : Tesseract, EasyOCR, PP-OCRv6 — comparaison systématique, meilleur résultat retenu
- **NLP** : correspondance exacte + floue contrôlée contre le catalogue officiel Steros Lab

---

## Fonctionnalités

- Import d'ordonnance par clic ou glisser-déposer, avec aperçu immédiat
- Détection automatique de 5 zones : patient, prescripteur, cachet, date, analyses
- OCR robuste combinant 3 moteurs, avec sélection du meilleur résultat par filtre de cohérence
- Correspondance automatique des examens détectés avec le catalogue officiel (1098 examens, 1434 synonymes)
- Interface de validation avec modification des champs, ajout/suppression d'examens (avec autocomplétion)
- Badges de statut par examen (Fiable / À vérifier / Ajouté manuellement)
- Export JSON des données validées
- Historique des ordonnances traitées (persistant navigateur)
- Tableau de bord d'indicateurs (taux de reconnaissance, temps de traitement, corrections manuelles)

---

## Stack technique

| Domaine | Technologies |
|---|---|
| Détection d'objets | YOLO26 (Ultralytics), Label Studio (annotation) |
| OCR | Tesseract (modèle `best`), EasyOCR, PaddleOCR (PP-OCRv6) |
| Traitement d'image | OpenCV (prétraitement, correction de rotation, débruitage, binarisation) |
| NLP | RapidFuzz (similarité textuelle), correspondance exacte normalisée |
| Backend | FastAPI, Uvicorn |
| Frontend | Next.js 15+, React, TypeScript, Tailwind CSS, Lucide Icons |

---

## Structure du projet

```
steros-smart-prescription-ai/
├── pipeline_complet.py          # Orchestrateur principal (détection + OCR + NLP)
├── api.py                       # API FastAPI exposant le pipeline
│
├── acquisition.py                # Chargement des images
├── pretraitement.py             # Prétraitement d'image (rotation, contraste, netteté...)
├── ocr_extraction.py            # Extraction Tesseract avec score de confiance
├── ocr_easyocr.py               # Extraction EasyOCR
├── ocr_ppocrv6.py                # Extraction PP-OCRv6
│
├── moteur_nlp.py                 # Moteur de correspondance sémantique
├── catalogue_officiel.py        # Catalogue d'examens généré (parsé depuis le SQL fourni)
├── parser_catalogue.py          # Script de parsing du catalogue SQL brut
├── lacunes_catalogue.md         # Suivi des abréviations manquantes du catalogue
│
├── entrainer_yolo.py             # Script d'entraînement YOLO26
├── data_v4.yaml                  # Configuration d'entraînement finale
├── dataset_zones_v4/              # Dataset annoté (images + labels)
├── runs_entrainement/            # Poids des modèles entraînés
│
└── steros-frontend/
    └── app/
        ├── page.tsx                    # Page principale (import + résultats)
        ├── historique/page.tsx         # Historique des ordonnances
        ├── tableau-de-bord/page.tsx    # Indicateurs de performance
        ├── components/
        │   ├── Sidebar.tsx
        │   ├── ZoneImport.tsx
        │   ├── ColonneOrdonnance.tsx
        │   ├── ColonneResultats.tsx
        │   └── EtapesWorkflow.tsx
        └── lib/
            ├── api.ts               # Client API
            └── historique.ts        # Persistance locale
```

---

## Installation

### Prérequis
- Python 3.11+
- Node.js 18+
- Tesseract OCR installé sur le système, avec le modèle linguistique français **"best"**
  ([tessdata_best](https://github.com/tesseract-ocr/tessdata_best))

### Backend

```bash
python -m venv venv
venv\Scripts\activate          # Windows
# source venv/bin/activate     # Linux/Mac

pip install -r requirements.txt
```

Principales dépendances : `ultralytics`, `opencv-python`, `pytesseract`, `easyocr`, `paddleocr`, `paddlepaddle`, `rapidfuzz`, `fastapi`, `uvicorn`.

### Frontend

```bash
cd steros-frontend
npm install
```

---

## Utilisation

### Lancer l'API backend

```bash
python -m uvicorn api:app --reload --port 8001
```

L'API expose une route `POST /traiter-ordonnance` (upload d'image, réponse JSON structurée), documentée automatiquement sur `http://localhost:8001/docs`.

### Lancer le frontend

```bash
cd steros-frontend
npm run dev
```

Interface accessible sur `http://localhost:3000`.

### Utiliser le pipeline en ligne de commande

```bash
python pipeline_complet.py
```

*(adapter le chemin de l'image de test dans le bloc `if __name__ == "__main__":`)*

---

## Résultats et performances

### Détection de zones (YOLO26)

| Version | Images annotées | mAP50 global |
|---|---|---|
| v1 | 307 | 0.562 |
| v2 | 433 | 0.531 |
| v3 | 594 | 0.591 |
| **v4 (finale)** | **703** | **0.605** |

Détail par classe (v4) : zone_analyses = 0.856, zone_patient = 0.655, zone_prescripteur = 0.521, zone_cachet = 0.532, zone_date = 0.461.

### OCR — comparaison des moteurs testés

| Moteur | Statut |
|---|---|
| Tesseract "best" | ✅ Adopté (+3.7 pts vs standard) |
| EasyOCR | ✅ Adopté |
| PP-OCRv6 (PaddleOCR) | ✅ Adopté (remplace TrOCR sur manuscrit) |
| TrOCR | ❌ Retiré (hallucinations sur manuscrit médical) |
| VLM local (Moondream2) | ❌ Retiré (trop lent sur CPU, VRAM insuffisante pour GPU) |
| DTrOCR | ❌ Écarté (aucun poids pré-entraîné public disponible) |

### Mesure globale (échantillon de test)

- Taux de détection de `zone_analyses` : **60%**
- Taux de reconnaissance des examens, conditionnel à la détection : **75%**
- Sur les formats imprimés/structurés : jusqu'à **100%** de reconnaissance correcte
- Sur l'écriture manuscrite cursive dense : performance significativement plus faible (limite documentée)

---

## Limites connues

- **Écriture manuscrite cursive dense** : reste la limite principale du système, malgré la comparaison de 3 moteurs OCR.
- **Détection de zones sur formats atypiques** : certains formats à mise en page multi-blocs (ex. formulaires "cabinet privé") restent mal couverts par le modèle actuel.
- **Détection de cases à cocher** : une approche géométrique a été testée puis abandonnée (taux de faux positifs trop élevé sur écriture manuscrite dense).
- **Correspondance NLP sur abréviations courtes** : les algorithmes de similarité approximative (distance d'édition, similarité floue étendue) ont montré un taux de faux positifs supérieur au gain sur du texte fortement bruité ; la stratégie retenue privilégie la précision (correspondance exacte + dictionnaire manuel contrôlé).
- **Lacunes du catalogue officiel** : certaines abréviations médicales courantes sont absentes du référentiel fourni (voir `lacunes_catalogue.md`).

---

## Pistes d'amélioration

- Lot d'annotation ciblé sur les formats à mise en page multi-blocs
- Modèle de détection dédié pour les cases à cocher (entraîné sur des paires case/libellé)
- VLM local en secours, sous réserve d'un GPU disposant d'au moins 8 Go de VRAM dédiés, ou d'une quantification 4-bit du modèle
- Enrichissement continu du catalogue officiel avec les abréviations manquantes identifiées en production
- Parallélisation des appels OCR (multi-threading) pour réduire le temps de traitement par ordonnance

---

## Auteure

Projet réalisé par **Salma**, étudiante en ingénierie logicielle à l'ENIS (École Nationale d'Ingénieurs de Sfax), dans le cadre d'un stage chez Steros Technologies.
