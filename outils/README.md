# Outils — le filigrane des PDF

Trois scripts Python pour le filigrane « @lesmaths1200 » des PDF de `cours/`
et `exercices/`. Ils ne dépendent que de **qpdf** (`port install qpdf` ou
`brew install qpdf`) et de Python 3 : rien à installer avec pip.

Tous réécrivent le PDF **à longueur d'octets constante** là où c'est
nécessaire, pour ne pas fausser la table des renvois du fichier décompressé.
Le texte, le nombre de pages et tout le reste du document sont intacts —
vérifié sur les 35 PDF du site le 20 novembre 2026.

## Le filigrane a deux écritures

C'est le piège de ce dossier. Deux chaînes de production ont servi :

| | 32 PDF ordinaires | `exercices/livret.pdf` |
|---|---|---|
| couleur | `/DeviceRGB cs … sc` | `rg` |
| valeur d'origine | `0.90196 0.46275 0.06275` | `0.902344 0.462646 0.0627441` |
| état graphique | un par page | un seul, `/R110`, partagé |
| script | `attenuer_filigrane.py` | `attenuer_livret.py` |

Un script qui ne cherche que la première écriture **rate le livret en
silence**, sans rien signaler. C'est arrivé une fois.

## Réglage actuel

Gris `0.55 0.55 0.55` à **12 %** d'opacité, depuis le 20 novembre 2026.
Avant : orange `0.902 0.463 0.063` à 40 %, jugé trop voyant — et à 40 % il
délavait aussi le texte noir qu'il traversait.

## Utilisation

Rendre plus terne un filigrane déjà présent :

```sh
python3 outils/attenuer_filigrane.py cours/entiers.pdf sortie.pdf \
    --couleur 0.55,0.55,0.55 --opacite 0.12
python3 outils/attenuer_livret.py exercices/livret.pdf sortie.pdf
```

Poser un filigrane sur un PDF qui n'en a pas. Le premier argument est un PDF
**déjà filigrané** : le script en tire un calque, ce qui est le seul moyen
d'hériter de la police embarquée, donc d'obtenir exactement la même taille,
la même inclinaison et la même position.

```sh
python3 outils/poser_filigrane.py cours/Pythagore.pdf cours/neuf.pdf sortie.pdf
python3 outils/poser_filigrane.py cours/Pythagore.pdf livret.pdf sortie.pdf --pages 2-37
```

`--pages` limite les pages de destination : le livret laisse sa couverture et
sa dernière page nues.

## Après coup

Les PDF sont relus en ligne à chaque ouverture, sur iPhone comme sur Android :
**rien à republier** sur l'App Store ni sur le Play Store, un `git push` suffit.
Compter une minute ou deux pour que GitHub Pages serve les nouveaux fichiers.

Les copies de `LesMaths1200/AppData/` dans le dépôt de l'app ne servent que de
repli hors ligne, mais mieux vaut les mettre à jour en même temps.
