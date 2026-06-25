import base64

import requests
import streamlit as st

# Optional imports
try:
    import ollama
except Exception:
    ollama = None

# ==========================================
# PROVIDERS
# ==========================================
PROVIDERS = {
    "🦙 Ollama (Local)": "ollama",
    "🤖 OpenAI": "openai",
    "⚡ Groq": "groq",
    "💎 Gemini": "gemini",
}

MODEL_OPTIONS = {
    "ollama": [
        "llama3.2",
        "llama3",
        "mistral",
        "gemma3",
        "qwen3",
        "llava",  # Vision model — can analyse food/body photos
        "llava:7b",
        "llava:13b",
        "llava:34b",
    ],
    "openai": [
        "gpt-4o-mini",
        "gpt-4o",
    ],
    "groq": [
        "llama-3.3-70b-versatile",
        "llama3-8b-8192",
        "mixtral-8x7b-32768",
    ],
    "gemini": [
        "gemini-1.5-flash",
        "gemini-1.5-pro",
        "gemini-2.0-flash-exp",
    ],
}


# ==========================================
# INIT SESSION STATE
# ==========================================
def _init_ai_state():
    if "ai_provider" not in st.session_state:
        st.session_state.ai_provider = "ollama"
    if "ai_model" not in st.session_state:
        st.session_state.ai_model = "llama3.2"
    if "api_key" not in st.session_state:
        st.session_state.api_key = ""


# ==========================================
# SIDEBAR
# ==========================================
def render_ai_sidebar():
    _init_ai_state()
    from utils.i18n import t

    st.sidebar.markdown(f"## ⚙️ {t('ai_settings')}")

    # Map displayed keys back to technical values
    inv_providers = {v: k for k, v in PROVIDERS.items()}
    current_prov_display = inv_providers.get(st.session_state.ai_provider, "🦙 Ollama (Local)")

    provider_display = st.sidebar.selectbox(
        t("provider"),
        options=list(PROVIDERS.keys()),
        index=list(PROVIDERS.keys()).index(current_prov_display)
        if current_prov_display in PROVIDERS
        else 0,
    )

    provider = PROVIDERS[provider_display]
    st.session_state.ai_provider = provider

    models = MODEL_OPTIONS[provider]
    current_model = st.session_state.ai_model
    if current_model not in models:
        current_model = models[0]

    selected_model = st.sidebar.selectbox(
        t("model"),
        options=models,
        index=models.index(current_model) if current_model in models else 0,
    )
    st.session_state.ai_model = selected_model

    # BYOK Inputs for cloud APIs
    if provider in ["openai", "groq", "gemini"]:
        st.session_state.api_key = st.sidebar.text_input(
            t("api_key"),
            type="password",
            value=st.session_state.api_key,
            placeholder="sk-..." if provider != "gemini" else "AIzaSy...",
        )
        if not st.session_state.api_key:
            st.sidebar.warning("⚠️ Please provide an API key for " + provider_display)

    st.sidebar.success(f"{t('active_model_desc')}: {selected_model}")


# ==========================================
# PROVIDER BADGE
# ==========================================
def provider_badge():
    provider = st.session_state.get("ai_provider", "ollama")
    model = st.session_state.get("ai_model", "llama3.2")
    return f"""
    <div style="
        display: inline-block;
        padding: 4px 8px;
        background-color: rgba(99, 102, 241, 0.15);
        color: #a5b4fc;
        border: 1px solid rgba(99, 102, 241, 0.3);
        border-radius: 6px;
        font-size: 0.75rem;
        font-weight: 600;
        margin-bottom: 12px;
    ">
        ⚡ Powered by {provider.upper()} ({model})
    </div>
    """


