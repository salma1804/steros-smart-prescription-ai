def detecter_format_lam_examens(texte_ocr_complet):
    """
    Détecte si le texte OCR correspond au format LAM 'Examens de Laboratoire'
    (celui avec ~112 cases à cocher), et pas un autre formulaire LAM (FOR-PR-01, etc.)
    """
    texte_minuscule = texte_ocr_complet.lower()

    # Mots-clés distinctifs de CE format précis (pas juste "senda jeribi masmoudi",
    # qui apparaît aussi sur d'autres formulaires LAM différents)
    mots_cles_obligatoires = ["hematologie", "hemostase", "biochimie"]

    return all(mot in texte_minuscule for mot in mots_cles_obligatoires)