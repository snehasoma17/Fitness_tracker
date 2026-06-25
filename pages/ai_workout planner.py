import streamlit as st

import ai_helper
from utils.i18n import t
from utils.navigation import initialize_page

# 1. Initialize Page and Sidebar
initialize_page(t("ai_workout_planner"), "💪")

# ── PAGE HEADER ─────────────────────────────────────────────
st.markdown(
    f"""
<div class="hero-card" style="padding:28px 36px;">
    <h1>💪 {t("ai_workout_planner")}</h1>
    <p style="color:#94a3b8;">
        {t("workout_plan_generated") if t("workout_plan_generated") != "workout_plan_generated" else "Generate personalized training plans using AI"}
    </p>
</div>
""",
    unsafe_allow_html=True,
)

st.write("")

# ── FORM INPUTS ─────────────────────────────────────────────
col1, col2 = st.columns(2)

with col1:
    age = st.number_input(t("age"), min_value=10, max_value=100, value=25)
    weight = st.number_input(
        f"{t('weight')} (kg)", min_value=20.0, max_value=300.0, value=70.0, step=0.5
    )

with col2:
    goal_opts = [t("weight_loss"), t("muscle_gain"), t("maintenance")]
    goal = st.selectbox(t("goal"), goal_opts)

    days = st.slider(t("workout_days_label"), 1, 7, 4)

extra_notes = st.text_area(t("injury_notes"), placeholder="e.g. Knee pain, asthma, dumbbells only")

# ── GENERATION ──────────────────────────────────────────────
generate_btn_lbl = t("generate_workout")

if st.button("🚀 " + generate_btn_lbl, type="primary", use_container_width=True):
    with st.spinner(t("loading")):
        prompt = f"""
Create a highly professional and tailored {days}-day weekly workout plan for a person with the following profile:
- Age: {age}
- Weight: {weight} kg
- Goal: {goal}
- Training Days: {days} days per week
- Extra constraints/notes: {extra_notes if extra_notes else "None"}

Provide:
1. Weekly Schedule overview.
2. Complete exercise breakdown per day (Exercises, Sets, Reps, Rest time, and Cardio guidance).
3. Progression tips (how to increase difficulty over time).
4. Safe training guidelines (warm-up and cool-down).
"""
        sys_p = "You are a professional strength and conditioning coach. Use tables and emojis. Respond in the requested language."

        try:
            result = ai_helper.get_ai_response(prompt, sys_p, max_tokens=2200)

            st.markdown(ai_helper.provider_badge(), unsafe_allow_html=True)
            st.success("✓ " + t("workout_plan_generated"))
            st.markdown(result)
        except Exception as e:
            st.error(f"Error generating workout: {e}")
