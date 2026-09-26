# numworks-baseconv

Convertisseur interactif BIN/OCT/DEC/HEX pour calculatrice NumWorks (Python).

Saisis un nombre dans une base au choix, et obtiens instantanément sa conversion dans les trois autres bases — sans avoir à ressaisir ou choisir une base cible.

## Fonctionnalités

- **Conversion simultanée** vers binaire, octal, décimal et hexadécimal à partir d'une seule saisie.
- **Validation en temps réel** : un caractère invalide pour la base choisie (ex: `9` en binaire, une lettre hors HEX) déclenche un message d'erreur immédiat au lieu d'un blocage silencieux.
- **Historique** des 5 dernières conversions, consultable et réouvrable sans ressaisie.
- **Défilement** horizontal pour les nombres trop longs pour l'écran, en saisie comme en résultat.
- **Support des nombres négatifs**.

## Installation

1. Ouvrir [my.numworks.com/python](https://my.numworks.com/python).
2. Créer un nouveau script et copier le contenu de [`baseconv.py`](./baseconv.py).
3. Importer le script sur la calculatrice (via le compte NumWorks ou en le collant directement dans l'app Python de la calculatrice).

Fonctionne aussi dans le [simulateur NumWorks](https://www.numworks.com/simulator/) pour tester sans calculatrice physique.

## Utilisation

- **Menu principal** : flèches gauche/droite pour choisir la base de départ, `OK`/`EXE` pour saisir un nombre.
- **Saisie** : taper le nombre au clavier (chiffres, `ALPHA` puis `EXP`/`LN`/`LOG`/`i`/`,`/`^` pour A-F en hexadécimal), `(-)` pour le signe, `DEL` pour supprimer, `OK`/`EXE` pour valider.
- **Résultat** : flèches haut/bas pour changer de base affichée, gauche/droite pour défiler un résultat trop long, `OK`/`EXE` pour une nouvelle saisie, `VAR` pour revenir au menu.
- **Historique** : depuis le menu, `VAR` (si des conversions existent) pour consulter les 5 dernières, `OK` pour en rouvrir une.

## Compatibilité

Ce script dépend des modules `ion` et `kandinsky`, propres au firmware Epsilon de NumWorks. Il ne fonctionne donc que sur une calculatrice NumWorks ou son simulateur officiel — pas sur un autre modèle de calculatrice ni en Python standard.

La logique de conversion elle-même (fonctions `caractere_valide`, `valeur_entiere`, `convertir_toutes_bases`, `ajouter_historique`) est indépendante de ces modules et réutilisable telle quelle dans un autre contexte (script console, interface graphique différente, etc.).

## Licence

Aucune licence spécifiée pour le moment.
