import os
import sqlite3
from datetime import date

import pandas as pd
import streamlit as st

import ai_helper
from utils.i18n import t
from utils.navigation import initialize_page

# 1. Initialize Page and Sidebar
initialize_page(t("profile"), "👤")

username = st.session_state.username

# 2. Database Connection
conn = sqlite3.connect("fitness.db", check_same_thread=False)
cursor = conn.cursor()

user_df = pd.read_sql("SELECT * FROM users WHERE username=?", conn, params=(username,))
user = user_df.iloc[0] if not user_df.empty else None

# ── PAGE HEADER ──────────────────────────────────────────────
st.markdown(
    f"""
<div class="hero-card" style="padding:28px 36px;display:flex;align-items:center;gap:24px;">
    <div style="font-size:4rem;">👤</div>
    <div>
        <h1 style="margin:0;font-size:2rem !important;">{t("profile")}</h1>
        <h3 style="margin:0;font-size:1rem !important;color:#64748b !important;">
            {t("profile_subtitle")} — <span style="color:#a5b4fc;">@{username}</span>
        </h3>
    </div>
</div>
""",
    unsafe_allow_html=True,
)

st.write("")

# ── PROFILE PHOTO & EDIT FORM ────────────────────────────────
left, right = st.columns([2, 3])

# Calculate initial BMR/TDEE for stats
h = float(user.get("height", 170.0)) if user is not None else 170.0
w = float(user.get("weight", 70.0)) if user is not None else 70.0
a = int(user.get("age", 25)) if user is not None else 25
g = str(user.get("gender", "Male")) if user is not None else "Male"
gl = str(user.get("goal", "Weight Loss")) if user is not None else "Weight Loss"

bmi = round(w / ((h / 100) ** 2), 1)
if bmi < 18.5:
    bl, bc = "Underweight", "#f59e0b"
elif bmi < 25:
    bl, bc = "Healthy ✓", "#10b981"
elif bmi < 30:
    bl, bc = "Overweight", "#f59e0b"
else:
    bl, bc = "Obese", "#ef4444"

bmr_init = round(10 * w + 6.25 * h - 5 * a + (5 if g == "Male" else -161))
tdee_init = round(bmr_init * 1.375)
target_cals_init = int(
    tdee_init - 500
    if gl == "Weight Loss"
    else tdee_init + 300
    if gl == "Muscle Gain"
    else tdee_init
)

with left:
    st.markdown(
        '<div class="section-header"><span class="icon">📸</span> Profile Photo</div>',
        unsafe_allow_html=True,
    )
    photo_path = f"data/photos/{username}_profile.jpg"
    if os.path.exists(photo_path):
        st.image(photo_path, caption="Profile photo", use_container_width=True)
    else:
        st.markdown(
            """
        <div class="info-card" style="text-align:center;padding:40px;">
            <div style="font-size:4rem;">🧑</div>
            <div class="info-label" style="margin-top:12px;">No photo uploaded</div>
        </div>
        """,
            unsafe_allow_html=True,
        )

    uploaded_photo = st.file_uploader("Upload Profile Photo", type=["jpg", "jpeg", "png"])
    if uploaded_photo:
        os.makedirs("data/photos", exist_ok=True)
        with open(photo_path, "wb") as f:
            f.write(uploaded_photo.read())
        st.success("✅ Profile photo updated!")
        st.rerun()

    st.write("")
    st.markdown(
        f"""
    <div class="info-card">
        <div class="info-label">📊 {t("quick_stats")}</div>
        <br>
        <div style="display:flex;justify-content:space-between;margin-bottom:10px;">
            <span style="color:#94a3b8;">⚖️ {t("weight")}</span>
            <span style="color:#a5b4fc;font-weight:700;">{w} kg</span>
        </div>
        <div style="display:flex;justify-content:space-between;margin-bottom:10px;">
            <span style="color:#94a3b8;">📏 {t("height")}</span>
            <span style="color:#a5b4fc;font-weight:700;">{h} cm</span>
        </div>
        <div style="display:flex;justify-content:space-between;margin-bottom:10px;">
            <span style="color:#94a3b8;">📊 {t("bmi")}</span>
            <span style="color:{bc};font-weight:700;">{bmi} ({bl})</span>
        </div>
        <div style="display:flex;justify-content:space-between;">
            <span style="color:#94a3b8;">🎯 {t("goal")}</span>
            <span style="color:#a5b4fc;font-weight:700;">{gl}</span>
        </div>
    </div>
    """,
        unsafe_allow_html=True,
    )

