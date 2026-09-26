from ion import *
from kandinsky import *
from time import sleep


# ============================================================
# BaseConv
# Convertisseur BIN / OCT / DEC / HEX pour calculatrice NumWorks
# ============================================================
#
# Architecture :
#   - Un seul point d'entree pour la lecture clavier (lire_touche)
#   - Un moteur d'ecran generique (boucle_ecran) qui factorise le
#     pattern "afficher -> lire touche -> reagir -> reafficher si
#     besoin", commun a tous les ecrans du programme.
#   - Chaque ecran est une paire (fonction d'affichage, fonction
#     de gestion de touche qui renvoie soit None pour rester sur
#     l'ecran, soit une valeur de sortie pour le quitter).
# ------------------------------------------------------------

BASES = (2, 8, 10, 16)

NOMS_BASES = {
    2: "BIN",
    8: "OCT",
    10: "DEC",
    16: "HEX"
}

LONGUEUR_MAX_SAISIE = 40
TAILLE_HISTORIQUE = 5


# ------------------------------------------------------------
# Ecran & couleurs
# ------------------------------------------------------------

LARGEUR_ECRAN = 320
HAUTEUR_ECRAN = 222
MARGE = 10

BLANC = (255, 255, 255)
NOIR = (0, 0, 0)
GRIS = (120, 120, 120)
GRIS_CLAIR = (200, 200, 200)
BLEU = (40, 90, 180)
BLEU_CLAIR = (220, 230, 250)
ROUGE = (200, 50, 50)
ROUGE_CLAIR = (250, 225, 225)


# ------------------------------------------------------------
# Touches
# ------------------------------------------------------------

CHIFFRES = {
    KEY_ZERO: "0", KEY_ONE: "1", KEY_TWO: "2", KEY_THREE: "3",
    KEY_FOUR: "4", KEY_FIVE: "5", KEY_SIX: "6", KEY_SEVEN: "7",
    KEY_EIGHT: "8", KEY_NINE: "9"
}

LETTRES_HEX = {
    KEY_EXP: "A", KEY_LN: "B", KEY_LOG: "C",
    KEY_IMAGINARY: "D", KEY_COMMA: "E", KEY_POWER: "F"
}

TOUCHES = [
    KEY_LEFT, KEY_UP, KEY_DOWN, KEY_RIGHT,
    KEY_OK, KEY_EXE, KEY_VAR, KEY_BACKSPACE,
    KEY_ALPHA, KEY_MINUS
] + list(CHIFFRES) + list(LETTRES_HEX)


def toutes_relachees():
    for touche in TOUCHES:
        if keydown(touche):
            return False
    return True


def lire_touche():
    """Attend le relachement de toute touche, puis bloque jusqu'a
    la prochaine pression et la renvoie (apres son relachement)."""
    while not toutes_relachees():
        sleep(0.01)

    while True:
        for touche in TOUCHES:
            if keydown(touche):
                while keydown(touche):
                    sleep(0.01)
                return touche
        sleep(0.01)


# ------------------------------------------------------------
# Primitives d'affichage
# ------------------------------------------------------------

def effacer():
    fill_rect(0, 0, LARGEUR_ECRAN, HAUTEUR_ECRAN, BLANC)


def texte(x, y, contenu, couleur=NOIR, fond=BLANC):
    draw_string(contenu, x, y, couleur, fond)


def ligne(x, y, largeur, couleur=GRIS):
    fill_rect(x, y, largeur, 1, couleur)


def entete(titre="BaseConv"):
    texte(MARGE, 8, titre, BLEU)
    ligne(MARGE, 28, LARGEUR_ECRAN - 2 * MARGE)


def pied_de_page(y, texte_aide):
    ligne(MARGE, y, LARGEUR_ECRAN - 2 * MARGE)
    texte(MARGE, y + 10, texte_aide, GRIS)


def fleche_gauche(x, y, couleur=NOIR):
    fill_rect(x + 4, y, 4, 2, couleur)
    fill_rect(x + 2, y + 2, 4, 2, couleur)
    fill_rect(x, y + 4, 14, 2, couleur)
    fill_rect(x + 2, y + 6, 4, 2, couleur)
    fill_rect(x + 4, y + 8, 4, 2, couleur)


