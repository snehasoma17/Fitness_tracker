import streamlit as st
import json

# -----------------------------
# LANGUAGE MAP (GLOBAL)
# -----------------------------
LANGUAGES = {
    "English": "en",
    "Hindi": "hi"
}

# -----------------------------
# LOAD TRANSLATIONS
# -----------------------------
def load_translations(lang_code):
    try:
        with open(f"pages/i18n/{lang_code}.json", "r", encoding="utf-8") as f:
            return json.load(f)
    except:
        return {}

# -----------------------------
# TRANSLATION FUNCTION
# -----------------------------
def t(key):
    lang = st.session_state.get("current_language", "English")
    lang_code = LANGUAGES.get(lang, "en")

    translations = load_translations(lang_code)
    return translations.get(key, key)