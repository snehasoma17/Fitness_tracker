import os
import sys
from unittest.mock import MagicMock

# Ensure project root is in the path (must be done before local imports)
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import streamlit as st  # noqa: E402

# Mock streamlit session state before importing utils
st.session_state = MagicMock()
st.session_state.get.return_value = "English"

from utils.i18n import LANGUAGES, t  # noqa: E402


def test_languages_mapping():
    assert "English" in LANGUAGES
    assert "Hindi" in LANGUAGES
    assert "Telugu" in LANGUAGES
    assert "Tamil" in LANGUAGES


def test_translation_fallback():
    # Since session_state returns "English" and we test a dummy key
    assert t("invalid_dummy_key_123") == "invalid_dummy_key_123"


def test_translation_valid_key():
    # Mock to return "English"
    st.session_state.get.side_effect = lambda key, default=None: (
        "English" if key == "current_language" else default
    )
    assert t("app_title") == "AI Fitness Tracker"
