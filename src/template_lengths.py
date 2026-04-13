"""Catégorie de longueur par template + chargement de la section associée.

Chaque template visuel appartient à une catégorie (`short`, `medium`, `long`)
qui détermine combien de texte la génération doit produire. La section
correspondante du fichier `markdowns/template_length_rules.md` est injectée
dans le prompt système.
"""

from __future__ import annotations

import re
from pathlib import Path

TEMPLATE_LENGTH_CATEGORY: dict[str, str] = {
    # Templates "cover / punchline" — texte minimal
    "couverture": "short",
    "hook": "short",
    "viral": "short",
    # Templates avec headline + corps court
    "insight": "medium",
    "story": "medium",
    "educational": "medium",
    # Templates pensés pour héberger du texte riche
    "article": "long",
    "listicle": "long",
    "long_quote": "long",
}

DEFAULT_CATEGORY = "medium"

_RULES_PATH = Path(__file__).resolve().parent.parent / "markdowns" / "template_length_rules.md"
_SECTION_RE = re.compile(r"^##\s+(\w+)\s*$", re.MULTILINE)


def category_for(template: str | None) -> str:
    if template is None:
        return DEFAULT_CATEGORY
    return TEMPLATE_LENGTH_CATEGORY.get(template, DEFAULT_CATEGORY)


def load_length_rules(template: str | None) -> str:
    """Retourne le bloc markdown ``## Template Length Rules`` à injecter.

    Si `template` est inconnu, utilise la catégorie par défaut.
    Lève FileNotFoundError si le fichier de règles est introuvable.
    """
    cat = category_for(template)
    text = _RULES_PATH.read_text(encoding="utf-8")

    matches = list(_SECTION_RE.finditer(text))
    body = ""
    for i, m in enumerate(matches):
        if m.group(1).lower() == cat:
            start = m.end()
            end = matches[i + 1].start() if i + 1 < len(matches) else len(text)
            body = text[start:end].strip()
            break
    if not body:
        raise ValueError(f"Section '{cat}' absente de {_RULES_PATH}")

    return (
        "\n\n---\n\n## Template Length Rules\n\n"
        f"*(applies to template: `{template or 'default'}`, category: `{cat}`)*\n\n"
        f"{body}\n"
    )
