import streamlit as st
import sqlite3
import pandas as pd
import os
from datetime import date

st.set_page_config(page_title="My Profile", page_icon="👤", layout="wide")
try:
    with open("data/style.css") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
except Exception:
    pass

username = st.session_state.get("username", "")
if not username:
    st.warning("🔒 Please login first."); st.stop()

conn = sqlite3.connect("fitness.db", check_same_thread=False)
cursor = conn.cursor()

# Load current user data
user_df = pd.read_sql(f"SELECT * FROM users WHERE username='{username}'", conn)
user = user_df.iloc[0] if not user_df.empty else None

# ── PAGE HEADER ──────────────────────────────────────────────
st.markdown(f"""
<div class="hero-card" style="padding:28px 36px;display:flex;align-items:center;gap:24px;">
    <div style="font-size:4rem;">👤</div>
    <div>
        <h1 style="margin:0;font-size:2rem !important;">My Profile</h1>
        <h3 style="margin:0;font-size:1rem !important;color:#64748b !important;">
            Manage your personal details and fitness profile — <span style="color:#a5b4fc;">@{username}</span>
        </h3>
    </div>
</div>
""", unsafe_allow_html=True)

# ── PROFILE PHOTO & EDIT FORM ────────────────────────────────
left, right = st.columns([2, 3])

with left:
    st.markdown('<div class="section-header"><span class="icon">📸</span> Profile Photo</div>', unsafe_allow_html=True)
    photo_path = f"data/photos/{username}_profile.jpg"
    if os.path.exists(photo_path):
        st.image(photo_path, caption="Your current profile photo", use_container_width=True)
    else:
        st.markdown("""
        <div class="info-card" style="text-align:center;padding:40px;">
            <div style="font-size:4rem;">🧑</div>
            <div class="info-label" style="margin-top:12px;">No photo uploaded</div>
        </div>
        """, unsafe_allow_html=True)

    uploaded_photo = st.file_uploader("Upload Profile Photo", type=["jpg", "jpeg", "png"])
    if uploaded_photo:
        os.makedirs("data/photos", exist_ok=True)
        with open(photo_path, "wb") as f:
            f.write(uploaded_photo.read())
        st.success("✅ Profile photo updated!")
        st.image(photo_path, use_container_width=True)

    # Quick stats from DB
    if user is not None:
        h = float(user.get("height", 170))
        w = float(user.get("weight", 70))
        bmi = round(w / ((h / 100) ** 2), 1)
        if bmi < 18.5:   bl, bc = "Underweight", "#f59e0b"
        elif bmi < 25:   bl, bc = "Healthy ✓",   "#10b981"
        elif bmi < 30:   bl, bc = "Overweight",   "#f59e0b"
        else:            bl, bc = "Obese",         "#ef4444"

        st.write("")
        st.markdown(f"""
        <div class="info-card">
            <div class="info-label">📊 Quick Stats</div>
            <br>
            <div style="display:flex;justify-content:space-between;margin-bottom:10px;">
                <span style="color:#94a3b8;">⚖️ Weight</span>
                <span style="color:#a5b4fc;font-weight:700;">{w} kg</span>
            </div>
            <div style="display:flex;justify-content:space-between;margin-bottom:10px;">
                <span style="color:#94a3b8;">📏 Height</span>
                <span style="color:#a5b4fc;font-weight:700;">{h} cm</span>
            </div>
            <div style="display:flex;justify-content:space-between;margin-bottom:10px;">
                <span style="color:#94a3b8;">📊 BMI</span>
                <span style="color:{bc};font-weight:700;">{bmi} ({bl})</span>
            </div>
            <div style="display:flex;justify-content:space-between;">
                <span style="color:#94a3b8;">🎯 Goal</span>
                <span style="color:#a5b4fc;font-weight:700;">{user.get("goal","—")}</span>
            </div>
        </div>
        """, unsafe_allow_html=True)

