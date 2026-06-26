import os
import sqlite3
import sys

import streamlit as st

# Ensure the root directory is in the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from utils.i18n import t
from utils.navigation import initialize_page

# 1. Initialize the page configuration and render the shared sidebar
initialize_page(t("app_title"), "🏋️", check_login=False)

# 2. Database connection
conn = sqlite3.connect("fitness.db", check_same_thread=False)
cursor = conn.cursor()

# Ensure database tables are fully initialized with correct schemas
cursor.execute("""
CREATE TABLE IF NOT EXISTS users(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE,
    password TEXT,
    age INTEGER DEFAULT 25,
    gender TEXT DEFAULT 'Male',
    height REAL DEFAULT 170.0,
    weight REAL DEFAULT 70.0,
    goal TEXT DEFAULT 'Weight Loss'
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS workouts(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT,
    date TEXT,
    exercise TEXT,
    duration INTEGER,
    calories INTEGER
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS meals(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT,
    date TEXT,
    meal TEXT,
    food TEXT,
    calories INTEGER,
    protein INTEGER DEFAULT 0,
    carbs INTEGER DEFAULT 0
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS weight_log(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT,
    date TEXT,
    weight REAL,
    notes TEXT
)
""")

conn.commit()

# ==========================================
# LOGIN / SIGNUP FLOW
# ==========================================
if not st.session_state.logged_in:
    st.markdown(
        f"""
    <div class="hero-card" style="padding:28px 36px;text-align:center;">
        <div style="font-size:4rem;margin-bottom:12px;">🏋️</div>
        <h1>{t("app_title")}</h1>
        <p style="color:#a5b4fc;font-size:1.1rem;">{t("home_subtitle")}</p>
    </div>
    """,
        unsafe_allow_html=True,
    )

    st.write("")

    # Auth Mode Selection
    auth_mode = st.radio(t("login_signup"), [t("login"), t("signup")], horizontal=True)

    # Auth Form
    with st.form("auth_form"):
        username_input = st.text_input(t("username"), placeholder="e.g. sneha")
        password_input = st.text_input(t("password"), type="password", placeholder="••••••••")
        submit_btn = st.form_submit_button(t("submit"), type="primary")

        if submit_btn:
            if not username_input.strip() or not password_input.strip():
                st.error("⚠️ " + t("fill_all_fields"))
            else:
                if auth_mode == t("login"):
                    # Check credentials
                    cursor.execute(
                        "SELECT * FROM users WHERE username=? AND password=?",
                        (username_input.strip(), password_input.strip()),
                    )
                    user = cursor.fetchone()
                    if user:
                        st.session_state.logged_in = True
                        st.session_state.username = username_input.strip()
                        st.success(f"✓ {t('welcome_back')}, {username_input}!")
                        st.rerun()
                    else:
                        st.error("❌ " + t("invalid_credentials"))
                else:
                    # Signup Mode - Check if username exists
                    cursor.execute(
                        "SELECT * FROM users WHERE username=?", (username_input.strip(),)
                    )
                    if cursor.fetchone():
                        st.error("❌ " + t("username_exists"))
                    else:
                        # Insert user
                        cursor.execute(
                            "INSERT INTO users (username, password) VALUES (?, ?)",
                            (username_input.strip(), password_input.strip()),
                        )
                        conn.commit()
                        st.session_state.logged_in = True
                        st.session_state.username = username_input.strip()
                        st.success(f"✓ {t('account_created')} {username_input}!")
                        st.rerun()

# ==========================================
# LOGGED IN LANDING/HUB
# ==========================================
else:
    st.markdown(
        f"""
    <div class="hero-card" style="padding:28px 36px;">
        <h1>👋 {t("success")}!</h1>
        <h3>{t("app_title")} - {t("nav_home")} Hub</h3>
        <p>{t("logged_in_as")}: <span style="color:#a5b4fc;font-weight:700;">@{st.session_state.username}</span></p>
    </div>
    """,
        unsafe_allow_html=True,
    )

    st.write("")

    # Quick overview & redirection guidelines
    st.info("ℹ️ " + t("home_nav_info"))

    # Grid of quick navigation buttons
    st.markdown(f"### ⚡ {t('quick_actions')}")
    col1, col2, col3 = st.columns(3)

    with col1:
        if st.button("📊 " + t("dashboard"), use_container_width=True):
            st.switch_page("pages/dashboard.py")
        if st.button("🥗 " + t("ai_diet_plan"), use_container_width=True):
            st.switch_page("pages/ai_diet plan.py")
        if st.button("📄 " + t("rag_assistant"), use_container_width=True):
            st.switch_page("pages/rag_fitness_assistant.py")

    with col2:
        if st.button("🍽️ " + t("meals"), use_container_width=True):
            st.switch_page("pages/meals.py")
        if st.button("💪 " + t("ai_workout_planner"), use_container_width=True):
            st.switch_page("pages/ai_workout planner.py")
        if st.button("👤 " + t("profile"), use_container_width=True):
            st.switch_page("pages/profile.py")

    with col3:
        if st.button("🔥 " + t("workout_streak"), use_container_width=True):
            st.switch_page("pages/workout-streak.py")
        if st.button("📈 " + t("progress"), use_container_width=True):
            st.switch_page("pages/progress.py")
        if st.button("🤖 " + t("ai_coach"), use_container_width=True):
            st.switch_page("pages/ai-coach.py")

    st.write("")
    st.divider()

    # Logout Action
    if st.button("🔒 " + t("logout"), type="secondary"):
        st.session_state.logged_in = False
        st.session_state.username = ""
        st.success("✓ " + t("logout") + " " + t("success"))
        st.rerun()

conn.close()
