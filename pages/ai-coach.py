import os
import sys
from io import BytesIO

import streamlit as st
from pypdf import PdfReader

# Ensure the root directory is in the path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import ai_helper
from utils.i18n import t
from utils.navigation import initialize_page

# 1. Initialize Page and Shared Sidebar
initialize_page(t("ai_coach"), "🤖")

lang = st.session_state.current_language


# ── Helpers ────────────────────────────────────────────────────────────────────
def extract_pdf_text(file_bytes: bytes) -> str:
    try:
        reader = PdfReader(BytesIO(file_bytes))
        return "\n".join(p.extract_text() or "" for p in reader.pages).strip()
    except Exception as e:
        return f"Error reading PDF: {e}"


def upload_section(key: str, label: str, desc: str) -> tuple:
    """Renders a styled upload box. Returns (file_bytes, file_ext, image_description)."""
    st.markdown(
        f"""
    <div class="upload-card">
        <span class="upload-icon">📂</span>
        <div style="color:#a5b4fc;font-weight:600;margin-bottom:4px;">{label}</div>
        <p>{desc}</p>
    </div>
    """,
        unsafe_allow_html=True,
    )
    uploaded = st.file_uploader(
        "Choose file", type=["png", "jpg", "jpeg", "pdf"], key=key, label_visibility="collapsed"
    )
    if not uploaded:
        return None, None, ""

    ext = uploaded.name.rsplit(".", 1)[-1].lower()
    file_bytes = uploaded.read()

    if ext in ("png", "jpg", "jpeg"):
        st.image(BytesIO(file_bytes), caption=f"📸 {uploaded.name}", use_container_width=True)
        img_desc_lbl = (
            "📝 Describe the image (for non-vision model)"
            if lang == "English"
            else "📝 छवि का वर्णन करें (गैर-विजन मॉडल के लिए)"
            if lang == "Hindi"
            else "📝 చిత్రాన్ని వివరించండి (నాన్-విజన్ మోడల్ కోసం)"
            if lang == "Telugu"
            else "📝 படத்தின் விளக்கம் (விஷன் அல்லாத மாதிரிக்கு)"
        )
        desc_placeholder = (
            "e.g. A plate with grilled salmon, brown rice, and broccoli."
            if lang == "English"
            else "जैसे: ग्रील्ड सामन, ब्राउन राइस और ब्रोकोली वाली एक प्लेट।"
            if lang == "Hindi"
            else "ఉదా: గ్రిల్డ్ సాల్మన్, బ్రౌన్ రైస్ మరియు బ్రోకలీ ఉన్న ప్లేట్."
            if lang == "Telugu"
            else "எ.கா. வறுத்த சால்மன், பழுப்பு அரிசி மற்றும் ப்ரோக்கோலி கொண்ட தட்டு."
        )

        desc_txt = st.text_area(
            img_desc_lbl, placeholder=desc_placeholder, key=f"{key}_desc", height=80
        )
        return file_bytes, ext, desc_txt
    else:
        st.success(f"📄 **{uploaded.name}** upload success!")
        return file_bytes, "pdf", ""


def run_ai(prompt: str, sys_prompt: str, file_bytes=None, ext=None, img_desc=""):
    """Build context from file + text, then call ai_helper."""
    context = ""
    images = None

    if file_bytes and ext == "pdf":
        text = extract_pdf_text(file_bytes)
        context = f"\n\n--- Extracted Document Content ---\n{text[:4000]}\n"
    elif file_bytes and ext in ("png", "jpg", "jpeg"):
        images = [file_bytes]
        if img_desc:
            context = f"\n\n--- Image Description ---\n{img_desc}\n"

    full_prompt = prompt + context
    return ai_helper.get_ai_response(full_prompt, sys_prompt, max_tokens=1800, images=images)


# ── Page Header ────────────────────────────────────────────────
provider = st.session_state.ai_provider
model = st.session_state.ai_model

st.markdown(ai_helper.provider_badge(), unsafe_allow_html=True)

# ── Tabs ───────────────────────────────────────────────────────
tab1, tab2, tab3, tab4 = st.tabs(
    [
        "🥗 " + t("ai_diet_nutrition"),
        "🏋️ " + t("ai_workout_coach"),
        "📊 " + t("ai_health_report"),
        "💬 " + t("ai_ask_anything"),
    ]
)

