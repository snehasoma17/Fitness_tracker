import streamlit as st
import sqlite3
import os, sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import ai_helper

# ─────────────────────────────────────────────
# CONFIG
# ─────────────────────────────────────────────
st.set_page_config(
    page_title="AI Fitness Tracker",
    page_icon="🏋️",
    layout="wide"
)

# ─────────────────────────────────────────────
# DATABASE
# ─────────────────────────────────────────────
conn = sqlite3.connect("fitness.db", check_same_thread=False)
cursor = conn.cursor()

# ─────────────────────────────────────────────
# SESSION
# ─────────────────────────────────────────────
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if "username" not in st.session_state:
    st.session_state.username = ""

# ─────────────────────────────────────────────
# AI SIDEBAR
# ─────────────────────────────────────────────
st.sidebar.title("⚙️ AI Settings")

st.sidebar.selectbox(
    "Provider",
    ["ollama", "openai"],
    key="ai_provider"
)

st.sidebar.text_input("API Key (if needed)", type="password", key="api_key")

# ─────────────────────────────────────────────
# LOGIN PAGE
# ─────────────────────────────────────────────
if not st.session_state.logged_in:

    st.title("🏋️ AI Fitness Tracker")

    choice = st.radio("Login / Signup", ["Login", "Signup"])

    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    if st.button("Submit"):
        st.session_state.logged_in = True
        st.session_state.username = username
        st.rerun()

# ─────────────────────────────────────────────
# MAIN APP
# ─────────────────────────────────────────────
else:

    st.sidebar.success(f"Logged in as {st.session_state.username}")

    menu = st.sidebar.radio(
        "Navigation",
        [
            "Dashboard",
            "AI Coach",
            "AI Diet Plan",
            "AI Workout",
            "📸 Food Scanner"
        ]
    )

    # ───────── DASHBOARD ─────────
    if menu == "Dashboard":
        st.title("Dashboard")
        st.write("Welcome to your fitness AI system")

    # ───────── AI COACH ─────────
    elif menu == "AI Coach":
        st.title("AI Coach")

        prompt = st.text_input("Ask anything")

        if prompt:
            response = ""
            for token in ai_helper.stream_ai_response(prompt):
                response += token
                st.write(response)

    # ───────── DIET ─────────
    elif menu == "AI Diet Plan":
        st.title("Diet Plan")

        prompt = st.text_area("Enter goal")

        if st.button("Generate"):
            st.write(ai_helper.get_ai_response(prompt))

    # ───────── WORKOUT ─────────
    elif menu == "AI Workout":
        st.title("Workout Plan")

        prompt = st.text_area("Enter goal")

        if st.button("Generate"):
            st.write(ai_helper.get_ai_response(prompt))

    # ───────── 📸 FOOD SCANNER ─────────
    elif menu == "📸 Food Scanner":
        st.title("Food Scanner AI")

        file = st.file_uploader("Upload food image", type=["png", "jpg", "jpeg"])

        if file:
            st.image(file, use_container_width=True)

            if st.button("Analyze Food"):
                result = ai_helper.analyze_food_image(file.read())
                st.success(result)