"""Génère un exemple par template pour couvrir toutes les tailles (short/medium/long).

Utilise les backgrounds locaux dans assets/backgrounds/ (aucune requête Pexels),
et du texte en dur adapté à chaque template. Sorties dans output/examples/.
"""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from main import build_fields
from src.cli import generate_post
from src.template_lengths import TEMPLATE_LENGTH_CATEGORY


OUTPUT_DIR = ROOT / "output" / "examples"
LOGO = ROOT / "assets" / "logo_candimaker.png"
BG_DIR = ROOT / "assets" / "backgrounds"


# Un (theme, texte refactoré simulé) par template, choisi pour respecter
# les règles de longueur dans markdowns/template_length_rules.md.
EXAMPLES: dict[str, tuple[str, str]] = {
    # ---- short (≤ ~30 mots, 1–2 phrases par champ) ----
    "couverture": (
        "focus",
        "Le focus est un avantage compétitif.",
    ),
    "hook": (
        "execution",
        "Une idée ne vaut rien sans exécution.",
    ),
    "viral": (
        "consistency",
        "Un peu chaque jour bat beaucoup une fois.\n\n"
        "La régularité compose. L'intensité ponctuelle s'oublie.\n\n"
        "Commence petit. Recommence demain.",
    ),

    # ---- medium (60–150 mots, 3–6 phrases) ----
    "insight": (
        "discipline",
        "La motivation est une étincelle. La discipline est le moteur.\n\n"
        "Les jours où l'envie manque, seule la routine te porte. "
        "Ce que tu fais quand personne ne regarde définit ce que tu deviens. "
        "Choisis un cap, fixe un rituel, et tiens-le même à 20% d'énergie.",
    ),
    "story": (
        "failure",
        "J'ai longtemps cru que l'échec était l'opposé du succès. "
        "Jusqu'à ce qu'un projet s'écroule après six mois de travail. "
        "J'ai tout perdu sauf les leçons — et ce sont elles qui ont construit la suite.\n\n"
        "Aujourd'hui, je ne cherche plus à éviter l'échec. "
        "Je cherche à en extraire un signal avant les autres. "
        "C'est là que se joue la vraie avance.",
    ),
    "educational": (
        "time",
        "Ce n'est pas un problème de temps, c'est un problème de priorités.\n\n"
        "Liste tout ce qui t'a pris du temps hier, sans filtrer. Sois honnête.\n\n"
        "Classe chaque ligne en 'utile pour mon cap' ou 'bruit'. Le verdict pique.\n\n"
        "Supprime ou automatise les trois plus gros voleurs de temps cette semaine.",
    ),

    # ---- long (pas de plafond, 3–6 phrases par champ) ----
    "article": (
        "mindset",
        "Ton mindset détermine ton plafond bien avant tes compétences.\n\n"
        "La plupart des gens sous-estiment l'effet des croyances qu'ils entretiennent sur eux-mêmes. "
        "Un talent brut piloté par une mentalité de plafond finit toujours par plafonner. "
        "À l'inverse, un profil moyen animé par une conviction solide peut dépasser largement les attentes.\n\n"
        "Le mindset se construit par exposition: à des idées exigeantes, à des personnes qui refusent le confort, "
        "à des situations où l'inconfort devient une donnée normale. "
        "Ce n'est pas un trait inné, c'est une hygiène quotidienne.\n\n"
        "La bonne question n'est pas 'suis-je capable ?' mais 'qu'est-ce que je dois croire pour passer à l'acte aujourd'hui ?'. "
        "Les résultats suivent, toujours avec un décalage. "
        "Ta tâche est de tenir la ligne pendant ce décalage.",
    ),
    "listicle": (
        "risk",
        "Ne rien risquer est devenu le plus grand risque. Voici cinq façons de reprendre l'initiative.\n\n"
        "Sortir du confort\n"
        "Accepte une mission, une prise de parole ou un projet légèrement au-dessus de ton niveau actuel. "
        "C'est là que se forme la vraie compétence.\n\n"
        "Miser sur soi\n"
        "Investis dans une formation, un coach ou un outil qui te fait peur par son prix. "
        "L'engagement financier crée l'engagement mental.\n\n"
        "Publier sans attendre\n"
        "Partage ce que tu apprends, même imparfait. La visibilité compose beaucoup plus vite que la perfection cachée.\n\n"
        "Dire non\n"
        "Refuse les opportunités tièdes. Elles consomment le temps des vraies opportunités.\n\n"
        "Parier sur l'asymétrie\n"
        "Choisis les paris où la perte est bornée et le gain potentiel grand. Ignore le reste.",
    ),
    "long_quote": (
        "clarity",
        "L'action crée la clarté, pas l'inverse. "
        "On attend rarement d'y voir clair pour agir — c'est en agissant que le brouillard se dissipe. "
        "Chaque pas, même imparfait, te donne une information que mille heures de réflexion ne produiront jamais.",
    ),
}


def pick_background(theme: str) -> Path:
    """Retourne un background cohérent avec le thème s'il existe, sinon un fallback."""
    candidate = BG_DIR / f"{theme}.jpg"
    if candidate.is_file():
        return candidate
    # Fallback : premier .jpg disponible
    for p in sorted(BG_DIR.glob("*.jpg")):
        return p
    raise FileNotFoundError(f"Aucun background dans {BG_DIR}")


def main() -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    templates = sorted(TEMPLATE_LENGTH_CATEGORY.keys())
    order = {"short": 0, "medium": 1, "long": 2}
    templates.sort(key=lambda t: (order[TEMPLATE_LENGTH_CATEGORY[t]], t))

    for template in templates:
        size = TEMPLATE_LENGTH_CATEGORY[template]
        theme, text = EXAMPLES[template]
        bg = pick_background(theme)

        fields = build_fields(template, theme, text)
        filename = f"{size}_{template}.png"

        out = generate_post(
            image=bg,
            logo=LOGO,
            template=template,
            output_dir=OUTPUT_DIR,
            filename=filename,
            **fields,
        )
        print(f"[{size:<6}] {template:<11} -> {out.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
