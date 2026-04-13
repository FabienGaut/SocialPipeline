import os
from pathlib import Path

import requests
from dotenv import load_dotenv

load_dotenv()

PEXELS_API_KEY = os.getenv("PEXELS_API_KEY")

def get_pexels_image(theme):
    """
    Récupère la première image Pexels liée à un thème.

    Args:
        theme (str): mot-clé de recherche (ex: "productivity", "startup")

    Returns:
        str: URL de l'image (format large)
    """
    url = "https://api.pexels.com/v1/search"
    
    headers = {
        "Authorization": PEXELS_API_KEY
    }
    
    params = {
        "query": theme,
        "per_page": 1  # on veut juste la première image
    }

    response = requests.get(url, headers=headers, params=params)

    if response.status_code != 200:
        raise Exception(f"Pexels API error: {response.status_code}")

    data = response.json()

    if not data["photos"]:
        return None

    # Tu peux choisir différents formats
    image_url = data["photos"][0]["src"]["large"]

    return image_url


def download_pexels_image(theme, output_dir="assets/backgrounds"):
    """Télécharge la première image Pexels pour `theme` et renvoie le chemin local.

    Args:
        theme (str): mot-clé de recherche.
        output_dir (str): dossier où enregistrer l'image.

    Returns:
        str | None: chemin local de l'image téléchargée, ou None si aucune image.
    """
    image_url = get_pexels_image(theme)
    if image_url is None:
        return None

    out_dir = Path(output_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / f"{theme}.jpg"

    response = requests.get(image_url)
    if response.status_code != 200:
        raise Exception(f"Pexels image download error: {response.status_code}")

    out_path.write_bytes(response.content)
    return str(out_path)