with right:
    st.markdown('<div class="section-header"><span class="icon">✏️</span> Update Profile Details</div>', unsafe_allow_html=True)

    defaults = {
        "age":    int(user.get("age", 22))    if user is not None else 22,
        "gender": str(user.get("gender","Male")) if user is not None else "Male",
        "weight": float(user.get("weight", 70.0)) if user is not None else 70.0,
        "height": float(user.get("height", 170.0)) if user is not None else 170.0,
        "goal":   str(user.get("goal", "Weight Loss")) if user is not None else "Weight Loss",
    }

    with st.form("profile_form"):
        r1c1, r1c2 = st.columns(2)
        with r1c1:
            age = st.number_input("🎂 Age", min_value=10, max_value=100, value=defaults["age"])
        with r1c2:
            gender = st.selectbox("⚧️ Gender", ["Male", "Female"],
                                  index=0 if defaults["gender"] == "Male" else 1)

        r2c1, r2c2 = st.columns(2)
        with r2c1:
            weight = st.number_input("⚖️ Weight (kg)", min_value=30.0, max_value=300.0,
                                     value=defaults["weight"], step=0.5)
        with r2c2:
            height = st.number_input("📏 Height (cm)", min_value=100.0, max_value=250.0,
                                     value=defaults["height"], step=0.5)

        goal_opts = ["Weight Loss", "Muscle Gain", "Maintain Weight"]
        goal_idx = goal_opts.index(defaults["goal"]) if defaults["goal"] in goal_opts else 0
        goal = st.selectbox("🎯 Fitness Goal", goal_opts, index=goal_idx)

        activity = st.selectbox("🏃 Activity Level",
                                 ["Sedentary (desk job, little exercise)",
                                  "Lightly Active (1–3 workouts/week)",
                                  "Moderately Active (3–5 workouts/week)",
                                  "Very Active (6–7 workouts/week)",
                                  "Extra Active (physical job + daily exercise)"])

        r3c1, r3c2 = st.columns(2)
        with r3c1:
            water = st.number_input("💧 Daily Water Goal (L)", min_value=0.5, max_value=10.0,
                                    value=2.5, step=0.1)
        with r3c2:
            sleep = st.number_input("😴 Sleep Goal (hrs/night)", min_value=4.0, max_value=12.0,
                                    value=8.0, step=0.5)

        save = st.form_submit_button("💾 Save Changes", type="primary")

        if save:
            try:
                cursor.execute("""
                    UPDATE users
                    SET age=?, gender=?, weight=?, height=?, goal=?
                    WHERE username=?
                """, (age, gender, weight, height, goal, username))
                conn.commit()

                # Also save extended profile to CSV
                os.makedirs("data", exist_ok=True)
                pd.DataFrame({
                    "username": [username], "age": [age], "gender": [gender],
                    "weight": [weight], "height": [height], "goal": [goal],
                    "activity": [activity], "water_goal": [water],
                    "sleep_goal": [sleep], "updated": [str(date.today())]
                }).to_csv("data/user_profile.csv", index=False)

                # Compute & show results
                bmi_new = round(weight / ((height / 100) ** 2), 1)
                activity_mult = {"Sedentary": 1.2, "Lightly": 1.375, "Moderately": 1.55, "Very": 1.725, "Extra": 1.9}
                mult = 1.55
                for k, v in activity_mult.items():
                    if k.lower() in activity.lower():
                        mult = v; break
                bmr = round(10*weight + 6.25*height - 5*age + (5 if gender=="Male" else -161))
                tdee = round(bmr * mult)

                st.success("✅ Profile updated successfully!")

                st.markdown(f"""
                <div class="section-header" style="margin-top:20px;"><span class="icon">📊</span> Updated Health Summary</div>
                """, unsafe_allow_html=True)

                sc1, sc2, sc3, sc4 = st.columns(4)
                bmi_c = "#10b981" if 18.5 <= bmi_new < 25 else "#f59e0b"
                with sc1:
                    st.markdown(f'<div class="stat-card"><span class="stat-icon">📊</span><div class="stat-value" style="color:{bmi_c};">{bmi_new}</div><div class="stat-label">BMI</div></div>', unsafe_allow_html=True)
                with sc2:
                    st.markdown(f'<div class="stat-card"><span class="stat-icon">🔥</span><div class="stat-value">{bmr}</div><div class="stat-label">BMR (kcal/day)</div></div>', unsafe_allow_html=True)
                with sc3:
                    st.markdown(f'<div class="stat-card"><span class="stat-icon">⚡</span><div class="stat-value">{tdee}</div><div class="stat-label">TDEE (kcal/day)</div></div>', unsafe_allow_html=True)
                with sc4:
                    deficit = tdee - 500 if goal == "Weight Loss" else tdee + 300 if goal == "Muscle Gain" else tdee
                    st.markdown(f'<div class="stat-card"><span class="stat-icon">🎯</span><div class="stat-value">{deficit}</div><div class="stat-label">Target Calories</div></div>', unsafe_allow_html=True)

            except Exception as e:
                st.error(f"Error updating: {str(e)}")

conn.close()