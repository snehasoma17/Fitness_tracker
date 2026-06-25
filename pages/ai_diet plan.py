import streamlit as st

import ai_helper
from utils.i18n import t
from utils.navigation import initialize_page

# 1. Initialize Page and Sidebar
initialize_page(t("ai_diet_plan"), "🥗")

lang = st.session_state.current_language

# ── PAGE HEADER ─────────────────────────────────────────────
st.markdown(
    f"""
<div class="hero-card" style="padding:28px 36px;">
    <h1>🥗 {t("ai_diet_plan")}</h1>
    <p style="color:#94a3b8;">
        {t("rag_subtitle") if t("rag_subtitle") != "rag_subtitle" else "Generate personalized nutrition plans using AI"}
    </p>
</div>
""",
    unsafe_allow_html=True,
)

st.write("")

# ── INPUTS ──────────────────────────────────────────────────
col1, col2 = st.columns(2)

with col1:
    age = st.number_input(t("age"), 10, 100, 25)
    weight = st.number_input(f"{t('weight')} (kg)", 20.0, 300.0, 70.0)
    height = st.number_input(f"{t('height')} (cm)", 100.0, 250.0, 170.0)

    gender_opts = [t("male"), t("female")]
    gender_val = st.selectbox(t("gender"), gender_opts)

with col2:
    goal_opts = [t("weight_loss"), t("muscle_gain"), t("maintenance")]
    goal = st.selectbox(t("goal"), goal_opts)

    # Activity level
    activity_opts = [
        t("activity_sedentary"),
        t("activity_light"),
        t("activity_moderate"),
        t("activity_very"),
    ]
    activity = st.selectbox(t("activity_level"), activity_opts)

    # Diet type
    diet_opts = [
        t("diet_balanced"),
        t("diet_vegetarian"),
        t("diet_vegan"),
        t("diet_keto"),
        t("diet_high_protein"),
    ]
    diet_type = st.selectbox(t("diet_type"), diet_opts)

meals_per_day = st.slider(t("meals_per_day"), 3, 6, 4)

allergies = st.text_input(t("allergies"), placeholder="e.g. Peanut, Lactose")

extra_notes = st.text_area(t("extra_notes"))

# Basic BMR / TDEE Calculation
db_gender = "Male" if gender_val == t("male") else "Female"
if db_gender == "Male":
    bmr = 10 * weight + 6.25 * height - 5 * age + 5
else:
    bmr = 10 * weight + 6.25 * height - 5 * age - 161

activity_multipliers = {
    activity_opts[0]: 1.2,
    activity_opts[1]: 1.375,
    activity_opts[2]: 1.55,
    activity_opts[3]: 1.725,
}
tdee = bmr * activity_multipliers.get(activity, 1.375)

# ── GENERATE PLAN ───────────────────────────────────────────
generate_btn_lbl = t("generate_diet")

if st.button("🚀 " + generate_btn_lbl, type="primary", use_container_width=True):
    with st.spinner(t("loading")):
        prompt = f"""
Create a comprehensive, personalised {meals_per_day}-meal-per-day diet plan for the following profile:
- Age: {age}
- Gender: {db_gender}
- Weight: {weight} kg
- Height: {height} cm
- Goal: {goal}
- Activity Level: {activity}
- Diet Type: {diet_type}
- Allergies: {allergies if allergies else "None"}
- BMR: {round(bmr)} kcal/day
- TDEE: {round(tdee)} kcal/day
- Extra Notes: {extra_notes if extra_notes else "None"}

Provide:
1. Daily calories and macro targets (Protein, Carbs, Fat) in a table.
2. Complete meal-by-meal schedule.
3. Grocery list.
4. Hydration guidelines.
5. Supplements recommendation (if needed).
6. Practical tips.
"""
        system_prompt = """
You are a Registered Dietitian and Sports Nutritionist.
Create detailed, practical, science-based diet plans.
Use markdown tables and emojis.
"""
        try:
            result = ai_helper.get_ai_response(prompt, system_prompt, max_tokens=2200)

            st.markdown(ai_helper.provider_badge(), unsafe_allow_html=True)
            st.success("✓ " + (t("success") if lang != "English" else "Diet Plan Generated!"))
            st.markdown(result)
        except Exception as e:
            st.error(f"Error generating plan: {e}")
