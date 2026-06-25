import sqlite3
from datetime import date

import streamlit as st

import ai_helper
from utils.i18n import t
from utils.navigation import initialize_page

# 1. Initialize Page and Shared Sidebar
initialize_page(t("dashboard"), "🏠")

username = st.session_state.username

# 2. Database Connection
conn = sqlite3.connect("fitness.db", check_same_thread=False)
cursor = conn.cursor()

# Fetch user details
cursor.execute("SELECT age, gender, height, weight, goal FROM users WHERE username=?", (username,))
user_row = cursor.fetchone()

# Default fallback values
user_age = 25
user_gender = "Male"
user_height = 170.0
user_weight = 70.0
user_goal = "Weight Loss"

if user_row:
    user_age, user_gender, user_height, user_weight, user_goal = user_row

# Compute BMR / TDEE
bmr = 10 * user_weight + 6.25 * user_height - 5 * user_age + (5 if user_gender == "Male" else -161)
tdee = bmr * 1.375  # Assume moderate activity multiplier for default dashboard
target_calories = int(
    tdee - 500 if user_goal == "Weight Loss" else tdee + 300 if user_goal == "Muscle Gain" else tdee
)
protein_goal = int(user_weight * 1.8)  # 1.8g per kg

# Fetch today's logged calories
today_str = str(date.today())
cursor.execute("SELECT SUM(calories) FROM meals WHERE username=? AND date=?", (username, today_str))
today_calories_val = cursor.fetchone()[0]
today_calories = int(today_calories_val) if today_calories_val else 0

# Fetch workout count this week
cursor.execute(
    "SELECT COUNT(*) FROM workouts WHERE username=? AND date >= date('now', '-7 days')", (username,)
)
workouts_this_week = cursor.fetchone()[0]

# Calculate calorie progress
progress_pct = min(int((today_calories / target_calories) * 100), 100) if target_calories > 0 else 0

# ── HERO SECTION ─────────────────────────────────────────────
st.markdown(
    f"""
<div class="hero-card">
    <h1>🏋️ {t("app_title")}</h1>
    <h3>Your Personal AI Fitness & Nutrition Coach</h3>
    <p>
        Track Workouts • Generate Diet Plans • AI Coaching • Progress Analytics
    </p>
</div>
""",
    unsafe_allow_html=True,
)

st.write("")

# ── TODAY OVERVIEW ───────────────────────────────────────────
st.markdown(f"## 📊 {t('today_overview')}")

col1, col2, col3, col4 = st.columns(4)

with col1:
    today_eaten_lbl = t("today_calories")
    st.metric(f"🔥 {today_eaten_lbl}", f"{today_calories} / {target_calories} kcal")

with col2:
    st.metric(f"💪 {t('protein_goal')}", f"{protein_goal} g")

with col3:
    st.metric(f"⚖️ {t('weight')}", f"{user_weight} kg")

with col4:
    workouts_lbl = t("workouts_week")
    st.metric(f"🏃 {workouts_lbl}", f"{workouts_this_week}")

st.divider()

# ── DAILY PROGRESS ───────────────────────────────────────────
st.markdown(f"## 🎯 {t('daily_progress')} ({today_eaten_lbl})")
st.progress(progress_pct / 100.0)

progress_desc = (
    t("progress_desc_text")
    .replace("{today_calories}", str(today_calories))
    .replace("{target_calories}", str(target_calories))
    .replace("{progress_pct}", str(progress_pct))
)
st.info(progress_desc)

st.divider()

# ── DAILY AI FITNESS INSIGHT (NEW AI FEATURE) ────────────────
st.markdown(f"## 🧠 {t('fitness_tip')}")

get_tip_btn = t("get_ai_tip")

if st.button(f"🧠 {get_tip_btn}", use_container_width=True):
    with st.spinner(t("loading")):
        prompt = f"""
The user has the following profile:
- Age: {user_age}
- Gender: {user_gender}
- Weight: {user_weight} kg
- Height: {user_height} cm
- Fitness Goal: {user_goal}
- Target Calories: {target_calories} kcal
- Today's Consumed Calories: {today_calories} kcal
- Workouts this week: {workouts_this_week}

Generate 1 specific, highly personalized fitness or nutrition tip for today. Keep it short (2-3 sentences), encouraging, and practical.
"""
        sys_p = "You are a friendly personal fitness coach. Keep it short."
        tip_response = ai_helper.get_ai_response(prompt, sys_p)

        st.markdown(ai_helper.provider_badge(), unsafe_allow_html=True)
        st.info(tip_response)

st.divider()

# ── QUICK ACTIONS ────────────────────────────────────────────
st.markdown(f"## ⚡ {t('quick_actions')}")

a1, a2, a3, a4 = st.columns(4)

with a1:
    if st.button("🥗 " + t("ai_diet_plan"), use_container_width=True):
        st.switch_page("pages/ai_diet plan.py")

with a2:
    if st.button("💪 " + t("ai_workout_planner"), use_container_width=True):
        st.switch_page("pages/ai_workout planner.py")

with a3:
    if st.button("🍽️ " + t("meals"), use_container_width=True):
        st.switch_page("pages/meals.py")

with a4:
    if st.button("📈 " + t("progress"), use_container_width=True):
        st.switch_page("pages/progress.py")

conn.close()
