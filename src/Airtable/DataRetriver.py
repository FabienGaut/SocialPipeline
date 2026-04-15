import os

import dotenv
import requests

dotenv.load_dotenv()

TOKEN = os.getenv("AIRTABLE_API_KEY")
BASE_ID = "app6cwJcbZBI8W9To"
TABLE = "tblUDSc6QRVAfT9tG"

BASE_URL = f"https://api.airtable.com/v0/{BASE_ID}/{TABLE}"
HEADERS = {"Authorization": f"Bearer {TOKEN}"}

POSTED_FIELD = "Posté"


def _get_first_image_url(fields, key="Image"):
    images = fields.get(key)
    if isinstance(images, list) and images:
        return images[0].get("url")
    return None


def _get_all_images(fields, key="Image"):
    images = fields.get(key)
    if isinstance(images, list):
        return [img.get("url") for img in images if "url" in img]
    return []


def fetch_records():
    """Récupère tous les records Airtable de la table configurée."""
    res = requests.get(BASE_URL, headers=HEADERS)
    res.raise_for_status()
    return res.json().get("records", [])


def _record_to_post(record):
    fields = record.get("fields", {})
    return {
        "record_id": record.get("id"),
        "theme": fields.get("Thème"),
        "text": fields.get("Texte"),
        "size": fields.get("Taille", "medium"),
        "type": fields.get("Type"),
        "image_url": _get_first_image_url(fields),
        "images": _get_all_images(fields),
        "posted": bool(fields.get(POSTED_FIELD, False)),
    }


def get_next_unposted():
    """Retourne le premier post Airtable non coché "Posté".

    Returns:
        dict | None: dict avec record_id/theme/text/size/type/images/posted,
        ou None si tous les posts sont déjà cochés.
    """
    for record in fetch_records():
        fields = record.get("fields", {})
        if fields.get(POSTED_FIELD):
            continue
        if not fields.get("Texte") or not fields.get("Thème"):
            continue
        return _record_to_post(record)
    return None


def mark_as_posted(record_id):
    """Coche la case "Posté" pour le record Airtable donné."""
    url = f"{BASE_URL}/{record_id}"
    payload = {"fields": {POSTED_FIELD: True}}
    res = requests.patch(url, headers={**HEADERS, "Content-Type": "application/json"}, json=payload)
    res.raise_for_status()
    return res.json()
