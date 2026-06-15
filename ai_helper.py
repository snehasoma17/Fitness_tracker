import streamlit as st
from openai import OpenAI
import ollama

# ==========================================
# PROVIDERS
# ==========================================

PROVIDERS = {
    "🦙 Ollama": "ollama",
    "🤖 OpenAI": "openai",
    "⚡ Groq": "groq",
    "💎 Gemini": "gemini",
}

MODEL_OPTIONS = {
    "ollama": [
        "llama3",
        "llama3:8b",
        "llava",
        "mistral",
        "gemma3",
        "qwen3",
        "deepseek-r1",
        "codellama",
    ],
    "openai": ["gpt-4o-mini"],
    "groq": [
        "llama3-8b-8192",
        "llama3-70b-8192",
        "mixtral-8x7b-32768"
    ],
    "gemini": [
        "gemini-1.5-flash",
        "gemini-1.5-pro"
    ],
}

# ==========================================
# INIT STATE
# ==========================================

def _init_ai_state():
    if "ai_provider" not in st.session_state:
        st.session_state.ai_provider = "ollama"

    if "ai_model" not in st.session_state:
        st.session_state.ai_model = "llama3"

    if "api_key" not in st.session_state:
        st.session_state.api_key = ""

# ==========================================
# SIDEBAR UI
# ==========================================

def render_ai_sidebar():
    _init_ai_state()

    st.sidebar.markdown("## ⚙️ AI Settings")

    provider_display = st.sidebar.selectbox(
        "Provider",
        list(PROVIDERS.keys()),
        key="provider_select"
    )

    provider = PROVIDERS[provider_display]
    st.session_state.ai