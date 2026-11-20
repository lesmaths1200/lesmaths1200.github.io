#!/usr/bin/env python3
"""Pose le filigrane « @lesmaths1200 » sur un PDF qui n'en a pas.

Plutôt que de recomposer le filigrane — il faudrait embarquer sa police —
on en fabrique un calque à partir d'un PDF déjà filigrané : on vide le flux
de contenu de sa première page et on ne garde que le flux du filigrane, puis
qpdf superpose ce calque sur chaque page de la cible.

Le vidage se fait sur place, à longueur d'octets constante, pour ne pas
fausser la table des renvois du fichier décompressé.
"""

import argparse
import re
import subprocess
import tempfile
from pathlib import Path


def construire_calque(modele: Path, calque: Path) -> None:
    with tempfile.TemporaryDirectory() as tmp:
        clair = Path(tmp) / "clair.pdf"
        subprocess.run(["qpdf", "--qdf", "--object-streams=disable", str(modele), str(clair)],
                       check=False, capture_output=True)
        données = clair.read_bytes()

        page = re.search(rb"\n\d+ 0 obj\n<<\n  /Contents \[\n(.*?)\n  \]", données, re.S)
        flux = [int(n) for n in re.findall(rb"(\d+) 0 R", page.group(1))]

        # Le dernier flux de la page est celui du filigrane (ajouté après coup) ;
        # tous les autres portent le cours lui-même et doivent disparaître.
        for num in flux[:-1]:
            motif = re.compile(rb"(\n%d 0 obj\n.*?\nstream\n)(.*?)(\nendstream)" % num, re.S)
            données = motif.sub(lambda m: m.group(1) + b" " * len(m.group(2)) + m.group(3), données, count=1)

        # Le flux du filigrane s'ouvre sur un « Q » qui refermait l'état
        # graphique du cours : sans le cours, il ne referme plus rien et les
        # lecteurs protestent. On le remplace par une espace.
        dernier = re.compile(rb"(\n%d 0 obj\n.*?\nstream\n)Q(\n)" % flux[-1], re.S)
        données = dernier.sub(lambda m: m.group(1) + b" " + m.group(2), données, count=1)

        modifie = Path(tmp) / "modifie.pdf"
        modifie.write_bytes(données)
        subprocess.run(["qpdf", str(modifie), "--pages", str(modifie), "1", "--", str(calque)],
                       check=True, capture_output=True)


def poser(entree: Path, sortie: Path, calque: Path, pages=None) -> None:
    commande = ["qpdf", str(entree), "--overlay", str(calque), "--repeat=1"]
    if pages:
        commande.append(f"--to={pages}")
    commande += ["--", str(sortie)]
    subprocess.run(commande, check=True, capture_output=True)


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("modele", help="PDF déjà filigrané, qui sert de patron")
    p.add_argument("entree")
    p.add_argument("sortie")
    p.add_argument("--pages", help="pages de destination (défaut : toutes)")
    a = p.parse_args()
    with tempfile.TemporaryDirectory() as tmp:
        calque = Path(tmp) / "calque.pdf"
        construire_calque(Path(a.modele), calque)
        poser(Path(a.entree), Path(a.sortie), calque, a.pages)
    print(f"{a.sortie} : filigrane posé")
