import streamlit as st
import sqlite3

# --------------------------------------------------
# PERFORMANCE: Lazy imports for heavy libraries
# --------------------------------------------------
# Delayed import of ai_helper to avoid loading ollama/openai at startup

# --------------------------------------------------
# PAGE CONFIG (MUST BE FIRST)
# --------------------------------------------------
st.set_page_config(
    page_title="AI Fitness Tracker",
    page_icon="🏋️",
    layout="wide"
)

# --------------------------------------------------
# CACHED RESOURCES (Fast)
# --------------------------------------------------
@st.cache_resource
def get_db_connection():
    return sqlite3.connect("fitness.db", check_same_thread=False)

@st.cache_data
def load_translations(lang_code):
    """Load translations from JSON files instead of API calls (much faster)"""
    import json
    try:
        with open(f"pages/i18n/{lang_code}.json", "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}

@st.cache_resource
def get_ai_helper():
    """Lazy load ai_helper only when needed (avoids loading ollama/openai at startup)"""
    import ai_helper
    return ai_helper

# --------------------------------------------------
# LANGUAGE (i18n SETUP) - MUST BE EARLY IN APP
# --------------------------------------------------
LANGUAGES = {
    "English": "en",
    "Hindi": "hi"
}

# Initialize language in session state
if "current_language" not in st.session_state:
    st.session_state.current_language = "English"

# Create a list of language names for the selectbox
lang_names = list(LANGUAGES.keys())

# Find the current index
try:
    current_index = lang_names.index(st.session_state.current_language)
except ValueError:
    current_index = 0

# Get current language code FIRST
current_lang_name = st.session_state.current_language
lang = LANGUAGES[current_lang_name]

# Load translations from JSON FIRST
translations = load_translations(lang)

# Define t() function FIRST
def t(key):
    """Translate key using loaded translations"""
    return translations.get(key, key)

# NOW use t() in selectbox
selected_lang_name = st.sidebar.selectbox(
    t("choose_language"),
    options=lang_names,
    index=current_index,
    key="current_language"
)

# Update language if selection changed
if selected_lang_name != st.session_state.current_language:
    st.session_state.current_language = selected_lang_name
    lang = LANGUAGES[selected_lang_name]
    translations = load_translations(lang)
    
    # Redefine t() with new translations
    def t(key):
        return translations.get(key, key)

# Get cached DB connection
conn = get_db_connection()
cursor = conn.cursor()

# --------------------------------------------------
# SESSION STATE
# --------------------------------------------------
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if "username" not in st.session_state:
    st.session_state.username = ""

# --------------------------------------------------
# SIDEBAR AI SETTINGS
# --------------------------------------------------
st.sidebar.title(t("ai_settings"))

st.sidebar.selectbox(
    t("provider"),
    ["ollama", "openai"],
    key="ai_provider"
)

st.sidebar.text_input(
    t("api_key"),
    type="password",
    key="api_key"
)

# --------------------------------------------------
# LOGIN PAGE
# --------------------------------------------------
if not st.session_state.logged_in:

    st.markdown(f"""
    <div style="
        padding:40px;
        border-radius:20px;
        background:linear-gradient(135deg,#2563eb,#7c3aed);
        color:white;
        text-align:center;
        margin-bottom:30px;">
        <h1>{t('app_title')}</h1>
        <h3>{t('app_subtitle')}</h3>
        <p>{t('app_description')}</p>
    </div>
    """, unsafe_allow_html=True)

    choice = st.radio(
        t("choose_action"),
        [t("login"), t("signup")],
        horizontal=True
    )

    username = st.text_input(t("username"))
    password = st.text_input(t("password"), type="password")

    if st.button(t("submit")):

        st.session_state.logged_in = True
        st.session_state.username = username

        st.rerun()

# --------------------------------------------------
# MAIN APP
# --------------------------------------------------
else:

    st.sidebar.success(
        f"{t('logged_in_as')} {st.session_state.username}"
    )

    menu = st.sidebar.radio(
        t("navigation"),
        [
            t("dashboard_title"),
            t("ai_coach"),
            t("diet_planner"),
            t("workout_planner"),
            t("food_scanner")
        ]
    )

    # ==================================================
    # DASHBOARD
    # ==================================================
    if menu == t("dashboard_title"):

        st.markdown("""
        <div style="
            padding:30px;
            border-radius:20px;
            background:linear-gradient(135deg,#2563eb,#7c3aed);
            color:white;
            text-align:center;
            margin-bottom:20px;">
            <h1>🏋️ AI Fitness Tracker</h1>
            <h3>AI Powered Fitness & Nutrition Assistant</h3>
        </div>
        """, unsafe_allow_html=True)

        c1, c2, c3, c4 = st.columns(4)

        with c1:
            st.metric(f"🔥 {t('calories_goal')}", "2200")

        with c2:
            st.metric(f"💪 {t('protein_goal')}", "140g")

        with c3:
            st.metric(f"⚖️ {t('weight')}", "70 kg")

        with c4:
            st.metric(f"🚶 {t('steps')}", "8500")

        st.markdown(f"## 🚀 {t('features')}")

        f1, f2, f3, f4 = st.columns(4)

        with f1:
            st.info(f"🤖 {t('ai_coach')}")

        with f2:
            st.info(f"🥗 {t('diet_planner')}")

        with f3:
            st.info(f"💪 {t('workout_planner')}")

        with f4:
            st.info(f"📸 {t('food_scanner')}")

        st.divider()

        st.subheader(f"🎯 {t('progress')}")

        st.progress(70)

        st.info(t("complete_workout"))
        
        st.success(t("good_progress"))

    # ==================================================
    # AI COACH
    # ==================================================
    elif menu == t("ai_coach"):

        st.title(f"🤖 {t('ai_coach')}")

        prompt = st.text_area(t("ask_question"))

        if st.button(t("submit")):

            try:
                response = get_ai_helper().get_ai_response(
                    f"{prompt}\nRespond in {lang} language"
                )
                st.success(response)

            except Exception as e:
                st.error(f"{t('ai_error')}: {e}")

    # ==================================================
    # AI DIET PLAN
    # ==================================================
    elif menu == t("diet_planner"):

        st.title(f"🥗 {t('diet_planner')}")

        goal = st.text_area(t("enter_goal"))

        if st.button(t("generate_diet_plan")):

            try:
                response = get_ai_helper().get_ai_response(
                    f"Create a personalized diet plan for: {goal}\nRespond in {lang} language"
                )

                st.success(response)

            except Exception as e:
                st.error(f"{t('ai_error')}: {e}")

    # ==================================================
    # AI WORKOUT
    # ==================================================
    elif menu == t("workout_planner"):

        st.title(f"💪 {t('workout_planner')}")

        goal = st.text_area(t("enter_fitness_goal"))

        if st.button(t("generate_workout")):

            try:
                response = get_ai_helper().get_ai_response(
                    f"Create a workout plan for: {goal}\nRespond in {lang} language"
                )

                st.success(response)

            except Exception as e:
                st.error(f"{t('ai_error')}: {e}")

    # ==================================================
    # FOOD SCANNER
    # ==================================================
    elif menu == t("food_scanner"):

        st.title(f"📸 {t('food_scanner')}")

        uploaded_file = st.file_uploader(
            t("upload_food_image"),
            type=["jpg", "jpeg", "png"]
        )

        if uploaded_file:

            st.image(uploaded_file, use_container_width=True)

            if st.button(t("analyze_food")):

                try:
                    image_bytes = uploaded_file.read()

                    result = get_ai_helper().analyze_food_image(image_bytes)

                    st.success(result)

                except Exception as e:
                    st.error(f"{t('ai_error')}: {e}")