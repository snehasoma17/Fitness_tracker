import streamlit as st
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import ai_helper
from pypdf import PdfReader
from io import BytesIO
from utils.theme import load_css
from utils.i18n import t

load_css()
st.set_page_config(page_title="AI Health Coach", page_icon="🤖", layout="wide")
try:
    with open("data/style.css") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
except Exception:
    pass

username = st.session_state.get("username", "")
if not username:
    st.warning("🔒 Please login from the main page."); st.stop()

ai_helper.render_ai_sidebar()

# ── Helpers ────────────────────────────────────────────────────────────────────
def extract_pdf_text(file_bytes: bytes) -> str:
    try:
        reader = PdfReader(BytesIO(file_bytes))
        return "\n".join(p.extract_text() or "" for p in reader.pages).strip()
    except Exception as e:
        return f"Error reading PDF: {e}"

def upload_section(key: str, label: str, desc: str) -> tuple:
    """Renders a styled upload box. Returns (file_bytes, file_ext, image_description)."""
    st.markdown(f"""
    <div class="upload-card">
        <span class="upload-icon">📂</span>
        <div style="color:#a5b4fc;font-weight:600;margin-bottom:4px;">{label}</div>
        <p>{desc}</p>
    </div>
    """, unsafe_allow_html=True)
    uploaded = st.file_uploader(
        "Choose file", type=["png","jpg","jpeg","pdf"],
        key=key, label_visibility="collapsed"
    )
    if not uploaded:
        return None, None, ""

    ext = uploaded.name.rsplit(".", 1)[-1].lower()
    file_bytes = uploaded.read()

    if ext in ("png","jpg","jpeg"):
        st.image(BytesIO(file_bytes), caption=f"📸 {uploaded.name}", use_container_width="stretch")
        desc_txt = st.text_area(
            "📝 Describe the image (if no vision model)",
            placeholder="e.g. A plate with grilled salmon, brown rice, and broccoli.",
            key=f"{key}_desc", height=80
        )
        return file_bytes, ext, desc_txt
    else:
        st.success(f"📄 **{uploaded.name}** uploaded successfully")
        return file_bytes, "pdf", ""

def run_ai(prompt: str, sys_prompt: str, file_bytes=None, ext=None, img_desc=""):
    """Build context from file + text, then call ai_helper."""
    context = ""
    images  = None

    if file_bytes and ext == "pdf":
        text = extract_pdf_text(file_bytes)
        context = f"\n\n--- Extracted Document Content ---\n{text[:4000]}\n"
    elif file_bytes and ext in ("png","jpg","jpeg"):
        # Try sending as vision image (Ollama only natively supports this)
        if st.session_state.get("ai_provider") == "ollama":
            images = [file_bytes]
        elif img_desc:
            context = f"\n\n--- Image Description ---\n{img_desc}\n"
        else:
            context = "\n\n[User uploaded an image but no vision model is active. Ask them to describe it.]"

    full_prompt = prompt + context
    return ai_helper.get_ai_response(full_prompt, sys_prompt, max_tokens=1800, images=images)


# ── Page Header ────────────────────────────────────────────────────────────────

provider = st.session_state.get("ai_provider", "OpenAI")
model = st.session_state.get("ai_model", "gpt-4o-mini")

st.markdown(
    f"""
    <div style="
        padding:8px;
        border-radius:10px;
        border:1px solid #444;
        margin-top:10px;">
        Provider: {provider}<br>
        Model: {model}
    </div>
    """,
    unsafe_allow_html=True
)

# ── Tabs ───────────────────────────────────────────────────────────────────────
tab1, tab2, tab3, tab4 = st.tabs([
    "🥗 Diet & Nutrition",
    "🏋️ Workout Coach",
    "📊 Health Report",
    "💬 Ask Anything",
])

