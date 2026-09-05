from rapidfuzz import fuzz, process
from catalogue_officiel import CATALOGUE_EXAMENS, REFERENTIEL_SYNONYMES
import re
import unicodedata

SEUIL_SIMILARITE_MINIMUM = 90

TOUS_LES_LIBELLES = [examen["libelle"] for examen in CATALOGUE_EXAMENS]


def normaliser(texte):
    texte = texte.strip().upper()
    texte_sans_accents = unicodedata.normalize('NFD', texte)
    texte_sans_accents = ''.join(c for c in texte_sans_accents if unicodedata.category(c) != 'Mn')
    return texte_sans_accents


REFERENTIEL_NORMALISE = {
    normaliser(abreviation): designation
    for abreviation, designation in REFERENTIEL_SYNONYMES.items()
}
for examen in CATALOGUE_EXAMENS:
    cle = normaliser(examen["libelle"])
    if cle not in REFERENTIEL_NORMALISE:
        REFERENTIEL_NORMALISE[cle] = examen["libelle"]

SYNONYMES_SUPPLEMENTAIRES = {
    "CREAT": "CREATININE",
    "CREA": "CREATININE",
    "TROPO": "TROPONINE T hs",
    "IOWO": "IONOGRAMME SANGUIN",
    "EBU": "SERO. DES INFECTIONS A VIRUS D\u2018EPSTEIN ET BARR",
}

REFERENTIEL_NORMALISE.update({
    normaliser(k): v for k, v in SYNONYMES_SUPPLEMENTAIRES.items()
})


def chercher_correspondance_exacte(texte):
    return REFERENTIEL_NORMALISE.get(normaliser(texte))


def chercher_correspondance_floue(mot):
    if not TOUS_LES_LIBELLES or len(mot) < 6:
        return None, 0
    meilleur_match = process.extractOne(mot, TOUS_LES_LIBELLES, scorer=fuzz.WRatio)
    if meilleur_match is None:
        return None, 0
    libelle_trouve, score = meilleur_match[0], meilleur_match[1]
    ratio_longueur = len(mot) / len(libelle_trouve)
    if ratio_longueur < 0.5:
        return None, 0
    return libelle_trouve, score


def faire_correspondre_examen(texte, autoriser_flou=True):
    texte = texte.strip()
    if texte == "":
        return {"texte_detecte": texte, "libelle_trouve": None, "score_confiance": 0,
                "methode": "aucune", "statut": "NonReconnu"}
    correspondance_exacte = chercher_correspondance_exacte(texte)
    if correspondance_exacte:
        statut = "Incertain" if len(texte) < 3 else "Reconnu"
        return {"texte_detecte": texte, "libelle_trouve": correspondance_exacte, "score_confiance": 100,
                "methode": "synonyme_exact", "statut": statut}
    if not autoriser_flou:
        return {"texte_detecte": texte, "libelle_trouve": None, "score_confiance": 0,
                "methode": "aucune", "statut": "NonReconnu"}
    libelle_flou, score = chercher_correspondance_floue(texte)
    if score >= SEUIL_SIMILARITE_MINIMUM:
        return {"texte_detecte": texte, "libelle_trouve": libelle_flou, "score_confiance": score,
                "methode": "similarite_floue", "statut": "Reconnu"}
    return {"texte_detecte": texte, "libelle_trouve": None, "score_confiance": score,
            "methode": "aucune", "statut": "NonReconnu"}


def fusionner_fragments_courts(mots, longueur_max_fragment=2):
    mots_enrichis = list(mots)
    for i in range(len(mots) - 1):
        if len(mots[i]) <= longueur_max_fragment or len(mots[i + 1]) <= longueur_max_fragment:
            fusion = mots[i] + mots[i + 1]
            if len(fusion) <= 6:
                mots_enrichis.append(fusion)
    return mots_enrichis


def analyser_texte_complet(texte_brut, taille_max_groupe=3):
    mots = re.split(r"[\s\-\u2013\u2014|,;\.]+", texte_brut)
    mots = [m.strip(".,;:()[]{}\"\'") for m in mots]
    mots = [m for m in mots if len(m) >= 2]
    mots = fusionner_fragments_courts(mots)

    resultats = []
    index_traites = set()

    i = 0
    while i < len(mots):
        if i in index_traites:
            i += 1
            continue
        trouve = False
        for taille_groupe in range(min(taille_max_groupe, len(mots) - i), 1, -1):
            groupe = " ".join(mots[i:i + taille_groupe])
            resultat = faire_correspondre_examen(groupe, autoriser_flou=False)
            if resultat["statut"] == "Reconnu":
                resultats.append(resultat)
                for j in range(i, i + taille_groupe):
                    index_traites.add(j)
                i += taille_groupe
                trouve = True
                break
        if not trouve:
            i += 1

    for i, mot in enumerate(mots):
        if i in index_traites:
            continue
        resultat = faire_correspondre_examen(mot, autoriser_flou=True)
        if resultat["statut"] != "NonReconnu":
            resultats.append(resultat)

    meilleurs_par_libelle = {}
    for r in resultats:
        cle = r["libelle_trouve"]
        if cle not in meilleurs_par_libelle or r["score_confiance"] > meilleurs_par_libelle[cle]["score_confiance"]:
            meilleurs_par_libelle[cle] = r

    return list(meilleurs_par_libelle.values())


if __name__ == "__main__":
    print(f"Catalogue charge : {len(CATALOGUE_EXAMENS)} examens, {len(REFERENTIEL_SYNONYMES)} synonymes")
    texte_exemple = "NFS creat Tropo uu sm Subhe EB U"
    for r in analyser_texte_complet(texte_exemple):
        print(r["texte_detecte"], "->", r["libelle_trouve"], r["statut"], r["score_confiance"], r["methode"])
