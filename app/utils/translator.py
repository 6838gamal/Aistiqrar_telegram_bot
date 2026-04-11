import json
from pathlib import Path

class Translator:
    def __init__(self):
        self.data = {
            "ar": self.load("ar"),
            "en": self.load("en")
        }

    def load(self, lang):
        path = Path(f"app/locales/{lang}.json")
        return json.loads(path.read_text(encoding="utf-8"))

    def t(self, key, lang="ar"):
        return self.data.get(lang, {}).get(key, key)

translator = Translator()