def fleche_droite(x, y, couleur=NOIR):
    fill_rect(x + 6, y, 4, 2, couleur)
    fill_rect(x + 8, y + 2, 4, 2, couleur)
    fill_rect(x, y + 4, 14, 2, couleur)
    fill_rect(x + 8, y + 6, 4, 2, couleur)
    fill_rect(x + 6, y + 8, 4, 2, couleur)


def fleche_haut(x, y, couleur=NOIR):
    fill_rect(x + 4, y, 6, 2, couleur)
    fill_rect(x + 2, y + 2, 10, 2, couleur)
    fill_rect(x, y + 4, 14, 2, couleur)
    fill_rect(x + 6, y + 6, 2, 6, couleur)


def fleche_bas(x, y, couleur=NOIR):
    fill_rect(x + 6, y, 2, 6, couleur)
    fill_rect(x, y + 6, 14, 2, couleur)
    fill_rect(x + 2, y + 8, 10, 2, couleur)
    fill_rect(x + 4, y + 10, 6, 2, couleur)


def fleches_horizontal(x, y, actif_gauche=True, actif_droite=True):
    fleche_gauche(x, y, NOIR if actif_gauche else GRIS_CLAIR)
    fleche_droite(x + 24, y, NOIR if actif_droite else GRIS_CLAIR)


def fleches_vertical(x, y, actif_haut=True, actif_bas=True):
    fleche_haut(x, y, NOIR if actif_haut else GRIS_CLAIR)
    fleche_bas(x, y + 18, NOIR if actif_bas else GRIS_CLAIR)


# ------------------------------------------------------------
# Moteur d'ecran generique
# ------------------------------------------------------------

def boucle_ecran(etat, afficher, gerer_touche):
    """
    Fait vivre un ecran jusqu'a ce que gerer_touche renvoie une
    valeur differente de None (cette valeur devient le resultat
    de la boucle, transmis a l'appelant).

    - afficher(etat) : dessine l'ecran a partir de l'etat courant.
    - gerer_touche(etat, touche) : modifie etat en place et renvoie
      soit None (rester sur l'ecran), soit un resultat de sortie.

    Le rafraichissement n'a lieu que si l'etat a reellement change.
    Une comparaison superficielle (dict(etat)) ne suffit pas des
    qu'un champ est lui-meme un dict/liste modifie en place (ex:
    les decalages de defilement) : on utilise donc une copie
    profonde via repr() pour detecter tout changement, y compris
    imbrique, sans avoir a coder un cas particulier par ecran.
    """
    afficher(etat)

    while True:
        touche = lire_touche()
        avant = repr(etat)

        resultat = gerer_touche(etat, touche)

        if resultat is not None:
            return resultat

        if repr(etat) != avant:
            afficher(etat)


# ------------------------------------------------------------
# Conversion
# ------------------------------------------------------------

def caractere_valide(caractere, base):
    if caractere.isdigit():
        return int(caractere) < base
    return base == 16 and caractere in "ABCDEF"


def valeur_entiere(nombre, base):
    """(valeur, None) si ok, sinon (None, message_erreur)."""
    if nombre in ("", "-"):
        return None, "Saisie vide."
    try:
        return int(nombre, base), None
    except ValueError:
        return None, "Format invalide en " + NOMS_BASES[base] + "."


def convertir_toutes_bases(valeur):
    signe = "-" if valeur < 0 else ""
    absolu = abs(valeur)
    return {
        2: signe + bin(absolu)[2:],
        8: signe + oct(absolu)[2:],
        10: signe + str(absolu),
        16: signe + hex(absolu)[2:].upper()
    }


def ajouter_historique(historique, source, nombre, resultats):
    """Ajoute en tete, tronque, evite les doublons consecutifs."""
    if historique and historique[0][:2] == (source, nombre):
        return historique
    return ([(source, nombre, resultats)] + historique)[:TAILLE_HISTORIQUE]


