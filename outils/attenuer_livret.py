#!/usr/bin/env python3
"""Même atténuation que « attenuer_filigrane.py », pour le livret d'exercices.

Le livret a été produit par une autre chaîne : son filigrane pose la couleur
avec « rg » (et non « /DeviceRGB cs ... sc »), en 0.902344 0.462646 0.0627441,
et partage un seul état graphique /R110 pour ses 36 pages. Le réglage visé
est le même : gris 0,55 à 12 % d'opacité.

Les deux réécritures gardent exactement le nombre d'octets d'origine — la
couleur en complétant d'espaces, l'opacité en écrivant « .12 » sans le zéro
de tête, que PDF accepte — pour ne pas décaler la table des renvois.
"""

import re
import subprocess
import sys
import tempfile
from pathlib import Path

COULEUR_ORIGINE = b"0.902344 0.462646 0.0627441 rg"
OPACITE_ORIGINE = b"/ca 0.4"
OPACITE_CIBLE = b"/ca .12"
GRIS = b"0.55 0.55 0.55"


def attenuer(entree: Path, sortie: Path) -> int:
    couleur = GRIS + b" " * (len(COULEUR_ORIGINE) - len(GRIS) - 3) + b" rg"
    assert len(couleur) == len(COULEUR_ORIGINE)
    assert len(OPACITE_CIBLE) == len(OPACITE_ORIGINE)

    with tempfile.TemporaryDirectory() as tmp:
        clair = Path(tmp) / "clair.pdf"
        subprocess.run(["qpdf", "--qdf", "--object-streams=disable", str(entree), str(clair)],
                       check=False, capture_output=True)
        données = clair.read_bytes()

        posées = len(re.findall(re.escape(COULEUR_ORIGINE), données))
        if not posées:
            return 0
        données = données.replace(COULEUR_ORIGINE, couleur)

        # L'état graphique du filigrane : le seul appelé juste avant sa couleur.
        noms = set(re.findall(rb"/(R\d+) gs\n" + re.escape(couleur), données))
        objets = set()
        for nom in noms:
            objets |= {int(n) for n in re.findall(rb"/" + nom + rb" (\d+) 0 R", données)}
        for num in objets:
            motif = re.compile(rb"(\n%d 0 obj\n.*?)%s(.*?\nendobj)" % (num, re.escape(OPACITE_ORIGINE)), re.S)
            données = motif.sub(lambda m: m.group(1) + OPACITE_CIBLE + m.group(2), données, count=1)

        modifie = Path(tmp) / "modifie.pdf"
        modifie.write_bytes(données)
        subprocess.run(["qpdf", "--object-streams=generate", str(modifie), str(sortie)],
                       check=True, capture_output=True)
    return posées


if __name__ == "__main__":
    n = attenuer(Path(sys.argv[1]), Path(sys.argv[2]))
    print(f"{sys.argv[1]} : {n} page(s) filigranée(s)")
