import streamlit as st
import ai_helper
from utils.theme import load_css
from utils.i18n import t

load_css()

st.set_page_config(
    page_title="AI Diet Planner",
    page_icon="🥗",
    layout="wide"
)

st.title("🥗 AI Diet Planner")
st.caption("Generate personalized nutrition plans using AI")

# User Inputs
col1, col2 = st.columns(2)

with col1:
    age = st.number_input("Age", 10, 100, 25)
    weight = st.number_input("Weight (kg)", 20.0, 300.0, 70.0)
    height = st.number_input("Height (cm)", 100.0, 250.0, 170.0)
    gender = st.selectbox("Gender", ["Male", "Female"])

with col2:
    goal = st.selectbox(
        "Goal",
        [
            "Fat Loss",
            "Muscle Gain",
            "Weight Maintenance"
        ]
    )

    activity = st.selectbox(
        "Activity Level",
        [
            "Sedentary",
            "Lightly Active",
            "Moderately Active",
            "Very Active"
        ]
    )

    diet_type = st.selectbox(
        "Diet Type",
        [
            "Balanced",
            "Vegetarian",
            "Vegan",
            "Keto",
            "High Protein"
        ]
    )

meals_per_day = st.slider(
    "Meals Per Day",
    3,
    6,
    4
)

allergies = st.text_input(
    "Allergies / Intolerances"
)

extra_notes = st.text_area(
    "Extra Notes"
)

# Basic BMR Calculation
if gender == "Male":
    bmr = 10 * weight + 6.25 * height - 5 * age + 5
else:
    bmr = 10 * weight + 6.25 * height - 5 * age - 161

activity_multipliers = {
    "Sedentary": 1.2,
    "Lightly Active": 1.375,
    "Moderately Active": 1.55,
    "Very Active": 1.725
}

tdee = bmr * activity_multipliers[activity]

if st.button("🚀 Generate Diet Plan"):

    prompt = f"""
Create a comprehensive, personalised {meals_per_day}-meal-per-day diet plan for the following person:

Profile:
- Age: {age}
- Gender: {gender}
- Weight: {weight} kg
- Height: {height} cm
- Goal: {goal}
- Activity: {activity}
- Diet Type: {diet_type}
- Allergies: {allergies if allergies else 'None'}
- BMR: {round(bmr)}
- TDEE: {round(tdee)}
- Extra Notes: {extra_notes if extra_notes else 'None'}

Provide:
1. Daily calories and macros
2. Meal plan
3. Grocery list
4. Hydration plan
5. Meal timing
6. Supplements
7. Practical tips
"""

    system_prompt = """
You are a Registered Dietitian and Sports Nutritionist.
Create detailed, practical, science-based diet plans.
Use tables and emojis.
"""

    try:

        result = ai_helper.get_ai_response(
            prompt,
            system_prompt,
            max_tokens=2000
        )

        provider = st.session_state.get(
            "ai_provider",
            "OpenAI"
        )

        model = st.session_state.get(
            "ai_model",
            "gpt-4o-mini"
        )

        st.success("Diet Plan Generated")

        st.info(
            f"Provider: {provider} | Model: {model}"
        )

        st.markdown(result)

    except Exception as e:

        st.error(
            f"Error generating diet plan: {e}"
        )