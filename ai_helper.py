import streamlit as st
import ollama as _ollama
from openai import OpenAI
import base64

# ─────────────────────────────────────────────
# INIT STATE
# ─────────────────────────────────────────────
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


# ─────────────────────────────────────────────
# NORMAL AI RESPONSE
# ─────────────────────────────────────────────
def get_ai_response(
    prompt,
    system_prompt="You are a fitness coach",
    max_tokens=1000
):
    _init_ai_state()

    provider = st.session_state["ai_provider"]
    model = st.session_state["ai_model"]

    if provider == "ollama":

        res = _ollama.chat(
            model=model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": prompt},
            ]
        )

        return res["message"]["content"]

    elif provider == "openai":

        client = OpenAI(
            api_key=st.session_state["api_key"]
        )

        res = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": prompt},
            ],
            max_tokens=max_tokens
        )

        return res.choices[0].message.content

    return "Provider not supported"

# ─────────────────────────────────────────────
# STREAMING AI (CHAT)
# ─────────────────────────────────────────────
def stream_ai_response(
    prompt,
    system_prompt="You are a fitness coach"
):
    _init_ai_state()

    provider = st.session_state["ai_provider"]
    model = st.session_state["ai_model"]

    if provider == "openai":

        client = OpenAI(
            api_key=st.session_state["api_key"]
        )

        stream = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": prompt},
            ],
            stream=True,
        )

        for chunk in stream:
            token = chunk.choices[0].delta.content

            if token:
                yield token

    elif provider == "ollama":

        stream = _ollama.chat(
            model=model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": prompt},
            ],
            stream=True,
        )

        for chunk in stream:
            yield chunk["message"]["content"]

    else:
        yield get_ai_response(
            prompt,
            system_prompt
        )


# ─────────────────────────────────────────────
# 🍎 FOOD IMAGE ANALYZER (NEW FEATURE)
# ─────────────────────────────────────────────
def analyze_food_image(image_bytes):
    _init_ai_state()

    provider = st.session_state["ai_provider"]
    model = st.session_state["ai_model"]

    prompt = """
You are a professional nutrition AI coach.

Analyze this food image and return:

1. Food name(s)
2. Estimated calories
3. Protein / carbs / fats
4. Health score (out of 10)
5. Is it healthy or not (yes/no with reason)
6. Best time to eat it (morning/afternoon/night/post-workout)
7. Simple diet advice
"""

    # ───────── OLLAMA (LLAVA) ─────────
    if provider == "ollama":
        res = _ollama.chat(
            model=model,
            messages=[
                {
                    "role": "user",
                    "content": prompt,
                    "images": [image_bytes],
                }
            ],
        )
        return res["message"]["content"]

    # ───────── OPENAI VISION ─────────
    elif provider == "openai":
        client = OpenAI(api_key=st.session_state["api_key"])

        b64 = base64.b64encode(image_bytes).decode()

        res = client.chat.completions.create(
            model=model,
            messages=[
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": prompt},
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/png;base64,{b64}"
                            },
                        },
                    ],
                }
            ],
        )

        return res.choices[0].message.content

    else:
        return "This provider does not support image analysis."


# ─────────────────────────────────────────────
# PROVIDER BADGE
# ─────────────────────────────────────────────
def provider_badge():
    _init_ai_state()
    return f"🤖 {st.session_state['ai_provider']} | {st.session_state['ai_model']}"
    # ─────────────────────────────────────────────
# ─────────────────────────────────────────────
# AI SIDEBAR
# ─────────────────────────────────────────────

def render_ai_sidebar():

    _init_ai_state()

    st.sidebar.title("⚙️ AI Settings")

    provider = st.sidebar.selectbox(
        "AI Provider",
        ["ollama", "openai"],
        index=0 if st.session_state["ai_provider"] == "ollama" else 1
    )

    st.session_state["ai_provider"] = provider

    if provider == "ollama":

        st.session_state["ai_model"] = st.sidebar.selectbox(
            "Model",
            [
                "llama3.2",
                "mistral",
                "gemma2",
                "llava"
            ]
        )

        st.sidebar.success(
            "🖥️ Local AI Inference (Ollama)"
        )

    elif provider == "openai":

        api_key = st.sidebar.text_input(
    "OpenAI API Key",
    type="password",
    value=st.session_state["api_key"]
)