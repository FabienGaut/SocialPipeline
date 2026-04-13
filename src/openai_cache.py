"""Cache Redis pour les appels chat.completions d'OpenAI.

Clé = hash SHA-256 de (modèle, messages, paramètres pertinents).
Si Redis est indisponible, le cache devient un no-op transparent.
"""

from __future__ import annotations

import hashlib
import json
import logging
import os
from typing import Any, Callable

try:
    import redis  # type: ignore
except ImportError:  # pragma: no cover
    redis = None  # type: ignore


_DEFAULT_TTL = int(os.environ.get("OPENAI_CACHE_TTL", "2592000"))  # 30 jours
_PREFIX = "openai:chat:"
_client: "redis.Redis | None" = None
_disabled = False


def _get_client() -> "redis.Redis | None":
    global _client, _disabled
    if _disabled or redis is None:
        return None
    if _client is not None:
        return _client
    url = os.environ.get("REDIS_URL", "redis://localhost:6379/0")
    try:
        client = redis.Redis.from_url(url, decode_responses=True)
        client.ping()
    except Exception as exc:
        logging.warning("Redis indisponible (%s) — cache désactivé.", exc)
        _disabled = True
        return None
    _client = client
    return _client


def _make_key(payload: dict[str, Any]) -> str:
    blob = json.dumps(payload, sort_keys=True, ensure_ascii=False).encode("utf-8")
    return _PREFIX + hashlib.sha256(blob).hexdigest()


def cached_chat_completion(
    call: Callable[[], Any],
    *,
    model: str,
    messages: list[dict[str, str]],
    **params: Any,
) -> str:
    """Exécute `call()` (un appel OpenAI) en passant par le cache Redis.

    Retourne le contenu texte du premier choix.
    """
    key = _make_key({"model": model, "messages": messages, "params": params})
    client = _get_client()

    if client is not None:
        try:
            hit = client.get(key)
            if hit is not None:
                logging.debug("OpenAI cache HIT %s", key)
                return hit
        except Exception as exc:
            logging.warning("Redis GET échoué (%s) — bypass.", exc)

    response = call()
    content = response.choices[0].message.content

    if client is not None and content is not None:
        try:
            client.set(key, content, ex=_DEFAULT_TTL)
        except Exception as exc:
            logging.warning("Redis SET échoué (%s).", exc)

    return content