with right:
    st.markdown(
        f'<div class="section-header"><span class="icon">✏️</span> {t("profile_details")}</div>',
        unsafe_allow_html=True,
    )

    defaults = {
        "age": a,
        "gender": g,
        "weight": w,
        "height": h,
        "goal": gl,
    }

    with st.form("profile_form"):
        r1c1, r1c2 = st.columns(2)
        with r1c1:
            age_val = st.number_input(
                f"🎂 {t('age')}", min_value=10, max_value=100, value=defaults["age"]
            )
        with r1c2:
            gender_val = st.selectbox(
                f"⚧️ {t('gender')}",
                [t("male"), t("female")],
                index=0 if defaults["gender"] == "Male" else 1,
            )

        r2c1, r2c2 = st.columns(2)
        with r2c1:
            weight_val = st.number_input(
                f"⚖️ {t('weight')} (kg)",
                min_value=30.0,
                max_value=300.0,
                value=defaults["weight"],
                step=0.5,
            )
        with r2c2:
            height_val = st.number_input(
                f"📏 {t('height')} (cm)",
                min_value=100.0,
                max_value=250.0,
                value=defaults["height"],
                step=0.5,
            )

        # Match localized goals
        goal_opts = [t("weight_loss"), t("muscle_gain"), t("maintenance")]
        # Match database value to options
        db_goal = defaults["goal"]
        if db_goal == "Weight Loss":
            goal_idx = 0
        elif db_goal == "Muscle Gain":
            goal_idx = 1
        else:
            goal_idx = 2

        goal_val = st.selectbox(f"🎯 {t('goal')}", goal_opts, index=goal_idx)

        activity = st.selectbox(
            f"🏃 {t('activity_level')}",
            [
                "Sedentary (desk job, little exercise)",
                "Lightly Active (1–3 workouts/week)",
                "Moderately Active (3–5 workouts/week)",
                "Very Active (6–7 workouts/week)",
                "Extra Active (physical job + daily exercise)",
            ],
        )

        r3c1, r3c2 = st.columns(2)
        with r3c1:
            water = st.number_input(
                f"💧 {t('daily_water_goal')}", min_value=0.5, max_value=10.0, value=2.5, step=0.1
            )
        with r3c2:
            sleep = st.number_input(
                f"😴 {t('sleep_goal')}", min_value=4.0, max_value=12.0, value=8.0, step=0.5
            )

        save = st.form_submit_button(t("save_changes"), type="primary")

        if save:
            # Map selected goal back to DB string
            g_db = "Weight Loss"
            if goal_val == t("muscle_gain"):
                g_db = "Muscle Gain"
            elif goal_val == t("maintenance"):
                g_db = "Maintenance"

            # Map gender
            g_gender = "Male" if gender_val == t("male") else "Female"

            try:
                cursor.execute(
                    """
                    UPDATE users
                    SET age=?, gender=?, weight=?, height=?, goal=?
                    WHERE username=?
                """,
                    (age_val, g_gender, weight_val, height_val, g_db, username),
                )
                conn.commit()

                # Also save to user_profile.csv
                os.makedirs("data", exist_ok=True)
                pd.DataFrame(
                    {
                        "username": [username],
                        "age": [age_val],
                        "gender": [g_gender],
                        "weight": [weight_val],
                        "height": [height_val],
                        "goal": [g_db],
                        "activity": [activity],
                        "water_goal": [water],
                        "sleep_goal": [sleep],
                        "updated": [str(date.today())],
                    }
                ).to_csv("data/user_profile.csv", index=False)

                st.success("✅ Profile updated successfully!")
                st.rerun()

            except Exception as e:
                st.error(f"Error updating: {str(e)}")