# ==========================================
# AI RESPONSE GENERATION (OLLAMA & BYOK)
# ==========================================
def get_ai_response(prompt, system_prompt=None, max_tokens=1000, images=None):
    _init_ai_state()
    provider = st.session_state.ai_provider
    model = st.session_state.ai_model
    api_key = st.session_state.api_key
    lang = st.session_state.get("current_language", "English")

    # Localize prompt by instructing LLM to respond in selected language
    if lang != "English":
        prompt += f"\n\nIMPORTANT: Please respond entirely in the {lang} language. All greetings, headings, explanations, and advice must be in {lang}."

    if not system_prompt:
        system_prompt = (
            "You are a helpful and professional personal trainer, nutritionist, and health coach."
        )

    try:
        # ---- 1. OLLAMA (LOCAL) ----
        if provider == "ollama":
            # Attempt to use local library, else fallback to direct requests
            try:
                msg = {"role": "user", "content": prompt}
                if images and isinstance(images, list):
                    # ollama package accepts bytes directly
                    msg["images"] = images

                messages = []
                if system_prompt:
                    messages.append({"role": "system", "content": system_prompt})
                messages.append(msg)

                response = ollama.chat(model=model, messages=messages)
                return response["message"]["content"]
            except Exception:
                # HTTP Fallback for Ollama API
                url = "http://localhost:11434/api/chat"
                msg = {"role": "user", "content": prompt}
                if images and isinstance(images, list):
                    # REST endpoint expects base64 encoded strings
                    msg["images"] = [base64.b64encode(img).decode("utf-8") for img in images]

                messages = []
                if system_prompt:
                    messages.append({"role": "system", "content": system_prompt})
                messages.append(msg)

                payload = {"model": model, "messages": messages, "stream": False}
                res = requests.post(url, json=payload, timeout=60)
                if res.status_code == 200:
                    return res.json()["message"]["content"]
                else:
                    return f"❌ Ollama Connection Error: Ensure Ollama is running locally at http://localhost:11434. ({res.status_code})"

        # Verify API key for commercial BYOK APIs
        if not api_key:
            return "❌ API Key Missing: Please provide an API key in the sidebar configuration."

        # ---- 2. OPENAI (BYOK) ----
        if provider == "openai":
            headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
            messages = [{"role": "system", "content": system_prompt}]

            if images and isinstance(images, list):
                content = [{"type": "text", "text": prompt}]
                for img in images:
                    b64_img = base64.b64encode(img).decode("utf-8")
                    content.append(
                        {
                            "type": "image_url",
                            "image_url": {"url": f"data:image/jpeg;base64,{b64_img}"},
                        }
                    )
                messages.append({"role": "user", "content": content})
            else:
                messages.append({"role": "user", "content": prompt})

            payload = {
                "model": model,
                "messages": messages,
                "max_tokens": max_tokens,
                "temperature": 0.7,
            }
            res = requests.post(
                "https://api.openai.com/v1/chat/completions",
                headers=headers,
                json=payload,
                timeout=60,
            )
            if res.status_code == 200:
                return res.json()["choices"][0]["message"]["content"]
            else:
                return f"❌ OpenAI Error {res.status_code}: {res.text}"

        # ---- 3. GROQ (BYOK) ----
        if provider == "groq":
            headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": prompt},
            ]
            payload = {
                "model": model,
                "messages": messages,
                "max_tokens": max_tokens,
                "temperature": 0.7,
            }
            res = requests.post(
                "https://api.groq.com/openai/v1/chat/completions",
                headers=headers,
                json=payload,
                timeout=60,
            )
            if res.status_code == 200:
                return res.json()["choices"][0]["message"]["content"]
            else:
                return f"❌ Groq Error {res.status_code}: {res.text}"

        # ---- 4. GEMINI (BYOK) ----
        if provider == "gemini":
            # Map model names to technical model names if necessary
            # e.g., gemini-1.5-flash -> gemini-1.5-flash
            url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={api_key}"

            parts = [{"text": prompt}]
            if images and isinstance(images, list):
                for img in images:
                    b64_img = base64.b64encode(img).decode("utf-8")
                    parts.append({"inlineData": {"mimeType": "image/jpeg", "data": b64_img}})

            payload = {
                "contents": [{"role": "user", "parts": parts}],
                "generationConfig": {"maxOutputTokens": max_tokens, "temperature": 0.7},
            }
            if system_prompt:
                payload["systemInstruction"] = {"parts": [{"text": system_prompt}]}

            res = requests.post(url, json=payload, timeout=60)
            if res.status_code == 200:
                return res.json()["candidates"][0]["content"]["parts"][0]["text"]
            else:
                return f"❌ Gemini Error {res.status_code}: {res.text}"

        return "❌ Unsupported AI Provider"

    except Exception as e:
        return f"❌ AI Execution Error: {str(e)}"


# ==========================================
# STREAMING COMPATIBILITY LAYER
# ==========================================
def stream_ai_response(prompt, system_prompt=None, max_tokens=1000):
    # Streaming simulator over HTTP response
    response = get_ai_response(prompt, system_prompt, max_tokens)
    for word in response.split(" "):
        yield word + " "


# ==========================================
# FOOD IMAGE ANALYZER
# ==========================================
def analyze_food_image(image_bytes):
    sys_p = "You are a professional nutrition analyzer. Identify the food item, estimate calories and macronutrients (Protein, Carbs, Fat) in a structured breakdown."
    prompt = "Analyze this food image. Provide a detailed summary."
    return get_ai_response(prompt, system_prompt=sys_p, images=[image_bytes])