# ═══════════════════════════════════════════════════════════════════
#  TAB 1 — DIET & NUTRITION
# ═══════════════════════════════════════════════════════════════════
with tab1:
    st.markdown('<div class="section-header"><span class="icon">🥗</span> Meal Analysis & Nutrition Advice</div>',
                unsafe_allow_html=True)

    left, right = st.columns([1, 1])

    with left:
        fb, ext, img_d = upload_section(
            "diet_upload",
            "Upload Meal Photo or Diet PDF",
            "Supported: JPG, PNG (meal photos), PDF (diet plans, recipes, menus)"
        )
        diet_q = st.text_area("💬 What do you want to know?",
                              placeholder="e.g. Is this meal suitable for weight loss? How can I add more protein?",
                              key="diet_q", height=100)
        goal_hint = st.selectbox("🎯 My current goal", ["Weight Loss","Muscle Gain","Maintain","Not sure"],
                                  key="diet_goal")

    with right:
        st.markdown("""
        <div class="info-card" style="padding:24px;">
            <div class="info-label">💡 What the AI analyses</div><br>
            <ul style="color:#94a3b8;font-size:0.88rem;line-height:2.1;padding-left:16px;margin:0;">
                <li>Calorie &amp; macro estimate (protein / carbs / fat)</li>
                <li>Nutritional pros and cons of the meal</li>
                <li>3 actionable improvements for your goal</li>
                <li>Hydration &amp; portion-size advice</li>
                <li>Full PDF diet-plan critique</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)

    if st.button("🚀 Analyse Meal / Diet", type="primary", key="diet_btn"):
        if not fb and not diet_q.strip():
            st.error("Please upload a file or type a question.")
        else:
            with st.spinner("AI is analysing your nutrition…"):
                try:
                    prompt = (
                        f"Goal: {goal_hint}\nQuestion: {diet_q}\n"
                        f"{'Image desc: ' + img_d if img_d else ''}"
                    )
                    sys_p = (
                        "You are a certified sports nutritionist and dietitian. "
                        "Analyse the meal/diet provided. Structure your response with bold section titles:\n"
                        "**🔢 Nutrition Estimate** | **✅ What's Great** | **⚠️ What to Improve** | "
                        "**💡 3 Actionable Tips** | **💧 Hydration & Portion Advice**\n"
                        "Be encouraging, practical, and science-backed."
                    )
                    result = run_ai(prompt, sys_p, fb, ext, img_d)
                    st.markdown(f'<div style="margin-top:6px;">{ai_helper.provider_badge()}</div>',
                                unsafe_allow_html=True)
                    st.markdown("### 📋 AI Nutritionist Report")
                    st.write(result)
                except Exception as e:
                    st.error(f"AI Error: {e}")

# ═══════════════════════════════════════════════════════════════════
#  TAB 2 — WORKOUT COACH
# ═══════════════════════════════════════════════════════════════════
with tab2:
    st.markdown('<div class="section-header"><span class="icon">🏋️</span> Workout Review & Training Plan</div>',
                unsafe_allow_html=True)

    left, right = st.columns([1, 1])

    with left:
        wfb, wext, wimg_d = upload_section(
            "workout_upload",
            "Upload Workout Log or Routine PDF",
            "Supported: JPG, PNG (gym log photos), PDF (training programmes)"
        )
        workout_q   = st.text_area("💬 What coaching do you need?",
                                   placeholder="e.g. Is this enough volume for hypertrophy? Help me break my bench press plateau.",
                                   key="workout_q", height=100)
        w_goal      = st.selectbox("🎯 Training goal", ["Muscle Gain","Weight Loss","Strength","Endurance","General Fitness"],
                                   key="w_goal")
        w_days      = st.slider("📅 Available training days / week", 2, 7, 4, key="w_days")
        w_level     = st.selectbox("🏅 Experience level", ["Beginner","Intermediate","Advanced"], key="w_level")

    with right:
        st.markdown("""
        <div class="info-card" style="padding:24px;">
            <div class="info-label">💡 What the AI reviews</div><br>
            <ul style="color:#94a3b8;font-size:0.88rem;line-height:2.1;padding-left:16px;margin:0;">
                <li>Push/pull/leg balance &amp; muscle-group coverage</li>
                <li>Sets, reps &amp; progressive overload critique</li>
                <li>Cardio integration suggestions</li>
                <li>Recovery &amp; injury-prevention advice</li>
                <li>Optimised weekly schedule</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)

    if st.button("🚀 Get Coaching Feedback", type="primary", key="workout_btn"):
        if not wfb and not workout_q.strip():
            st.error("Please upload a file or type a question.")
        else:
            with st.spinner("AI coach is reviewing your training…"):
                try:
                    prompt = (
                        f"Goal: {w_goal} | Level: {w_level} | Days/week: {w_days}\n"
                        f"Question: {workout_q}\n"
                        f"{'Image desc: ' + wimg_d if wimg_d else ''}"
                    )
                    sys_p = (
                        "You are a professional strength & conditioning coach. "
                        "Analyse the workout programme. Structure your response with bold titles:\n"
                        "**📊 Routine Critique** | **📈 Volume & Intensity** | "
                        "**🔄 Progressive Overload Tips** | **🛡️ Recovery & Injury Prevention** | "
                        "**📅 Optimised Weekly Schedule**\n"
                        "Be specific, motivating, and evidence-based."
                    )
                    result = run_ai(prompt, sys_p, wfb, wext, wimg_d)
                    st.markdown(f'<div style="margin-top:6px;">{ai_helper.provider_badge()}</div>',
                                unsafe_allow_html=True)
                    st.markdown("### 📋 AI Coach Feedback")
                    st.write(result)
                except Exception as e:
                    st.error(f"AI Error: {e}")

