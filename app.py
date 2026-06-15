import streamlit as st

# ==========================================
# PAGE CONFIG
# ==========================================
st.set_page_config(
    page_title="AI Fitness Tracker",
    page_icon="🏋️",
    layout="wide"
)

# ==========================================
# IMPORTS
# ==========================================
import sqlite3
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import ai_helper
from utils.theme import load_css
from utils.i18n import LANGUAGES, t

# ==========================================
# CSS
# ==========================================
load_css()

# ==========================================
# SESSION INIT (SAFE)
# ==========================================
if "current_language" not in st.session_state:
    st.session_state.current_language = "English"

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if "username" not in st.session_state:
    st.session_state.username = ""

# ==========================================
# SIDEBAR - LANGUAGE (ONLY ONCE)
# ==========================================
st.sidebar.markdown("## 🌐 Language")

st.sidebar.selectbox(
    "Choose Language",
    options=list(LANGUAGES.keys()),
    key="current_language"
)

# ==========================================
# SIDEBAR - AI SETTINGS
# ==========================================
st.sidebar.markdown("---")
ai_helper.render_ai_sidebar()

# ==========================================
# DATABASE
# ==========================================
conn = sqlite3.connect("fitness.db", check_same_thread=False)
cursor = conn.cursor()

# ==========================================
# LOGIN PAGE
# ==========================================
if not st.session_state.logged_in:

    st.title(f"🏋️ {t('app_title')}")

    auth_mode = st.radio(
        t("login_signup"),
        [t("login"), t("signup")]
    )

    username = st.text_input(t("username"))
    password = st.text_input(t("password"), type="password")

    if st.button(t("submit")):
        st.session_state.logged_in = True
        st.session_state.username = username
        st.rerun()

# ==========================================
# MAIN APP
# ==========================================
else:

    st.sidebar.success(f"Logged in as {st.session_state.username}")

    menu = st.sidebar.radio(
        "Navigation",
        [
            t("dashboard"),
            t("ai_coach"),
            t("diet_planner"),
            t("workout_planner"),
            t("food_scanner")
        ]
    )

    # ---------------- DASHBOARD ----------------
    if menu == t("dashboard"):
        st.title(f"📊 {t('dashboard')}")
        st.success(f"Welcome back, {st.session_state.username}!")
        st.write(t("track_message"))

    # ---------------- AI COACH ----------------
    elif menu == t("ai_coach"):
        st.title(f"🤖 {t('ai_coach')}")

        prompt = st.text_input(t("ask_ai"))

        if prompt:
            placeholder = st.empty()
            response = ""

            for token in ai_helper.stream_ai_response(prompt):
                response += token
                placeholder.markdown(response)

    # ---------------- DIET ----------------
    elif menu == t("diet_planner"):
        st.title(f"🥗 {t('diet_planner')}")

        goal = st.text_area(t("enter_diet_goal"))

        if st.button(t("generate_diet")):
            result = ai_helper.get_ai_response(
                f"Create a diet plan for: {goal}"
            )
            st.markdown(result)

    # ---------------- WORKOUT ----------------
    elif menu == t("workout_planner"):
        st.title(f"💪 {t('workout_planner')}")

        goal = st.text_area(t("enter_workout_goal"))

        if st.button(t("generate_workout")):
            result = ai_helper.get_ai_response(
                f"Create a workout plan for: {goal}"
            )
            st.markdown(result)

    # ---------------- FOOD SCANNER ----------------
    elif menu == t("food_scanner"):
        st.title(f"📸 {t('food_scanner')}")

        uploaded_file = st.file_uploader(
            t("upload_food"),
            type=["png", "jpg", "jpeg"]
        )

        if uploaded_file:
            st.image(uploaded_file)

            if st.button(t("analyze_food")):
                result = ai_helper.analyze_food_image(
                    uploaded_file.read()
                )
                st.success(result)