# utils/translator.py

from deep_translator import GoogleTranslator

class Translator:
    def __init__(self, target_lang="en"):
        self.target_lang = target_lang

    def set_language(self, lang):
        self.target_lang = lang

    def translate(self, text, source_lang="auto"):
        try:
            translated = GoogleTranslator(
                source=source_lang,
                target=self.target_lang
            ).translate(text)
            return translated
        except Exception as e:
            return f"Translation error: {str(e)}"