# ═══════════════════════════════════════════════════════════════════
#  TAB 1 — DIET & NUTRITION
# ═══════════════════════════════════════════════════════════════════
with tab1:
    tab1_header = (
        "Meal Analysis & Nutrition Advice"
        if lang == "English"
        else "भोजन विश्लेषण और पोषण सलाह"
        if lang == "Hindi"
        else "భోజన విశ్లేషణ & పోషకాహార సలహా"
        if lang == "Telugu"
        else "உணவு பகுப்பாய்வு & ஊட்டச்சத்து ஆலோசனை"
    )
    st.markdown(
        f'<div class="section-header"><span class="icon">🥗</span> {tab1_header}</div>',
        unsafe_allow_html=True,
    )

    left, right = st.columns([1, 1])

    with left:
        upl_lbl = (
            "Upload Meal Photo or Diet PDF"
            if lang == "English"
            else "भोजन का फोटो या डाइट पीडीएफ अपलोड करें"
            if lang == "Hindi"
            else "భోజనం ఫోటో లేదా డైట్ పీడీఎఫ్ అప్‌లోడ్ చేయండి"
            if lang == "Telugu"
            else "உணவுப் படம் அல்லது உணவுத் திட்ட பிடிஎஃப்-ஐ பதிவேற்றவும்"
        )
        upl_desc = (
            "Supported: JPG, PNG, PDF (diet plans, recipes, menus)"
            if lang == "English"
            else "समर्थित: JPG, PNG, PDF (डाइट प्लान, रेसिपी, मेनू)"
            if lang == "Hindi"
            else "మద్దతు గలవి: JPG, PNG, PDF (డైట్ ప్లాన్లు, వంటకాలు, మెనూలు)"
            if lang == "Telugu"
            else "ஆதரிக்கப்படும் வடிவங்கள்: JPG, PNG, PDF (உணவுத் திட்டங்கள், சமையல் குறிப்புகள்)"
        )

        fb, ext, img_d = upload_section("diet_upload", upl_lbl, upl_desc)

        q_lbl = (
            "What do you want to know?"
            if lang == "English"
            else "आप क्या जानना चाहते हैं?"
            if lang == "Hindi"
            else "మీరు ఏమి తెలుసుకోవాలనుకుంటున్నారు?"
            if lang == "Telugu"
            else "நீங்கள் என்ன தெரிந்து கொள்ள விரும்புகிறீர்கள்?"
        )
        q_placeholder = (
            "e.g. Is this meal suitable for weight loss? How can I add more protein?"
            if lang == "English"
            else "जैसे: क्या यह भोजन वजन घटाने के लिए उपयुक्त है? मैं अधिक प्रोटीन कैसे जोड़ सकता हूँ?"
            if lang == "Hindi"
            else "ఉదా: ఈ భోజనం బరువు తగ్గడానికి సరిపోతుందా? నేను ఎక్కువ ప్రోటీన్ ఎలా జోడించాలి?"
            if lang == "Telugu"
            else "எ.கா. இந்த உணவு எடை இழப்புக்கு உகந்ததா? நான் எப்படி அதிக புரதத்தை சேர்ப்பது?"
        )

        diet_q = st.text_area(q_lbl, placeholder=q_placeholder, key="diet_q", height=100)

        goal_lbl = (
            "My current goal"
            if lang == "English"
            else "मेरा वर्तमान लक्ष्य"
            if lang == "Hindi"
            else "నా ప్రస్తుత లక్ష్యం"
            if lang == "Telugu"
            else "எனது தற்போதைய இலக்கு"
        )
        diet_goal_opts = [t("weight_loss"), t("muscle_gain"), t("maintenance")]
        goal_hint = st.selectbox(goal_lbl, diet_goal_opts, key="diet_goal")

    with right:
        info_header = (
            "💡 What the AI analyses"
            if lang == "English"
            else "💡 एआई क्या विश्लेषण करता है"
            if lang == "Hindi"
            else "💡 ఏఐ ఏమి విశ్లేషిస్తుంది"
            if lang == "Telugu"
            else "💡 ஏஐ என்ன பகுப்பாய்வு செய்கிறது"
        )
        li1 = (
            "Calorie & macro estimate (protein / carbs / fat)"
            if lang == "English"
            else "कैलोरी और मैक्रो अनुमान (प्रोटीन / कार्ब्स / वसा)"
            if lang == "Hindi"
            else "కేలరీలు & మాక్రోల అంచనా (ప్రోటీన్ / కార్బోహైడ్రేట్లు / కొవ్వు)"
            if lang == "Telugu"
            else "கலோரி மற்றும் மேக்ரோ மதிப்பீடு"
        )
        li2 = (
            "Nutritional pros and cons of the meal"
            if lang == "English"
            else "भोजन के पोषण संबंधी फायदे और नुकसान"
            if lang == "Hindi"
            else "భోజనం యొక్క పోషకాహార లాభాలు మరియు నష్టాలు"
            if lang == "Telugu"
            else "உணவின் ஊட்டச்சத்து நன்மைகள் மற்றும் தீமைகள்"
        )
        li3 = (
            "3 actionable improvements for your goal"
            if lang == "English"
            else "आपके लक्ष्य के लिए 3 व्यावहारिक सुधार"
            if lang == "Hindi"
            else "మీ లక్ష్యం కోసం 3 ఉపయోగకరమైన సలహాలు"
            if lang == "Telugu"
            else "உங்கள் இலக்கிற்கான 3 பயனுள்ள குறிப்புகள்"
        )
        li4 = (
            "Hydration & portion-size advice"
            if lang == "English"
            else "जलयोजन और भाग-आकार की सलाह"
            if lang == "Hindi"
            else " hydration & పరిమాణ సలహా"
            if lang == "Telugu"
            else "நீர் உட்கொள்ளல் மற்றும் அளவு ஆலோசனை"
        )

        st.markdown(
            f"""
        <div class="info-card" style="padding:24px;">
            <div class="info-label">{info_header}</div><br>
            <ul style="color:#94a3b8;font-size:0.88rem;line-height:2.1;padding-left:16px;margin:0;">
                <li>{li1}</li>
                <li>{li2}</li>
                <li>{li3}</li>
                <li>{li4}</li>
            </ul>
        </div>
        """,
            unsafe_allow_html=True,
        )

    btn_lbl = (
        "Analyse Meal / Diet"
        if lang == "English"
        else "भोजन / डाइट का विश्लेषण करें"
        if lang == "Hindi"
        else "భోజనం / డైట్ విశ్లేషించు"
        if lang == "Telugu"
        else "உணவை பகுப்பாய்வு செய்"
    )
    if st.button("🚀 " + btn_lbl, type="primary", key="diet_btn", use_container_width=True):
        if not fb and not diet_q.strip():
            st.error("Please upload a file or type a question.")
        else:
            with st.spinner(t("loading")):
                try:
                    prompt = (
                        f"Goal: {goal_hint}\nQuestion: {diet_q}\n"
                        f"{'Image description: ' + img_d if img_d else ''}"
                    )
                    sys_p = (
                        "You are a certified sports nutritionist and dietitian. "
                        "Analyse the meal/diet provided. Structure your response with bold section titles:\n"
                        "**🔢 Nutrition Estimate** | **✅ What's Great** | **⚠️ What to Improve** | "
                        "**💡 3 Actionable Tips** | **💧 Hydration & Portion Advice**\n"
                        "Be encouraging, practical, and science-backed."
                    )
                    result = run_ai(prompt, sys_p, fb, ext, img_d)
                    st.markdown("### 📋 AI Nutritionist Report")
                    st.write(result)
                except Exception as e:
                    st.error(f"AI Error: {e}")

