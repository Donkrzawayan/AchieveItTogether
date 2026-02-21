import json
import os
import logging
import discord

logger = logging.getLogger(__name__)

LOCALES_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "locales")
TRANSLATIONS: dict[str, dict] = {}


def _load_translations():
    """Loads all .json files from the locales folder into the cache."""
    if not os.path.exists(LOCALES_DIR):
        logger.warning(f"Locales directory not found at {LOCALES_DIR}")
        return

    for filename in os.listdir(LOCALES_DIR):
        if filename.endswith(".json"):
            lang_code = filename[:-5]
            filepath = os.path.join(LOCALES_DIR, filename)
            try:
                with open(filepath, "r", encoding="utf-8") as f:
                    TRANSLATIONS[lang_code] = json.load(f)
                logger.debug(f"Loaded translations for language: {lang_code}")
            except Exception as e:
                logger.error(f"Failed to load translation file {filename}: {e}")


_load_translations()


def _get_nested_value(d: dict, keys: list[str]):
    for key in keys:
        if isinstance(d, dict) and key in d:
            d = d[key]
        else:
            return None
    return d


def get_text(locale: discord.Locale | str | None, key: str, **kwargs):
    """Gets the text for a given language.

    If the language does not exist or the key is missing, it uses English (en).
    """
    lang = str(locale)
    if lang not in TRANSLATIONS:
        lang = "en"
    key_parts = key.split(".")

    text = _get_nested_value(TRANSLATIONS.get(lang, {}), key_parts)
    if text is None and lang != "en":
        text = _get_nested_value(TRANSLATIONS.get("en", {}), key_parts)

    if text is None:
        return key

    # Formatting strings with variables (if specified)
    if kwargs and isinstance(text, str):
        try:
            return text.format(**kwargs)
        except (KeyError, ValueError):
            logger.error(
                f"Failed to format translation for key '{key}' in locale '{lang}'. \n"
                f"Text: {text}, kwargs: {kwargs}"
            )

    return text