# ------------------------------------------------------------
# Ecran : menu principal
# ------------------------------------------------------------

def etat_menu(historique):
    return {"source": 10, "historique": historique}


def afficher_menu(etat):
    effacer()
    entete()

    texte(20, 45, "BASE DE DEPART")

    largeur_case = 60
    for i, base in enumerate(BASES):
        x = 20 + i * (largeur_case + 8)
        actif = (base == etat["source"])
        fond = BLEU if actif else BLEU_CLAIR
        couleur = BLANC if actif else BLEU

        fill_rect(x, 65, largeur_case, 30, fond)
        texte(x + 14, 73, NOMS_BASES[base], couleur, fond)

    ligne(MARGE, 118, LARGEUR_ECRAN - 2 * MARGE)
    fleches_horizontal(20, 138)
    texte(58, 138, "G/D : choisir la base")

    texte(20, 168, "OK / EXE : saisir un nombre", GRIS)

    if etat["historique"]:
        texte(20, 190, "VAR : voir l'historique", BLEU)
    else:
        texte(20, 190, "Conversion vers toutes les bases", GRIS)


def gerer_menu(etat, touche):
    index = BASES.index(etat["source"])

    if touche == KEY_LEFT:
        etat["source"] = BASES[(index - 1) % len(BASES)]

    elif touche == KEY_RIGHT:
        etat["source"] = BASES[(index + 1) % len(BASES)]

    elif touche == KEY_OK or touche == KEY_EXE:
        return ("saisie", etat["source"])

    elif touche == KEY_VAR and etat["historique"]:
        return ("historique", None)

    return None


# ------------------------------------------------------------
# Ecran : historique
# ------------------------------------------------------------

def afficher_historique(etat):
    effacer()
    entete("Historique")

    historique = etat["historique"]

    if not historique:
        texte(MARGE, 60, "Aucune conversion pour le moment.", GRIS)
        texte(MARGE, 190, "VAR : retour", GRIS)
        return

    y = 40
    for i, (base_src, nombre, resultats) in enumerate(historique):
        actif = (i == etat["index"])

        if actif:
            fill_rect(0, y, LARGEUR_ECRAN, 30, BLEU_CLAIR)

        couleur = BLEU if actif else NOIR
        texte(MARGE, y + 4, NOMS_BASES[base_src] + " " + nombre, couleur)
        texte(MARGE, y + 18, "-> HEX " + resultats[16], GRIS)
        y += 34

    pied_de_page(y + 4, "H/B : choisir   OK : revoir   VAR : retour")


def gerer_historique(etat, touche):
    historique = etat["historique"]

    if touche == KEY_VAR:
        return ("retour", None)

    if not historique:
        return None

    if touche == KEY_UP:
        etat["index"] = (etat["index"] - 1) % len(historique)

    elif touche == KEY_DOWN:
        etat["index"] = (etat["index"] + 1) % len(historique)

    elif touche == KEY_OK or touche == KEY_EXE:
        return ("ouvrir", historique[etat["index"]])

    return None


# ------------------------------------------------------------
# Ecran : saisie
# ------------------------------------------------------------

def etat_saisie(base):
    return {
        "nombre": "", "position": 0, "base": base,
        "alpha": False, "erreur": ""
    }


def inserer(etat, caractere):
    n, p = etat["nombre"], etat["position"]
    etat["nombre"] = n[:p] + caractere + n[p:]
    etat["position"] += 1