# ═══════════════════════════════════════════════════════════════════
#  TAB 3 — HEALTH REPORT
# ═══════════════════════════════════════════════════════════════════
with tab3:
    st.markdown('<div class="section-header"><span class="icon">📊</span> Health Report & Wellness Analysis</div>',
                unsafe_allow_html=True)
    st.warning("⚠️ **Disclaimer:** This is for educational purposes only and is NOT medical advice. Always consult a qualified healthcare professional.")

    left, right = st.columns([1, 1])

    with left:
        rfb, rext, rimg_d = upload_section(
            "report_upload",
            "Upload Health Report or Body Scan",
            "Supported: JPG, PNG (InBody/lab report photos), PDF (blood work, health checkups)"
        )
        report_q    = st.text_area("💬 What wellness goal do you have?",
                                   placeholder="e.g. Improve energy levels, lower stress, better sleep quality.",
                                   key="report_q", height=100)
        manual_data = st.text_area("📝 Key metrics (optional, if no file)",
                                   placeholder="e.g. Cholesterol: 220 mg/dL, Body fat: 28%, Vitamin D: 25 ng/mL",
                                   key="manual_data", height=80)

    with right:
        st.markdown("""
        <div class="info-card" style="padding:24px;">
            <div class="info-label">💡 What the AI reviews</div><br>
            <ul style="color:#94a3b8;font-size:0.88rem;line-height:2.1;padding-left:16px;margin:0;">
                <li>Metrics summary &amp; what they mean</li>
                <li>Lifestyle impact on energy, sleep &amp; stamina</li>
                <li>Diet, hydration &amp; activity adjustments</li>
                <li>Sleep hygiene &amp; stress management tips</li>
                <li>Recommended next steps &amp; follow-ups</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)

    if st.button("🚀 Analyse Report", type="primary", key="report_btn"):
        if not rfb and not report_q.strip() and not manual_data.strip():
            st.error("Please upload a file, enter metrics, or type a question.")
        else:
            with st.spinner("AI is analysing your health data…"):
                try:
                    prompt = (
                        f"Goal: {report_q}\n"
                        f"{'Manual metrics: ' + manual_data + chr(10) if manual_data else ''}"
                        f"{'Image desc: ' + rimg_d if rimg_d else ''}"
                    )
                    sys_p = (
                        "You are a holistic wellness coach (NOT a medical doctor). "
                        "Begin with a clear disclaimer. Then analyse the health data. "
                        "Structure response with bold titles:\n"
                        "**⚠️ Disclaimer** | **📊 Metrics Summary** | "
                        "**💥 Lifestyle Impact** | **🌿 Habits & Routine Advice** | "
                        "**✅ Recommended Next Steps**\n"
                        "Keep tone positive, encouraging, and professional."
                    )
                    result = run_ai(prompt, sys_p, rfb, rext, rimg_d)
                    st.markdown(f'<div style="margin-top:6px;">{ai_helper.provider_badge()}</div>',
                                unsafe_allow_html=True)
                    st.markdown("### 📋 AI Wellness Report")
                    st.write(result)
                except Exception as e:
                    st.error(f"AI Error: {e}")

# ═══════════════════════════════════════════════════════════════════
#  TAB 4 — CONVERSATIONAL Q&A
# ═══════════════════════════════════════════════════════════════════
with tab4:
    st.markdown('<div class="section-header"><span class="icon">💬</span> Ask Your AI Fitness Coach Anything</div>',
                unsafe_allow_html=True)

    # Example quick questions
    st.markdown("**💡 Quick starters:**")
    qcols = st.columns(3)
    starters = [
        "What should I eat post-workout?",
        "How do I calculate my TDEE?",
        "Best exercises for lower back pain?",
        "How many rest days per week?",
        "What is progressive overload?",
        "How to improve sleep quality?",
    ]
    starter_clicked = None
    for i, q in enumerate(starters):
        with qcols[i % 3]:
            if st.button(q, key=f"starter_{i}", use_container_width="stretch"):
                starter_clicked = q

    st.write("")

    chat_q = st.text_area(
        "✍️ Your question:",
        value=starter_clicked if starter_clicked else "",
        placeholder="e.g. What is the difference between active and passive recovery?",
        height=110,
        key="chat_q"
    )

    c1, c2 = st.columns([1, 3])
    with c1:
        if st.button("💬 Ask Coach", type="primary", key="chat_btn", use_container_width="stretch"):
            if not chat_q.strip():
                st.error("Please enter a question.")
            else:
                with st.spinner("AI Coach is thinking…"):
                    try:
                        sys_p = (
                            "You are an expert personal trainer, nutritionist, and wellness coach. "
                            "Give a comprehensive, friendly, and scientifically accurate answer. "
                            "Use bold headings, bullet points, and emojis to make the response easy to read."
                        )
                        result = ai_helper.get_ai_response(chat_q, sys_p, max_tokens=1800)
                        st.markdown(f'<div style="margin-top:6px;">{ai_helper.provider_badge()}</div>',
                                    unsafe_allow_html=True)
                        st.markdown("### 💬 AI Coach Response")
                        st.write(result)
                    except Exception as e:
                        st.error(f"AI Error: {e}")