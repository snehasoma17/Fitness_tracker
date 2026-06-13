"""
ai_helper.py — Central AI Routing Module for AI Fitness Tracker

Supports:
  • Ollama  (Local)
  • OpenAI  (BYOK)
  • Groq    (BYOK)
  • Gemini  (BYOK)
  • Streaming responses (ChatGPT-style)
"""

import streamlit as st
#import ollama as _ollama
from openai import OpenAI

# ─────────────────────────────────────────────────────────────
# 🔥 GLOBAL CACHE (FAST RESPONSE FIX)
# ─────────────────────────────────────────────────────────────
AI_RESPONSE_CACHE = {}

# ─────────────────────────────────────────────────────────────
# Providers
# ─────────────────────────────────────────────────────────────

PROVIDERS = {
    "🖥️ Ollama": "ollama",
    "🤖 OpenAI": "openai",
    "⚡ Groq": "groq",
    "💎 Gemini": "gemini",
}

MODEL_OPTIONS = {
    "ollama": ["llama3.2", "llama3", "mistral", "phi3", "gemma2"],
    "openai": ["gpt-4o-mini", "gpt-4o"],
    "groq":   ["llama3-8b-8192", "mixtral-8x7b-32768"],
    "gemini": ["gemini-1.5-flash", "gemini-1.5-pro"],
}

# ─────────────────────────────────────────────────────────────
# INIT STATE
# ─────────────────────────────────────────────────────────────

def _init_ai_state():
    defaults = {
        "ai_provider": "ollama",
        "ai_model": "llama3.2",
        "api_key": "",
        "ollama_url": "http://localhost:11434",
    }

    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v


# ─────────────────────────────────────────────────────────────
# MAIN AI FUNCTION (NON-STREAMING)
# ─────────────────────────────────────────────────────────────

def get_ai_response(prompt, system_prompt="You are a fitness coach", max_tokens=1000):
    _init_ai_state()

    provider = st.session_state["ai_provider"]
    model = st.session_state["ai_model"]

    cache_key = f"{provider}|{model}|{prompt}"

    # 🔥 CACHE HIT
    if cache_key in AI_RESPONSE_CACHE:
        return AI_RESPONSE_CACHE[cache_key]

    result = ""

    # ── OLLAMA ─────────────────────────────
    if provider == "ollama":
        response = _ollama.chat(
            model=model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": prompt},
            ],
            options={"num_predict": 400}
        )
        result = response["message"]["content"]

    # ── OPENAI ─────────────────────────────
    elif provider == "openai":
        api_key = st.session_state["api_key"].strip()
        client = OpenAI(api_key=api_key)

        resp = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": prompt},
            ],
            max_tokens=max_tokens,
        )
        result = resp.choices[0].message.content

    # ── GROQ ─────────────────────────────
    elif provider == "groq":
        api_key = st.session_state["api_key"].strip()
        client = OpenAI(api_key=api_key, base_url="https://api.groq.com/openai/v1")

        resp = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": prompt},
            ],
            max_tokens=max_tokens,
        )
        result = resp.choices[0].message.content

    # ── GEMINI ─────────────────────────────
    elif provider == "gemini":
        api_key = st.session_state["api_key"].strip()
        client = OpenAI(
            api_key=api_key,
            base_url="https://generativelanguage.googleapis.com/v1beta/openai/"
        )

        resp = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": prompt},
            ],
            max_tokens=max_tokens,
        )
        result = resp.choices[0].message.content

    else:
        result = "Invalid provider"

    # 🔥 STORE CACHE
    AI_RESPONSE_CACHE[cache_key] = result
    return result


# ─────────────────────────────────────────────────────────────
# ⚡ STREAMING FUNCTION (CHATGPT TYPE EFFECT)
# ─────────────────────────────────────────────────────────────

def stream_ai_response(prompt, system_prompt="You are a fitness coach"):
    _init_ai_state()

    provider = st.session_state["ai_provider"]
    model = st.session_state["ai_model"]

    # ── OPENAI STREAM ─────────────────────
    if provider == "openai":
        api_key = st.session_state["api_key"].strip()
        client = OpenAI(api_key=api_key)

        stream = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": prompt},
            ],
            stream=True
        )

        for chunk in stream:
            token = chunk.choices[0].delta.content
            if token:
                yield token

    # ── OLLAMA STREAM ─────────────────────
    elif provider == "ollama":
        response = _ollama.chat(
            model=model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": prompt},
            ],
            stream=True
        )

        for chunk in response:
            yield chunk["message"]["content"]

    # ── OTHERS (NO STREAM SUPPORT) ────────
    else:
        yield get_ai_response(prompt, system_prompt)


# ─────────────────────────────────────────────────────────────
# DB MIGRATION HELPER
# ─────────────────────────────────────────────────────────────

def ensure_db_schema(conn):
    cursor = conn.cursor()

    migrations = [
        "ALTER TABLE workouts ADD COLUMN username TEXT",
        "ALTER TABLE meals ADD COLUMN username TEXT",
        "ALTER TABLE weight_log ADD COLUMN username TEXT",
    ]

    for sql in migrations:
        try:
            cursor.execute(sql)
            conn.commit()
        except:
            pass


# ─────────────────────────────────────────────────────────────
# UI BADGE
# ─────────────────────────────────────────────────────────────

def provider_badge():
    _init_ai_state()

    p = st.session_state["ai_provider"]
    m = st.session_state["ai_model"]

    colors = {
        "ollama": "#10b981",
        "openai": "#6366f1",
        "groq": "#f59e0b",
        "gemini": "#ec4899",
    }

    return f"""
    <span style="
        padding:4px 10px;
        border-radius:20px;
        border:1px solid {colors.get(p,'#999')};
        color:{colors.get(p,'#999')};
        font-size:12px;">
        {p} · {m}
    </span>
    """
    def render_ai_sidebar():
    _init_ai_state()

    st.sidebar.markdown("## ⚙️ AI Settings")

    provider_display = st.sidebar.selectbox(
        "Provider",
        list(PROVIDERS.keys()),
        index=list(PROVIDERS.values()).index(
            st.session_state["ai_provider"]
        )
    )

    provider = PROVIDERS[provider_display]
    st.session_state["ai_provider"] = provider

    models = MODEL_OPTIONS.get(provider, [])

    current_model = st.session_state.get("ai_model", models[0])

    if current_model not in models:
        current_model = models[0]

    st.session_state["ai_model"] = st.sidebar.selectbox(
        "Model",
        models,
        index=models.index(current_model)
    )

    if provider in ["openai", "groq", "gemini"]:
        st.session_state["api_key"] = st.sidebar.text_input(
            "API Key",
            value=st.session_state.get("api_key", ""),
            type="password"
        )

    if provider == "ollama":
        st.session_state["ollama_url"] = st.sidebar.text_input(
            "Ollama URL",
            value=st.session_state.get(
                "ollama_url",
                "http://localhost:11434"
            )
        )

    st.sidebar.markdown("---")
    st.sidebar.markdown(
        provider_badge(),
        unsafe_allow_html=True
    )