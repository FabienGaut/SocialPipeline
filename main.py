from src.cli import generate_post
from src.image_getter import download_pexels_image
from src.text_handler import get_text_from_json, mark_post_as_used, refactor_text


POSTS_FILE = "data/tests.json"
TITLE_PLATFORM = "linkedin"

# Un template par catégorie de longueur (cf. src/template_lengths.py).
SIZE_TO_TEMPLATE: dict[str, str] = {
    "short": "hook",
    "medium": "insight",
    "long": "article",
}
DEFAULT_TEMPLATE = "insight"


def template_for_size(size: str) -> str:
    """Choisit le template à utiliser en fonction de la taille du post."""
    return SIZE_TO_TEMPLATE.get(size, DEFAULT_TEMPLATE)


def _split_paragraphs(text: str, n: int) -> list[str]:
    """Découpe `text` en `n` paragraphes (pad avec chaînes vides si besoin)."""
    parts = [p.strip() for p in text.split("\n\n") if p.strip()]
    if len(parts) < n:
        # Si on n'a pas assez de blocs `\n\n`, on retombe sur les sauts simples.
        parts = [p.strip() for p in text.splitlines() if p.strip()]
    while len(parts) < n:
        parts.append("")
    return parts[:n]


def build_fields(template: str, theme: str, text: str) -> dict[str, str]:
    """Adapte le texte refactoré aux placeholders du template choisi."""
    tag = f"#{theme}"
    footer = "@candimaker"

    if template == "couverture":
        return {"title": text, "subtitle": theme}

    if template == "insight":
        return {"title": theme, "text": text, "tag": tag, "footer": footer}

    if template == "hook":
        return {"hook": text, "subhook": theme, "tag": tag, "footer": footer}

    if template == "story":
        parts = _split_paragraphs(text, 2)
        return {
            "hook": theme,
            "story": parts[0],
            "punch": parts[1],
            "tag": tag,
            "footer": footer,
        }

    if template == "viral":
        parts = _split_paragraphs(text, 3)
        return {
            "headline": theme,
            "subtext": parts[0],
            "punch": parts[1],
            "cta": parts[2],
            "tag": tag,
            "footer": footer,
        }

    if template == "educational":
        parts = _split_paragraphs(text, 4)
        return {
            "title": theme,
            "intro": parts[0],
            "step1": parts[1],
            "step2": parts[2],
            "step3": parts[3],
            "tag": tag,
            "footer": footer,
        }

    if template == "article":
        parts = _split_paragraphs(text, 4)
        return {
            "kicker": theme,
            "title": theme.capitalize(),
            "lead": parts[0],
            "paragraph1": parts[1],
            "paragraph2": parts[2],
            "paragraph3": parts[3],
            "author": footer,
            "footer": tag,
        }

    if template == "listicle":
        parts = _split_paragraphs(text, 6)  # intro + 5 items
        intro = parts[0]
        items = parts[1:6]
        fields: dict[str, str] = {
            "tag": tag,
            "title": theme.capitalize(),
            "intro": intro,
            "footer": footer,
            "cta": "",
        }
        for i, item in enumerate(items, start=1):
            # On sépare titre / description d'un item sur la première ligne / le reste.
            lines = item.splitlines()
            item_title = lines[0].strip() if lines else ""
            item_desc = " ".join(l.strip() for l in lines[1:]).strip()
            fields[f"item{i}_title"] = item_title
            fields[f"item{i}_desc"] = item_desc
        return fields

    if template == "long_quote":
        return {
            "tag": tag,
            "quote": text,
            "author": footer,
            "source": "",
            "context": "",
            "footer": theme,
            "handle": footer,
        }

    raise ValueError(f"Template non supporté par main.py : {template}")


def main():
    result = get_text_from_json(POSTS_FILE)
    if not result:
        return
    theme, seed_text, size, post_id = result

    template = template_for_size(size)

    # L'LLM enrichit le texte seed (phrase courte ou thème) pour le réseau
    # social cible, et aux contraintes de longueur du template — voir
    # markdowns/template_length_rules.md.
    refactored_text = refactor_text(seed_text, TITLE_PLATFORM, template=template)

    background = download_pexels_image(theme)
    if background is None:
        raise RuntimeError(f"Aucune image Pexels trouvée pour le thème : {theme!r}")

    out = generate_post(
        image=background,
        logo="assets/logo_candimaker.png",
        template=template,
        **build_fields(template, theme, refactored_text),
    )
    print(f"Image générée : {out.resolve()} (template={template}, size={size})")

    mark_post_as_used(POSTS_FILE, post_id)


if __name__ == "__main__":
    main()