def afficher_saisie(etat):
    effacer()
    entete()

    nombre, position, base = etat["nombre"], etat["position"], etat["base"]
    erreur = etat["erreur"]

    texte(MARGE, 42, "SAISIE EN")
    texte(240, 42, NOMS_BASES[base], BLEU)

    couleur_zone = ROUGE_CLAIR if erreur else BLEU_CLAIR
    fill_rect(MARGE, 66, LARGEUR_ECRAN - 2 * MARGE, 40, couleur_zone)

    largeur_max_car = 27
    debut = 0
    if len(nombre) > largeur_max_car:
        debut = max(0, min(position - largeur_max_car + 4,
                            len(nombre) - largeur_max_car))

    visible = nombre[debut:debut + largeur_max_car]
    texte(18, 76, visible, NOIR, couleur_zone)

    if debut > 0:
        texte(MARGE, 76, "<", GRIS, couleur_zone)
    if debut + largeur_max_car < len(nombre):
        texte(LARGEUR_ECRAN - 20, 76, ">", GRIS, couleur_zone)

    curseur_x = 10 * (position - debut) + 18
    fill_rect(curseur_x, 74, 2, 24, ROUGE if erreur else BLEU)

    if erreur:
        texte(MARGE, 118, erreur, ROUGE)
    elif base == 16:
        if etat["alpha"]:
            texte(MARGE, 118, "ALPHA actif : A-F", BLEU)
        else:
            texte(MARGE, 118, "ALPHA : appuyer pour A-F", GRIS)
    elif nombre:
        texte(MARGE, 118, str(len(nombre)) + " caractere(s)", GRIS)

    ligne(MARGE, 140, LARGEUR_ECRAN - 2 * MARGE)
    fleches_horizontal(MARGE, 158)
    texte(48, 158, "G/D : curseur")

    texte(MARGE, 180, "DEL : supprimer   (-) : signe", GRIS)
    texte(MARGE, 198, "OK/EXE : valider   VAR : menu", GRIS)


def gerer_saisie(etat, touche):
    nombre, position, base = etat["nombre"], etat["position"], etat["base"]
    etat["erreur"] = ""

    if touche == KEY_VAR:
        return ("annuler", None)

    if touche == KEY_ALPHA and base == 16:
        etat["alpha"] = not etat["alpha"]

    elif touche == KEY_LEFT:
        etat["position"] = max(0, position - 1)

    elif touche == KEY_RIGHT:
        etat["position"] = min(len(nombre), position + 1)

    elif touche == KEY_BACKSPACE:
        if position > 0:
            etat["nombre"] = nombre[:position - 1] + nombre[position:]
            etat["position"] = position - 1

    elif touche == KEY_OK or touche == KEY_EXE:
        _, err = valeur_entiere(nombre, base)
        if err:
            etat["erreur"] = err
        else:
            return ("valider", nombre)

    elif touche == KEY_MINUS and position == 0:
        if nombre.startswith("-"):
            etat["nombre"] = nombre[1:]
            etat["position"] = 0
        else:
            etat["nombre"] = "-" + nombre
            etat["position"] = 1

    elif etat["alpha"] and base == 16 and touche in LETTRES_HEX:
        if len(nombre) < LONGUEUR_MAX_SAISIE:
            inserer(etat, LETTRES_HEX[touche])
        else:
            etat["erreur"] = "Longueur maximale atteinte."

    elif touche in CHIFFRES:
        chiffre = CHIFFRES[touche]
        if not caractere_valide(chiffre, base):
            etat["erreur"] = "'" + chiffre + "' invalide en " + NOMS_BASES[base] + "."
        elif len(nombre) >= LONGUEUR_MAX_SAISIE:
            etat["erreur"] = "Longueur maximale atteinte."
        else:
            inserer(etat, chiffre)

    elif touche in LETTRES_HEX and base != 16:
        etat["erreur"] = "Lettres reservees a l'HEX."

    return None


# ------------------------------------------------------------
# Ecran : resultat (conversion simultanee vers toutes les bases)
# ------------------------------------------------------------

LARGEUR_CARACTERE = 10
LARGEUR_VISIBLE_RESULTAT = 230


def etat_resultat(source, nombre, resultats):
    maxima = {
        base: max(0, len(resultats[base]) * LARGEUR_CARACTERE - LARGEUR_VISIBLE_RESULTAT)
        for base in BASES
    }
    return {
        "source": source, "nombre": nombre, "resultats": resultats,
        "index": BASES.index(source),
        "decalages": {base: 0 for base in BASES},
        "maxima": maxima
    }