# ═══════════════════════════════════════════════════════════════════
#  TAB 2 — WORKOUT COACH
# ═══════════════════════════════════════════════════════════════════
with tab2:
    tab2_header = (
        "Workout Review & Training Plan"
        if lang == "English"
        else "वर्कआउट समीक्षा और प्रशिक्षण योजना"
        if lang == "Hindi"
        else "వర్కౌట్ సమీక్ష & శిక్షణ ప్రణాళిక"
        if lang == "Telugu"
        else "உடற்பயிற்சி மதிப்பாய்வு & பயிற்சி திட்டம்"
    )
    st.markdown(
        f'<div class="section-header"><span class="icon">🏋️</span> {tab2_header}</div>',
        unsafe_allow_html=True,
    )

    left, right = st.columns([1, 1])

    with left:
        upl_lbl_w = (
            "Upload Workout Log or Routine PDF"
            if lang == "English"
            else "वर्कआउट लॉग या रूटीन पीडीएफ अपलोड करें"
            if lang == "Hindi"
            else "వర్కౌట్ లాగ్ లేదా రూటిన్ పీడీఎఫ్ అప్‌లోడ్ చేయండి"
            if lang == "Telugu"
            else "உடற்பயிற்சி பதிவேடு அல்லது வழக்கமான பிடிஎஃப்-ஐ பதிவேற்றவும்"
        )
        upl_desc_w = (
            "Supported: JPG, PNG, PDF (training programmes)"
            if lang == "English"
            else "समर्थित: JPG, PNG, PDF (प्रशिक्षण कार्यक्रम)"
            if lang == "Hindi"
            else "మద్దతు గలవి: JPG, PNG, PDF (శిక్షణ కార్యక్రమాలు)"
            if lang == "Telugu"
            else "ஆதரிக்கப்படும் வடிவங்கள்: JPG, PNG, PDF"
        )

        wfb, wext, wimg_d = upload_section("workout_upload", upl_lbl_w, upl_desc_w)

        q_lbl_w = (
            "What coaching do you need?"
            if lang == "English"
            else "आपको किस प्रशिक्षण सहायता की आवश्यकता है?"
            if lang == "Hindi"
            else "మీకు ఎలాంటి కోచింగ్ సలహా కావాలి?"
            if lang == "Telugu"
            else "உங்களுக்கு என்ன பயிற்சி தேவை?"
        )
        q_placeholder_w = (
            "e.g. Is this enough volume for hypertrophy? Help me break my bench press plateau."
            if lang == "English"
            else "जैसे: क्या यह हाइपरट्रॉफी के लिए पर्याप्त मात्रा है? बेंच प्रेस की बाधा को तोड़ने में मेरी मदद करें।"
            if lang == "Hindi"
            else "ఉదా: ఇది కండరాల పెరుగుదలకు సరిపోతుందా? బెంచ్ ప్రెస్ పీఠభూమిని అధిగమించడానికి సహాయపడండి."
            if lang == "Telugu"
            else "எ.கா. தசை வளர்ச்சிக்கு இது போதுமானதா? எனது உடற்பயிற்சி திறனை மேம்படுத்த உதவவும்."
        )

        workout_q = st.text_area(q_lbl_w, placeholder=q_placeholder_w, key="workout_q", height=100)

        t_goal_lbl = (
            "Training goal"
            if lang == "English"
            else "प्रशिक्षण लक्ष्य"
            if lang == "Hindi"
            else "శిక్షణ లక్ష్యం"
            if lang == "Telugu"
            else "பயிற்சி இலக்கு"
        )
        w_goals = [t("muscle_gain"), t("weight_loss"), "Strength", "Endurance", "General Fitness"]
        w_goal = st.selectbox(t_goal_lbl, w_goals, key="w_goal")

        days_lbl = (
            "Available training days / week"
            if lang == "English"
            else "प्रति सप्ताह उपलब्ध दिन"
            if lang == "Hindi"
            else "వారానికి అందుబాటులో ఉన్న శిక్షణ రోజులు"
            if lang == "Telugu"
            else "வாரத்தில் கிடைக்கக்கூடிய பயிற்சி நாட்கள்"
        )
        w_days = st.slider(days_lbl, 2, 7, 4, key="w_days")

        lvl_lbl = (
            "Experience level"
            if lang == "English"
            else "अनुभव का स्तर"
            if lang == "Hindi"
            else "అనుభవ స్థాయి"
            if lang == "Telugu"
            else "அனுபவ நிலை"
        )
        w_level = st.selectbox(lvl_lbl, ["Beginner", "Intermediate", "Advanced"], key="w_level")

    with right:
        info_header_w = (
            "💡 What the AI reviews"
            if lang == "English"
            else "💡 एआई क्या समीक्षा करता है"
            if lang == "Hindi"
            else "💡 ఏఐ ఏమి సమీక్షిస్తుంది"
            if lang == "Telugu"
            else "💡 ஏஐ என்ன மதிப்பாய்வு செய்கிறது"
        )
        wli1 = (
            "Push/pull/leg balance & muscle-group coverage"
            if lang == "English"
            else "पुश/पुल/लेग बैलेंस और मांसपेशी-समूह कवरेज"
            if lang == "Hindi"
            else "పుష్/పుల్/లెగ్ బ్యాలెన్స్ & కండరాల సమూహాల కవరేజ్"
            if lang == "Telugu"
            else "உடற்பயிற்சி சமநிலை & தசை குழுக்கள் பாதுகாப்பு"
        )
        wli2 = (
            "Sets, reps & progressive overload critique"
            if lang == "English"
            else "सेट, रैप और प्रगतिशील अधिभार की समीक्षा"
            if lang == "Hindi"
            else "సెట్లు, రెప్స్ & ప్రోగ్రెసివ్ ఓవర్‌లోడ్ విశ్లేషణ"
            if lang == "Telugu"
            else "செட்டுகள், ரெப்ஸ் & உடற்பயிற்சி முன்னேற்றம்"
        )
        wli3 = (
            "Cardio integration suggestions"
            if lang == "English"
            else "कार्डियो एकीकरण सुझाव"
            if lang == "Hindi"
            else "కార్డియో అనుసంధాన సలహాలు"
            if lang == "Telugu"
            else "கார்டியோ ஒருங்கிணைப்பு பரிந்துரைகள்"
        )
        wli4 = (
            "Recovery & injury-prevention advice"
            if lang == "English"
            else "रिकवरी और चोट से बचाव की सलाह"
            if lang == "Hindi"
            else "రికవరీ & గాయాల నివారణ సలహా"
            if lang == "Telugu"
            else "மீட்பு & காயம் தடுப்பு ஆலோசனை"
        )

        st.markdown(
            f"""
        <div class="info-card" style="padding:24px;">
            <div class="info-label">{info_header_w}</div><br>
            <ul style="color:#94a3b8;font-size:0.88rem;line-height:2.1;padding-left:16px;margin:0;">
                <li>{wli1}</li>
                <li>{wli2}</li>
                <li>{wli3}</li>
                <li>{wli4}</li>
            </ul>
        </div>
        """,
            unsafe_allow_html=True,
        )

    btn_lbl_w = (
        "Get Coaching Feedback"
        if lang == "English"
        else "कोचिंग फीडबैक प्राप्त करें"
        if lang == "Hindi"
        else "కోచింగ్ అభిప్రాయాన్ని పొందండి"
        if lang == "Telugu"
        else "பயிற்சி கருத்துக்களைப் பெறுக"
    )
    if st.button("🚀 " + btn_lbl_w, type="primary", key="workout_btn", use_container_width=True):
        if not wfb and not workout_q.strip():
            st.error("Please upload a file or type a question.")
        else:
            with st.spinner(t("loading")):
                try:
                    prompt = (
                        f"Goal: {w_goal} | Level: {w_level} | Days/week: {w_days}\n"
                        f"Question: {workout_q}\n"
                        f"{'Image description: ' + wimg_d if wimg_d else ''}"
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
                    st.markdown("### 📋 AI Coach Feedback")
                    st.write(result)
                except Exception as e:
                    st.error(f"AI Error: {e}")

# ═══════════════════════════════════════════════════════════════════
#  TAB 3 — HEALTH REPORT
# ═══════════════════════════════════════════════════════════════════
with tab3:
    tab3_header = (
        "Health Report & Wellness Analysis"
        if lang == "English"
        else "स्वास्थ्य रिपोर्ट और कल्याण विश्लेषण"
        if lang == "Hindi"
        else "ఆరోగ్య నివేదిక & శ్రేయస్సు విశ్లేషణ"
        if lang == "Telugu"
        else "உடல்நல அறிக்கை & ஆரோக்கிய பகுப்பாய்வு"
    )
    st.markdown(
        f'<div class="section-header"><span class="icon">📊</span> {tab3_header}</div>',
        unsafe_allow_html=True,
    )
    st.warning(
        "⚠️ "
        + (
            "Disclaimer: This is for educational purposes only and is NOT medical advice."
            if lang == "English"
            else "अस्वीकरण: यह केवल शैक्षिक उद्देश्यों के लिए है और चिकित्सा सलाह नहीं है।"
            if lang == "Hindi"
            else "నిరాకరణ: ఇది విద్యా ప్రయోజనాల కోసం మాత్రమే మరియు వైద్య సలహా కాదు."
            if lang == "Telugu"
            else "பொறுப்புத் துறப்பு: இது கல்வி நோக்கங்களுக்காக மட்டுமே, மருத்துவ ஆலோசனை அல்ல."
        )
    )

    left, right = st.columns([1, 1])

    with left:
        upl_lbl_r = (
            "Upload Health Report or Body Scan"
            if lang == "English"
            else "स्वास्थ्य रिपोर्ट या बॉडी स्कैन अपलोड करें"
            if lang == "Hindi"
            else "ఆరోగ్య నివేదిక లేదా బాడీ స్కాన్ అప్‌లోడ్ చేయండి"
            if lang == "Telugu"
            else "உடல்நல அறிக்கை அல்லது உடல் ஸ்கேன் பதிவேற்றவும்"
        )
        upl_desc_r = (
            "Supported: JPG, PNG, PDF (blood work, checkups)"
            if lang == "English"
            else "समर्थित: JPG, PNG, PDF (रक्त परीक्षण, चेकअप)"
            if lang == "Hindi"
            else "మద్దతు గలవి: JPG, PNG, PDF (రక్త పరీక్షలు, ఆరోగ్య పరీక్షలు)"
            if lang == "Telugu"
            else "ஆதரிக்கப்படும் வடிவங்கள்: JPG, PNG, PDF"
        )

        rfb, rext, rimg_d = upload_section("report_upload", upl_lbl_r, upl_desc_r)

        q_lbl_r = (
            "What wellness goal do you have?"
            if lang == "English"
            else "आपका कल्याण लक्ष्य क्या है?"
            if lang == "Hindi"
            else "మీ ఆరోగ్య లక్ష్యం ఏమిటి?"
            if lang == "Telugu"
            else "உங்கள் ஆரோக்கிய இலக்கு என்ன?"
        )
        q_placeholder_r = (
            "e.g. Improve energy levels, lower stress, better sleep quality."
            if lang == "English"
            else "जैसे: ऊर्जा स्तर में सुधार, तनाव कम करना, बेहतर नींद की गुणवत्ता।"
            if lang == "Hindi"
            else "ఉదా: శక్తి స్థాయిలను మెరుగుపరచడం, ఒత్తిడిని తగ్గించడం, మంచి నిద్ర నాణ్యత."
            if lang == "Telugu"
            else "எ.கா. ஆற்றல் அளவை மேம்படுத்துதல், மன அழுத்தத்தைக் குறைத்தல்."
        )

        report_q = st.text_area(q_lbl_r, placeholder=q_placeholder_r, key="report_q", height=100)

        metrics_lbl = (
            "Key metrics (optional, if no file)"
            if lang == "English"
            else "प्रमुख मीट्रिक (वैकल्पिक, यदि कोई फ़ाइल नहीं है)"
            if lang == "Hindi"
            else "ముఖ్యమైన కొలతలు (ఐచ్ఛికం, ఫైల్ లేకపోతే)"
            if lang == "Telugu"
            else "முக்கிய அளவீடுகள் (விருப்பம், கோப்பு இல்லை எனில்)"
        )
        metrics_placeholder = (
            "e.g. Cholesterol: 220 mg/dL, Body fat: 28%"
            if lang == "English"
            else "जैसे: कोलेस्ट्रॉल: 220 mg/dL, शरीर की वसा: 28%"
            if lang == "Hindi"
            else "ఉదా: కొలెస్ట్రాల్: 220 mg/dL, శరీర కొవ్వు: 28%"
            if lang == "Telugu"
            else "எ.கா. கொலஸ்ட்ரால்: 220 mg/dL, உடல் கொழுப்பு: 28%"
        )

        manual_data = st.text_area(
            metrics_lbl, placeholder=metrics_placeholder, key="manual_data", height=80
        )

    with right:
        info_header_r = (
            "💡 What the AI reviews"
            if lang == "English"
            else "💡 एआई क्या समीक्षा करता है"
            if lang == "Hindi"
            else "💡 ఏఐ ఏమి సమీక్షిస్తుంది"
            if lang == "Telugu"
            else "💡 ஏஐ என்ன மதிப்பாய்வு செய்கிறது"
        )
        rli1 = (
            "Metrics summary & what they mean"
            if lang == "English"
            else "मीट्रिक सारांश और उनका क्या अर्थ है"
            if lang == "Hindi"
            else "కొలతల సారాంశం & వాటి అర్థం"
            if lang == "Telugu"
            else "அளவீடுகளின் சுருக்கம் & அவற்றின் பொருள்"
        )
        rli2 = (
            "Lifestyle impact on energy, sleep & stamina"
            if lang == "English"
            else "ऊर्जा, नींद और सहनशक्ति पर जीवनशैली का प्रभाव"
            if lang == "Hindi"
            else "శక్తి, నిద్ర & స్టామినాపై జీవనశైలి ప్రభావం"
            if lang == "Telugu"
            else "ஆற்றல், தூக்கம் & சகிப்புத்தன்மையில் வாழ்க்கை முறை தாக்கம்"
        )
        rli3 = (
            "Diet, hydration & activity adjustments"
            if lang == "English"
            else "आहार, जलयोजन और गतिविधि समायोजन"
            if lang == "Hindi"
            else "ఆహారం, నీరు & కార్యాచరణ సర్దుబాట్లు"
            if lang == "Telugu"
            else "உணவு, நீர் & செயல்பாட்டு சரிசெய்தல்"
        )
        rli4 = (
            "Sleep hygiene & stress management tips"
            if lang == "English"
            else "नींद की स्वच्छता और तनाव प्रबंधन युक्तियाँ"
            if lang == "Hindi"
            else "నిద్ర విధానం & ఒత్తిడి నిర్వహణ చిట్కాలు"
            if lang == "Telugu"
            else "தூக்க சுகாதாரம் & மன அழுத்த மேலாண்மை குறிப்புகள்"
        )

        st.markdown(
            f"""
        <div class="info-card" style="padding:24px;">
            <div class="info-label">{info_header_r}</div><br>
            <ul style="color:#94a3b8;font-size:0.88rem;line-height:2.1;padding-left:16px;margin:0;">
                <li>{rli1}</li>
                <li>{rli2}</li>
                <li>{rli3}</li>
                <li>{rli4}</li>
            </ul>
        </div>
        """,
            unsafe_allow_html=True,
        )

    btn_lbl_r = (
        "Analyse Report"
        if lang == "English"
        else "रिपोर्ट का विश्लेषण करें"
        if lang == "Hindi"
        else "నివేదికను విశ్లేషించండి"
        if lang == "Telugu"
        else "அறிக்கையை பகுப்பாய்வு செய்"
    )
    if st.button("🚀 " + btn_lbl_r, type="primary", key="report_btn", use_container_width=True):
        if not rfb and not report_q.strip() and not manual_data.strip():
            st.error("Please upload a file, enter metrics, or type a question.")
        else:
            with st.spinner(t("loading")):
                try:
                    prompt = (
                        f"Goal: {report_q}\n"
                        f"{'Manual metrics: ' + manual_data + chr(10) if manual_data else ''}"
                        f"{'Image description: ' + rimg_d if rimg_d else ''}"
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
                    st.markdown("### 📋 AI Wellness Report")
                    st.write(result)
                except Exception as e:
                    st.error(f"AI Error: {e}")

# ═══════════════════════════════════════════════════════════════════
#  TAB 4 — CONVERSATIONAL Q&A
# ═══════════════════════════════════════════════════════════════════
with tab4:
    tab4_header = (
        "Ask Your AI Fitness Coach Anything"
        if lang == "English"
        else "अपने एआई फिटनेस कोच से कुछ भी पूछें"
        if lang == "Hindi"
        else "మీ ఏఐ ఫిట్‌నెస్ కోచ్‌ని ఏదైనా అడగండి"
        if lang == "Telugu"
        else "உங்கள் ஏஐ ஃபிட்னஸ் பயிற்சியாளரிடம் எது வேண்டுமானாலும் கேளுங்கள்"
    )
    st.markdown(
        f'<div class="section-header"><span class="icon">💬</span> {tab4_header}</div>',
        unsafe_allow_html=True,
    )

    quick_starters_lbl = (
        "💡 Quick starters:"
        if lang == "English"
        else "💡 त्वरित शुरूआत करने वाले:"
        if lang == "Hindi"
        else "💡 శీఘ్ర ప్రశ్నలు:"
        if lang == "Telugu"
        else "💡 விரைவான கேள்விகள்:"
    )
    st.markdown(f"**{quick_starters_lbl}**")

    qcols = st.columns(3)

    starters = [
        "What should I eat post-workout?"
        if lang == "English"
        else "वर्कआउट के बाद मुझे क्या खाना चाहिए?"
        if lang == "Hindi"
        else "వర్కౌట్ తర్వాత నేను ఏమి తినాలి?"
        if lang == "Telugu"
        else "உடற்பயிற்சிக்குப் பிறகு நான் என்ன சாப்பிட வேண்டும்?",
        "How do I calculate my TDEE?"
        if lang == "English"
        else "मैं अपने टीडीईई (TDEE) की गणना कैसे करूं?"
        if lang == "Hindi"
        else "నేను నా టీడీఈఈని ఎలా లెక్కించాలి?"
        if lang == "Telugu"
        else "எனது டிடிஇஇ-ஐ எவ்வாறு கணக்கிடுவது?",
        "Best exercises for lower back pain?"
        if lang == "English"
        else "पीठ के निचले हिस्से में दर्द के लिए सबसे अच्छा व्यायाम?"
        if lang == "Hindi"
        else "నడుము నొప్పికి ఉత్తమ వ్యాయామాలు ఏమిటి?"
        if lang == "Telugu"
        else "நடு முதுகு வலிக்கு சிறந்த உடற்பயிற்சிகள்?",
        "How many rest days per week?"
        if lang == "English"
        else "प्रति सप्ताह कितने विश्राम दिन होने चाहिए?"
        if lang == "Hindi"
        else "వారానికి ఎన్ని రోజులు విశ్రాంతి తీసుకోవాలి?"
        if lang == "Telugu"
        else "வாரத்திற்கு எத்தனை நாட்கள் ஓய்வு தேவை?",
        "What is progressive overload?"
        if lang == "English"
        else "प्रगतिशील अधिभार (progressive overload) क्या है?"
        if lang == "Hindi"
        else "ప్రోగ్రెసివ్ ఓవర్‌లోడ్ అంటే ఏమిటి?"
        if lang == "Telugu"
        else "முற்போக்கான சுமை (progressive overload) என்றால் என்ன?",
        "How to improve sleep quality?"
        if lang == "English"
        else "नींद की गुणवत्ता में कैसे सुधार करें?"
        if lang == "Hindi"
        else "నిద్ర నాణ్యతను ఎలా మెరుగుపరచాలి?"
        if lang == "Telugu"
        else "தூக்கத்தின் தரத்தை எவ்வாறு மேம்படுத்துவது?",
    ]

    starter_clicked = None
    for i, q in enumerate(starters):
        with qcols[i % 3]:
            if st.button(q, key=f"starter_{i}", use_container_width=True):
                starter_clicked = q

    st.write("")

    your_q_lbl = (
        "✍️ Your question:"
        if lang == "English"
        else "✍️ आपका प्रश्न:"
        if lang == "Hindi"
        else "✍️ మీ ప్రశ్న:"
        if lang == "Telugu"
        else "✍️ உங்கள் கேள்வி:"
    )
    q_placeholder_chat = (
        "e.g. What is the difference between active and passive recovery?"
        if lang == "English"
        else "जैसे: सक्रिय और निष्क्रिय रिकवरी में क्या अंतर है?"
        if lang == "Hindi"
        else "ఉదా: యాక్టివ్ మరియు పాసివ్ రికవరీ మధ్య తేడా ఏమిటి?"
        if lang == "Telugu"
        else "எ.கா. செயலில் உள்ள மற்றும் செயலற்ற மீட்புக்கு என்ன வித்தியாசம்?"
    )

    chat_q = st.text_area(
        your_q_lbl,
        value=starter_clicked if starter_clicked else "",
        placeholder=q_placeholder_chat,
        height=110,
        key="chat_q",
    )

    btn_lbl_chat = (
        "Ask Coach"
        if lang == "English"
        else "कोच से पूछें"
        if lang == "Hindi"
        else "కోచ్‌ని అడగండి"
        if lang == "Telugu"
        else "பயிற்சியாளரிடம் கேள்"
    )
    if st.button("💬 " + btn_lbl_chat, type="primary", key="chat_btn", use_container_width=True):
        if not chat_q.strip():
            st.error("Please enter a question.")
        else:
            with st.spinner(t("loading")):
                try:
                    sys_p = (
                        "You are an expert personal trainer, nutritionist, and wellness coach. "
                        "Give a comprehensive, friendly, and scientifically accurate answer. "
                        "Use bold headings, bullet points, and emojis to make the response easy to read."
                    )
                    result = ai_helper.get_ai_response(chat_q, sys_p, max_tokens=1800)
                    st.markdown("### 💬 AI Coach Response")
                    st.write(result)
                except Exception as e:
                    st.error(f"AI Error: {e}")