# ── METABOLIC HEALTH SUMMARY ─────────────────────────────────
st.markdown(
    """
<div class="section-header" style="margin-top:20px;"><span class="icon">📊</span> Health Summary</div>
""",
    unsafe_allow_html=True,
)

sc1, sc2, sc3, sc4 = st.columns(4)
bmi_c = "#10b981" if 18.5 <= bmi < 25 else "#f59e0b"
with sc1:
    st.markdown(
        f'<div class="stat-card"><span class="stat-icon">📊</span><div class="stat-value" style="color:{bmi_c};">{bmi}</div><div class="stat-label">{t("bmi")}</div></div>',
        unsafe_allow_html=True,
    )
with sc2:
    st.markdown(
        f'<div class="stat-card"><span class="stat-icon">🔥</span><div class="stat-value">{bmr_init}</div><div class="stat-label">{t("bmr_lbl")}</div></div>',
        unsafe_allow_html=True,
    )
with sc3:
    st.markdown(
        f'<div class="stat-card"><span class="stat-icon">⚡</span><div class="stat-value">{tdee_init}</div><div class="stat-label">{t("tdee_lbl")}</div></div>',
        unsafe_allow_html=True,
    )
with sc4:
    st.markdown(
        f'<div class="stat-card"><span class="stat-icon">🎯</span><div class="stat-value">{target_cals_init}</div><div class="stat-label">{t("target_calories")}</div></div>',
        unsafe_allow_html=True,
    )

# ── AI GOAL ADVISOR (NEW AI FEATURE) ─────────────────────────
st.write("")
st.markdown(
    f'<div class="section-header"><span class="icon">🤖</span> {t("ai_goal_advisor")}</div>',
    unsafe_allow_html=True,
)

advisor_btn_lbl = t("ai_metabolism_btn")

if st.button(f"🧠 {advisor_btn_lbl}", type="secondary", use_container_width=True):
    with st.spinner(t("loading")):
        prompt = f"""
The user has updated their profile details:
- Age: {a}
- Gender: {g}
- Weight: {w} kg
- Height: {h} cm
- Goal: {gl}
- Activity Level: {activity}
- Water Target: {user.get("water_goal", 2.5) if user is not None else 2.5} L/day
- Sleep Target: {user.get("sleep_goal", 8.0) if user is not None else 8.0} hrs/night
- BMR: {bmr_init} kcal/day
- TDEE: {tdee_init} kcal/day
- Target Calorie Intake: {target_cals_init} kcal/day

As an AI Fitness Advisor, provide a comprehensive review of this profile:
1. Assess the target calories relative to their BMR/TDEE and goal. Are they healthy and realistic?
2. Give daily protein, carbohydrate, and fat ratio suggestions.
3. Assess their sleep and water targets.
Keep the advice motivational, concise, and structured with bullet points.
"""
        sys_p = "You are a professional holistic fitness and metabolism coach. Respond in the requested language."
        advisor_res = ai_helper.get_ai_response(prompt, sys_p)

        st.markdown(ai_helper.provider_badge(), unsafe_allow_html=True)
        st.markdown(
            f"""
        <div class="info-card" style="padding:20px;border-left:4px solid #10b981;">
            <h4 style="margin-top:0;color:#10b981;">📋 AI Goal Assessment</h4>
            <div>{advisor_res}</div>
        </div>
        """,
            unsafe_allow_html=True,
        )

conn.close()