def afficher_resultat(etat):
    effacer()
    entete()

    source, nombre = etat["source"], etat["nombre"]
    texte(MARGE, 36, "ENTREE (" + NOMS_BASES[source] + ") : " + nombre)
    ligne(MARGE, 52, LARGEUR_ECRAN - 2 * MARGE)

    y = 60
    hauteur_ligne = 30

    for i, base in enumerate(BASES):
        actif = (i == etat["index"])

        if actif:
            fill_rect(0, y, LARGEUR_ECRAN, hauteur_ligne - 2, BLEU_CLAIR)

        marqueur = "* " if base == source else "  "
        couleur = BLEU if actif else NOIR
        fond = BLEU_CLAIR if actif else BLANC

        texte(MARGE, y + 4, marqueur + NOMS_BASES[base], couleur, fond)

        decalage = etat["decalages"][base]
        texte(70 - decalage, y + 4, etat["resultats"][base], couleur, fond)

        y += hauteur_ligne

    ligne(MARGE, y, LARGEUR_ECRAN - 2 * MARGE)

    base_active = BASES[etat["index"]]
    actif_gauche = etat["decalages"][base_active] > 0
    actif_droite = etat["decalages"][base_active] < etat["maxima"][base_active]

    fleches_vertical(MARGE, y + 8)
    texte(38, y + 12, "ligne", GRIS)

    fleches_horizontal(90, y + 8, actif_gauche, actif_droite)
    texte(128, y + 12, "defiler", GRIS)

    texte(200, y + 12, "OK:nouveau VAR:menu", GRIS)


def gerer_resultat(etat, touche):
    base_active = BASES[etat["index"]]

    if touche == KEY_UP:
        etat["index"] = (etat["index"] - 1) % len(BASES)

    elif touche == KEY_DOWN:
        etat["index"] = (etat["index"] + 1) % len(BASES)

    elif touche == KEY_LEFT:
        etat["decalages"][base_active] = max(0, etat["decalages"][base_active] - 20)

    elif touche == KEY_RIGHT:
        maximum = etat["maxima"][base_active]
        etat["decalages"][base_active] = min(maximum, etat["decalages"][base_active] + 20)

    elif touche == KEY_VAR:
        return "menu"

    elif touche == KEY_OK or touche == KEY_EXE:
        return "nouveau"

    return None


# ------------------------------------------------------------
# Enchainement des ecrans
# ------------------------------------------------------------

def ecran_menu(historique):
    return boucle_ecran(etat_menu(historique), afficher_menu, gerer_menu)


def ecran_historique(historique):
    etat = {"historique": historique, "index": 0}
    return boucle_ecran(etat, afficher_historique, gerer_historique)


def ecran_saisie(base):
    return boucle_ecran(etat_saisie(base), afficher_saisie, gerer_saisie)


def ecran_resultat(source, nombre, resultats):
    etat = etat_resultat(source, nombre, resultats)
    return boucle_ecran(etat, afficher_resultat, gerer_resultat)


def executer_conversion(source, nombre, historique):
    """Calcule le resultat, met a jour l'historique et affiche
    l'ecran resultat. Renvoie le nouvel historique."""
    valeur, err = valeur_entiere(nombre, source)

    if err:
        # Filet de securite : la saisie est deja validee en temps
        # reel, ce cas ne devrait normalement jamais survenir.
        return historique

    resultats = convertir_toutes_bases(valeur)
    historique = ajouter_historique(historique, source, nombre, resultats)

    ecran_resultat(source, nombre, resultats)

    return historique


# ------------------------------------------------------------
# Programme principal
# ------------------------------------------------------------

historique = []

while True:
    action_menu, donnee_menu = ecran_menu(historique)

    if action_menu == "historique":
        action_hist, donnee_hist = ecran_historique(historique)

        if action_hist == "ouvrir":
            source, nombre, resultats = donnee_hist
            ecran_resultat(source, nombre, resultats)

        continue

    # action_menu == "saisie"
    source = donnee_menu
    action_saisie, nombre = ecran_saisie(source)

    if action_saisie == "annuler":
        continue

    historique = executer_conversion(source, nombre, historique)
