"""Fonctions d'appel haut-niveau et CLI pour la génération de visuels."""

from __future__ import annotations

import argparse
from pathlib import Path

from src.post_maker import list_templates, make_post


def _parse_field(pair: str) -> tuple[str, str]:
    if "=" not in pair:
        raise argparse.ArgumentTypeError(
            f"--field attend 'nom=valeur' (reçu : {pair!r})"
        )
    key, value = pair.split("=", 1)
    key = key.strip()
    if not key.isidentifier():
        raise argparse.ArgumentTypeError(f"Nom de champ invalide : {key!r}")
    return key, value


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Génère un visuel social depuis un template HTML/CSS.")
    p.add_argument("--image", required=True, help="Chemin vers l'image de fond.")
    p.add_argument("--logo", default=None, help="Chemin vers le logo (utilisé par les templates qui l'exposent).")
    p.add_argument("--output-dir", default="output", help="Dossier de sortie (défaut: output).")
    p.add_argument("--filename", default=None, help="Nom du fichier de sortie (défaut: <slug>.png).")
    p.add_argument(
        "--template",
        default="couverture",
        help=f"Nom du template dans templates/ (disponibles : {', '.join(list_templates())}).",
    )
    p.add_argument(
        "--field",
        action="append",
        default=[],
        type=_parse_field,
        metavar="NOM=VALEUR",
        help="Champ à injecter dans le template (répétable).",
    )
    # Raccourcis courants, utilisables sans --field
    p.add_argument("--title", default=None, help="Raccourci pour --field title=...")
    p.add_argument("--subtitle", default=None, help="Raccourci pour --field subtitle=...")
    return p.parse_args()


def _slug(text: str, limit: int = 40) -> str:
    keep = []
    for ch in text.lower():
        if ch.isalnum():
            keep.append(ch)
        elif ch in " -_":
            keep.append("-")
    s = "".join(keep).strip("-")
    while "--" in s:
        s = s.replace("--", "-")
    return (s or "post")[:limit]


def _default_filename(fields: dict[str, str]) -> str:
    for key in ("title", "headline", "hook", "subtitle"):
        if fields.get(key):
            return f"{_slug(fields[key])}.png"
    return "post.png"


def generate_post(
    image: str | Path,
    logo: str | Path | None = None,
    template: str = "couverture",
    output_dir: str | Path = "output",
    filename: str | None = None,
    **fields: str,
) -> Path:
    """Génère le visuel pour `template` et renvoie le chemin du fichier produit.

    Les `fields` sont les placeholders attendus par le template choisi
    (ex. `title`/`subtitle` pour couverture, `hook`/`subhook`/`tag`/`footer`
    pour hook, etc.).
    """
    filename = filename or _default_filename(fields)
    return make_post(
        template=template,
        background=image,
        logo=logo,
        output_dir=output_dir,
        filename=filename,
        **fields,
    )


def run_cli() -> None:
    args = parse_args()
    fields: dict[str, str] = dict(args.field)
    if args.title is not None:
        fields["title"] = args.title
    if args.subtitle is not None:
        fields["subtitle"] = args.subtitle

    out = generate_post(
        image=args.image,
        logo=args.logo,
        template=args.template,
        output_dir=args.output_dir,
        filename=args.filename,
        **fields,
    )
    print(f"Image générée : {out.resolve()}")
