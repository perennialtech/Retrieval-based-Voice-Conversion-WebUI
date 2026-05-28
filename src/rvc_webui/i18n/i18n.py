import json
import locale
import os
from importlib.resources import files

from rvc_webui.config import Singleton


def load_language_list(language):
    path = files("rvc_webui.i18n").joinpath("locale", f"{language}.json")
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


class I18nAuto(metaclass=Singleton):
    def __init__(self, language=None):
        if language in ["Auto", None]:
            language = locale.getdefaultlocale(
                envvars=("LANG", "LC_ALL", "LC_CTYPE", "LANGUAGE")
            )[0]

        if not files("rvc_webui.i18n").joinpath(f"locale/{language}.json").is_file():
            language = "en_US"
        self.language = language
        self.language_map = load_language_list(language)

    def __call__(self, key):
        return self.language_map.get(key, key)

    def __repr__(self):
        return "Language: " + self.language
