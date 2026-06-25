import json

import streamlit as st

# -----------------------------
# LANGUAGE MAP
# -----------------------------
LANGUAGES = {"English": "en", "Hindi": "hi", "Telugu": "te", "Tamil": "ta"}


# -----------------------------
# CACHE TRANSLATIONS (IMPORTANT FIX)
# -----------------------------
@st.cache_data
def load_translations(lang_code):
    try:
        with open(f"pages/i18n/{lang_code}.json", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}


# -----------------------------
# TRANSLATION FUNCTION
# -----------------------------
def t(key):
    lang = st.session_state.get("current_language", "English")
    lang_code = LANGUAGES.get(lang, "en")

    translations = load_translations(lang_code)

    return translations.get(key, key)
