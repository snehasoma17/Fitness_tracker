import os
import sys

import streamlit as st

# Ensure the root directory is in the path so we can import ai_helper
root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if root_dir not in sys.path:
    sys.path.insert(0, root_dir)

import ai_helper  # noqa: E402
from utils.i18n import LANGUAGES, t  # noqa: E402
from utils.theme import load_css  # noqa: E402

# Language flag emojis for visual feedback
LANG_FLAGS = {
    "English": "🇬🇧",
    "Hindi": "🇮🇳",
    "Telugu": "🇮🇳",
    "Tamil": "🇮🇳",
}


def _on_language_change():
    """Called immediately when language selectbox changes — forces full rerun."""
    st.rerun()


def initialize_page(page_title: str, page_icon: str, check_login: bool = True):
    """
    Safely configures the Streamlit page layout and renders the common sidebar.
    - Calls st.set_page_config as the very first command (prevents crashes).
    - Renders a global Language selector that translates the ENTIRE app on one tap.
    - Renders the AI Provider/Model selector for Ollama and BYOK APIs.
    """
    # ── 1. Page config — must be the absolute first Streamlit call ──────────
    st.set_page_config(page_title=page_title, page_icon=page_icon, layout="wide")

    # ── 2. CSS Theme ─────────────────────────────────────────────────────────
    load_css()

    # ── 3. Initialize session state defaults ─────────────────────────────────
    if "current_language" not in st.session_state:
        st.session_state.current_language = "English"
    if "logged_in" not in st.session_state:
        st.session_state.logged_in = False
    if "username" not in st.session_state:
        st.session_state.username = ""

    # ── 4. Login gate ─────────────────────────────────────────────────────────
    if check_login and not st.session_state.logged_in:
        st.warning("🔒 " + t("please_login_warning"))
        st.stop()

    # ── 5. GLOBAL LANGUAGE SELECTOR ──────────────────────────────────────────
    #   Selecting a language here immediately reruns the entire page in the
    #   new language — exactly like Amazon / Flipkart one-tap language switch.
    # ─────────────────────────────────────────────────────────────────────────
    current_lang = st.session_state.current_language
    flag = LANG_FLAGS.get(current_lang, "🌐")

    st.sidebar.markdown(
        f"""
        <div style="
            background: linear-gradient(135deg,rgba(99,102,241,0.15),rgba(139,92,246,0.15));
            border: 1px solid rgba(99,102,241,0.3);
            border-radius: 12px;
            padding: 14px 16px;
            margin-bottom: 8px;
        ">
            <div style="color:#a5b4fc;font-size:0.75rem;font-weight:700;
                        letter-spacing:.08em;text-transform:uppercase;margin-bottom:6px;">
                🌐 {t('language')}
            </div>
            <div style="color:#e2e8f0;font-size:1.05rem;font-weight:600;">
                {flag} {current_lang}
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # The selectbox is the single source of truth for the whole app.
    # on_change fires BEFORE the rest of the page body runs, so every
    # widget and every t() call already sees the new language value.
    new_lang = st.sidebar.selectbox(
        "Switch language / भाषा / భాష / மொழி",
        options=list(LANGUAGES.keys()),
        index=list(LANGUAGES.keys()).index(current_lang),
        label_visibility="collapsed",
    )

    # If language changed → update session_state and rerun immediately
    if new_lang != current_lang:
        st.session_state.current_language = new_lang
        st.rerun()

    st.sidebar.markdown("---")

    # ── 6. Global AI Settings ─────────────────────────────────────────────────
    ai_helper.render_ai_sidebar()

    # ── 7. Sidebar footer — logged-in user badge ──────────────────────────────
    if st.session_state.logged_in and st.session_state.username:
        st.sidebar.markdown("---")
        st.sidebar.markdown(
            f"""
            <div style="
                text-align:center;
                padding: 10px;
                background:rgba(16,185,129,0.08);
                border:1px solid rgba(16,185,129,0.2);
                border-radius:10px;
                font-size:0.8rem;
                color:#6ee7b7;
            ">
                👤 <b>@{st.session_state.username}</b>
            </div>
            """,
            unsafe_allow_html=True,
        )
