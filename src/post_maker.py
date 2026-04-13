"""Génère une image sociale à partir d'un template HTML/CSS.

Les templates sont stockés dans le dossier `templates/` (ex. `couverture.html`,
`hook.html`, `educational.html`…). Ils sont chargés dynamiquement selon le type
demandé.

Le rendu utilise une substitution par regex : seuls les jetons `{nom}` où
`nom` est un identifiant (ex. `{title}`, `{bg}`) sont remplacés — les `{...}`
du CSS ne sont pas affectés, donc les templates n'ont **pas** besoin de doubler
leurs accolades.

Placeholders réservés automatiquement :
    - `{W}`, `{H}`  : dimensions
    - `{bg}`        : image de fond (data URI) si `background` est fourni
    - `{logo}`      : logo transparent (data URI) si `logo` est fourni

Tous les autres placeholders sont passés via `**fields`.
"""

from __future__ import annotations

import base64
import io
import mimetypes
import re
from pathlib import Path

from PIL import Image
from playwright.sync_api import sync_playwright


WIDTH, HEIGHT = 1080, 1350  # format 4:5 (Instagram)

TEMPLATES_DIR = Path(__file__).resolve().parent.parent / "templates"

_PLACEHOLDER_RE = re.compile(r"\{([A-Za-z_][A-Za-z0-9_]*)\}")


def _load_template(template: str) -> str:
    path = TEMPLATES_DIR / f"{template}.html"
    if not path.is_file():
        available = sorted(p.stem for p in TEMPLATES_DIR.glob("*.html"))
        raise FileNotFoundError(
            f"Template '{template}' introuvable dans {TEMPLATES_DIR}. "
            f"Disponibles : {available}"
        )
    return path.read_text(encoding="utf-8")


def list_templates() -> list[str]:
    return sorted(p.stem for p in TEMPLATES_DIR.glob("*.html"))


def _render(template_html: str, values: dict[str, str]) -> str:
    missing: list[str] = []

    def sub(m: re.Match[str]) -> str:
        key = m.group(1)
        if key in values:
            return str(values[key])
        missing.append(key)
        return m.group(0)

    rendered = _PLACEHOLDER_RE.sub(sub, template_html)
    if missing:
        uniq = sorted(set(missing))
        raise KeyError(
            f"Placeholders manquants pour ce template : {uniq}. "
            f"Fournis via les kwargs de make_post/generate_post."
        )
    return rendered


def _to_data_uri(path: Path) -> str:
    mime, _ = mimetypes.guess_type(str(path))
    if mime is None:
        mime = "image/png"
    b64 = base64.b64encode(path.read_bytes()).decode("ascii")
    return f"data:{mime};base64,{b64}"


def _logo_to_transparent_data_uri(path: Path, threshold: int = 240) -> str:
    """Charge le logo et rend les pixels blancs (≥ threshold sur R,G,B) transparents."""
    img = Image.open(path).convert("RGBA")
    pixels = img.load()
    w, h = img.size
    for y in range(h):
        for x in range(w):
            r, g, b, a = pixels[x, y]
            if r >= threshold and g >= threshold and b >= threshold:
                pixels[x, y] = (r, g, b, 0)
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    b64 = base64.b64encode(buf.getvalue()).decode("ascii")
    return f"data:image/png;base64,{b64}"


def _escape(text: str) -> str:
    return (
        text.replace("&", "&amp;")
            .replace("<", "&lt;")
            .replace(">", "&gt;")
    )


def make_post(
    template: str = "couverture",
    background: str | Path | None = None,
    logo: str | Path | None = None,
    output_dir: str | Path = "output",
    filename: str = "post.png",
    **fields: str,
) -> Path:
    values: dict[str, str] = {"W": str(WIDTH), "H": str(HEIGHT)}

    if background is not None:
        bg_path = Path(background).resolve()
        if not bg_path.is_file():
            raise FileNotFoundError(bg_path)
        values["bg"] = _to_data_uri(bg_path)

    if logo is not None:
        logo_path = Path(logo).resolve()
        if not logo_path.is_file():
            raise FileNotFoundError(logo_path)
        values["logo"] = _logo_to_transparent_data_uri(logo_path)

    for key, val in fields.items():
        values[key] = _escape(str(val))

    html = _render(_load_template(template), values)

    out_dir = Path(output_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / filename

    with sync_playwright() as p:
        browser = p.chromium.launch()
        context = browser.new_context(
            viewport={"width": WIDTH, "height": HEIGHT},
            device_scale_factor=1,
        )
        page = context.new_page()
        page.set_content(html, wait_until="networkidle")
        page.wait_for_timeout(300)  # laisser les fonts se stabiliser
        page.screenshot(path=str(out_path), omit_background=False, full_page=False)
        browser.close()

    return out_path
