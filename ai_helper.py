import streamlit as st
from openai import OpenAI

# --------------------------------------------------
# PROVIDERS
# --------------------------------------------------

PROVIDERS = {
    "🤖 OpenAI": "openai",
    "⚡ Groq": "groq",
    "💎 Gemini": "gemini",
}

MODEL_OPTIONS = {
    "openai": ["gpt-4o-mini"],
    "groq": ["llama3-8b-8192"],
    "gemini": ["gemini-1.5-flash"],
}


# --------------------------------------------------
# INIT SESSION STATE
# --------------------------------------------------

def _init_ai_state():
    defaults = {
        "ai_provider": "openai",
        "ai_model": "gpt-4o-mini",
        "api_key": "",
    }

    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v


# --------------------------------------------------
# SIDEBAR
# --------------------------------------------------

def render_ai_sidebar():
    _init_ai_state()

    st.sidebar.markdown("## ⚙️ AI Settings")

    provider_display = st.sidebar.selectbox(
        "Provider",
        list(PROVIDERS.keys())
    )

    provider = PROVIDERS[provider_display]
    st.session_state["ai_provider"] = provider

    models = MODEL_OPTIONS[provider]

    st.session_state["ai_model"] = st.sidebar.selectbox(
        "Model",
        models
    )

    st.session_state["api_key"] = st.sidebar.text_input(
        "API Key",
        type="password"
    )


# --------------------------------------------------
# AI RESPONSE
# --------------------------------------------------

def get_ai_response(
    prompt,
    system_prompt="You are a fitness coach",
    max_tokens=1000
):
    _init_ai_state()

    provider = st.session_state["ai_provider"]
    model = st.session_state["ai_model"]
    api_key = st.session_state["api_key"]

    if not api_key:
        return "Please enter an API key in the sidebar."

    try:

        if provider == "groq":
            client = OpenAI(
                api_key=api_key,
                base_url="https://api.groq.com/openai/v1"
            )

        elif provider == "gemini":
            client = OpenAI(
                api_key=api_key,
                base_url="https://generativelanguage.googleapis.com/v1beta/openai/"
            )

        else:
            client = OpenAI(api_key=api_key)

        response = client.chat.completions.create(
            model=model,
            messages=[
                {
                    "role": "system",
                    "content": system_prompt
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            max_tokens=max_tokens,
        )

        return response.choices[0].message.content

    except Exception as e:
        return f"AI Error: {e}"


# --------------------------------------------------
# STREAMING FALLBACK
# --------------------------------------------------

def stream_ai_response(
    prompt,
    system_prompt="You are a fitness coach"
):
    yield get_ai_response(prompt, system_prompt)


# --------------------------------------------------
# PROVIDER BADGE
# --------------------------------------------------

def provider_badge():
    _init_ai_state()

    return f"""
    <div style="
        padding:8px;
        border-radius:10px;
        border:1px solid #444;
        margin-top:10px;">
        Provider: {st.session_state['ai_provider']}<br>
        Model: {st.session_state['ai_model']}
    </div>
    """