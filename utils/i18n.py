import i18n
import os
import discord

LOCALES_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "locales")

i18n.load_path.append(LOCALES_DIR)
i18n.set("file_format", "json")
i18n.set("filename_format", "{locale}.{format}")
i18n.set("fallback", "en")
i18n.set("skip_locale_root_data", True)


def get_text(locale: discord.Locale | str | None, key: str, **kwargs):
    """Gets the text for a given language.

    If the language does not exist or the key is missing, it uses English (en).
    """
    lang = str(locale) if locale else "en"
    return i18n.t(key, locale=lang, **kwargs)
