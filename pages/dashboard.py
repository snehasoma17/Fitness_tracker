import streamlit as st
import pandas as pd
import utils.theme
import ai_helper
from utils.theme import load_css
from utils.i18n import t

# =====================================
# PAGE CONFIG
# =====================================

st.set_page_config(
    page_title="Dashboard",
    page_icon="🏠",
    layout="wide"
)

# =====================================
# LOAD CSS
# =====================================

load_css()

# =====================================
# DEMO DATA
# =====================================

calories_goal = 2200
protein_goal = 140
weight = 70
steps = 8500

progress = 70
fitness_score = 74

weekly_workouts = pd.DataFrame({
    "Day": ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"],
    "Workouts": [2, 4, 5, 3, 6, 7, 4]
})

# =====================================
# HERO SECTION
# =====================================

st.markdown(f"""
<div class="hero-card">
    <h1>🏋️ {t("app_title")}</h1>
    <h3>Your Personal AI Fitness & Nutrition Coach</h3>
    <p>
        Track Workouts • Generate Diet Plans • AI Coaching • Progress Analytics
    </p>
</div>
""", unsafe_allow_html=True)

# =====================================
# TODAY OVERVIEW
# =====================================

st.markdown(f"## 📊 {t('today_overview')}")

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric(
        f"🔥 {t('calories_goal')}",
        f"{calories_goal} kcal"
    )

with col2:
    st.metric(
        f"💪 {t('protein_goal')}",
        f"{protein_goal} g"
    )

with col3:
    st.metric(
        f"⚖️ {t('weight')}",
        f"{weight} kg"
    )

with col4:
    st.metric(
        f"🚶 {t('daily_steps')}",
        f"{steps}"
    )

st.divider()

# =====================================
# AI FEATURES
# =====================================

st.markdown(f"## 🚀 {t('ai_features')}")

f1, f2, f3, f4 = st.columns(4)

with f1:
    st.success(f"🤖 {t('ai_coach')}")

with f2:
    st.success(f"🥗 {t('diet_planner')}")

with f3:
    st.success(f"💪 {t('workout_planner')}")

with f4:
    st.success(f"📸 {t('food_scanner')}")

st.divider()

# =====================================
# DAILY PROGRESS
# =====================================

st.markdown(f"## 🎯 {t('daily_progress')}")

st.progress(progress)

st.info(
    f"You are {progress}% toward today's fitness goal."
)

st.divider()

# =====================================
# CHARTS
# =====================================

left, right = st.columns(2)

with left:

    st.markdown(f"### 📈 {t('weekly_activity')}")

    st.bar_chart(
        weekly_workouts.set_index("Day")
    )

with right:

    st.markdown(f"### 🧠 {t('fitness_score')}")

    st.metric(
        label=t("fitness_score"),
        value=f"{fitness_score}/100"
    )

    if fitness_score >= 80:
        st.success(
            "Excellent progress! Keep pushing 🔥"
        )

    elif fitness_score >= 60:
        st.info(
            "Good progress 👍 Stay consistent."
        )

    else:
        st.warning(
            "Focus on improving your daily habits."
        )

st.divider()

# =====================================
# FITNESS TIP
# =====================================

st.markdown(f"## 💡 {t('fitness_tip')}")

st.info(
    """
    Aim for **1.6–2.2g of protein per kg**
    of body weight daily to support
    muscle growth and recovery.
    """
)

st.divider()

# =====================================
# MOTIVATION
# =====================================

st.markdown(f"## 🏆 {t('motivation')}")

st.success(
    """
    Small daily improvements lead to
    big long-term results.

    Stay consistent and trust the process 🚀
    """
)

st.divider()

# =====================================
# QUICK ACTIONS
# =====================================

st.markdown("## ⚡ Quick Actions")

a1, a2, a3, a4 = st.columns(4)

with a1:
    st.button(
        "🥗 Create Diet Plan",
        width="stretch"
    )

with a2:
    st.button(
        "💪 Generate Workout",
        width="stretch"
    )

with a3:
    st.button(
        "📊 View Progress",
        width="stretch"
    )

with a4:
    st.button(
        "🤖 Ask AI Coach",
        width="stretch"
    )