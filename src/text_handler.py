# Imports
import json
import logging
import os

from requests import post

from openai import OpenAI
from dotenv import load_dotenv

from src.openai_cache import cached_chat_completion
from src.template_lengths import load_length_rules
# Constants

load_dotenv()
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
client = OpenAI(api_key=os.environ.get('OPENAI_API_KEY'))

# Functions


def get_text_from_json(file_path):
    """
    Reads a JSON file and returns the next post's theme, seed text, size and id.

    Args:
        file_path (str): The path to the JSON file.

    Returns:
        tuple[str, str, str, str] | None: (theme, text, size, post_id) for
        the next unused post, or None if all posts have already been used.
    """
    with open(file_path, 'r') as file:
        data = json.load(file)

    posts = data["posts"]
    last_post = data.get("last_post_id")

    if last_post is None:
        next_idx = 0
    else:
        idx = next((i for i, p in enumerate(posts) if p["id"] == last_post), None)
        if idx is None:
            raise KeyError(f"last_post_id '{last_post}' not found in posts")
        next_idx = idx + 1

    if next_idx >= len(posts):
        logging.warning("TEXTS ALL POSTED ALREADY, PLEASE UPDATE THE TEXTS")
        return None

    next_post = posts[next_idx]
    return (
        next_post["theme"],
        next_post["text"],
        next_post.get("size", "medium"),
        next_post["id"],
    )


def mark_post_as_used(file_path, post_id):
    """Met à jour `last_post_id` dans le JSON après avoir utilisé un post."""
    with open(file_path, 'r') as file:
        data = json.load(file)
    data["last_post_id"] = post_id
    with open(file_path, 'w') as file:
        json.dump(data, file, indent=4)



def adapt_prompt(social_media, template=None):
    """Build the system prompt for a single-platform refactor.

    Args:
        social_media: target platform name (e.g. "linkedin").
        template: visual template the text will be placed into. Used to
            inject the appropriate length/density rules.
    """
    with open("markdowns/prompt_helper.md", 'r') as file:
        prompt_helper = file.read()
    with open("markdowns/social_prompt_maker.md", 'r') as file:
        social_media_prompt_helper = file.read()

    social_media_prompt_helper = social_media_prompt_helper.split("##")

    prompt_helper = prompt_helper + "## Style" + [s for s in social_media_prompt_helper if social_media.lower() in s.lower()][0]
    prompt_helper = prompt_helper.split("****")
    prompt_helper = prompt_helper[0] + social_media + prompt_helper[1]
    prompt_helper += load_length_rules(template)
    return prompt_helper


def refactor_text(text, social_media, template=None):
    """Refactor `text` for `social_media`, sized for the target `template`."""
    prompt_helper = adapt_prompt(social_media, template=template)
    model = "gpt-4.1-mini"
    messages = [
        {"role": "system", "content": prompt_helper},
        {"role": "user", "content": text},
    ]
    return cached_chat_completion(
        lambda: client.chat.completions.create(model=model, messages=messages),
        model=model,
        messages=messages,
    )


def all_social_media(text, template=None):
    """Generate one variant per platform, sized for the target `template`."""
    with open("markdowns/every_platform_prompt_helper.md", 'r') as file:
        prompt_helper = file.read()
    prompt_helper += load_length_rules(template)

    model = "gpt-4.1-mini"
    messages = [
        {"role": "system", "content": prompt_helper},
        {"role": "user", "content": text},
    ]
    return cached_chat_completion(
        lambda: client.chat.completions.create(model=model, messages=messages),
        model=model,
        messages=messages,
    )

