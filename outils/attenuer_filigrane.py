#!/usr/bin/env python3
"""Rend plus terne le filigrane « @lesmaths1200 » des PDF de cours et d'exercices.

Le filigrane est, sur chaque page, un bloc de texte ajouté après coup :

    q /gsN gs /DeviceRGB cs 0.90196 0.46275 0.06275 sc BT /F8 100 Tf ... Tj ET Q

Deux réglages le rendent voyant : la couleur orange vif et l'opacité 0,4
portée par l'état graphique /gsN (un objet par page, qui ne sert qu'à lui).
On agit sur les deux. La couleur est réécrite sur exactement le même nombre
de caractères, pour ne pas fausser la longueur des flux décompressés.
"""

import argparse
import re
import subprocess
import sys
import tempfile
from pathlib import Path

COULEUR_ORIGINE = b"0.90196 0.46275 0.06275"
OPACITE_ORIGINE = b"/ca 0.4"


def couleur_en_octets(rvb):
    texte = " ".join(f"{c:.5f}" for c in rvb).encode()
    if len(texte) != len(COULEUR_ORIGINE):
        raise ValueError(f"couleur de longueur {len(texte)}, attendu {len(COULEUR_ORIGINE)}")
    return texte


def attenuer(entree: Path, sortie: Path, couleur, opacite) -> int:
    with tempfile.TemporaryDirectory() as tmp:
        clair = Path(tmp) / "clair.pdf"
        subprocess.run(["qpdf", "--qdf", "--object-streams=disable", str(entree), str(clair)],
                       check=False, capture_output=True)
        données = clair.read_bytes()

        # Les états graphiques du filigrane : ceux que le bloc de couleur appelle.
        noms = set(re.findall(rb"/(gs\d+) gs\n/DeviceRGB cs\n" + re.escape(COULEUR_ORIGINE), données))
        objets = set()
        for nom in noms:
            objets |= {int(n) for n in re.findall(rb"/" + nom + rb" (\d+) 0 R", données)}
        if not objets:
            return 0

        données = données.replace(COULEUR_ORIGINE + b" sc", couleur_en_octets(couleur) + b" sc")

        # L'opacité est réécrite sur le même nombre d'octets que « /ca 0.4 » :
        # une décimale de plus se paie d'une espace d'indentation en moins,
        # sinon la table des renvois du fichier décompressé se décale.
        nouvelle_opacite = f"/ca {opacite:g}".encode()
        marge = b" " * max(0, len(OPACITE_ORIGINE) - len(nouvelle_opacite))
        retrait = b"  "[: max(0, 2 - (len(nouvelle_opacite) - len(OPACITE_ORIGINE)))]
        remplacement = retrait + nouvelle_opacite + marge
        for num in objets:
            motif = re.compile(rb"(\n%d 0 obj\n.*?)\n  %s(.*?\nendobj)" % (num, re.escape(OPACITE_ORIGINE)), re.S)
            données = motif.sub(lambda m: m.group(1) + b"\n" + remplacement + m.group(2), données, count=1)

        modifie = Path(tmp) / "modifie.pdf"
        modifie.write_bytes(données)
        subprocess.run(["qpdf", "--object-streams=generate", str(modifie), str(sortie)],
                       check=True, capture_output=True)
    return len(objets)


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("entree")
    p.add_argument("sortie")
    p.add_argument("--couleur", default="0.71,0.495,0.295", help="r,g,b entre 0 et 1")
    p.add_argument("--opacite", type=float, default=0.15)
    a = p.parse_args()
    rvb = [float(x) for x in a.couleur.split(",")]
    n = attenuer(Path(a.entree), Path(a.sortie), rvb, a.opacite)
    print(f"{a.entree} : {n} page(s) filigranée(s)" if n else f"{a.entree} : aucun filigrane")
