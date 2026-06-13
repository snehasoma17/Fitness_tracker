import streamlit as st

# ==========================
# DASHBOARD PAGE
# ==========================

st.set_page_config(
    page_title="Dashboard",
    page_icon="🏠",
    layout="wide"
)

# Hero Section
st.markdown("""
<div style="
padding:30px;
border-radius:20px;
background:linear-gradient(135deg,#2563eb,#7c3aed);
color:white;
text-align:center;
margin-bottom:25px;
">
    <h1>🏋️ AI Fitness Tracker</h1>
    <h3>Your Personal AI Fitness & Nutrition Coach</h3>
    <p>
        Track Workouts • Generate Diet Plans • Analyze Food Images • AI Coaching
    </p>
</div>
""", unsafe_allow_html=True)

# ==========================
# QUICK STATS
# ==========================

st.subheader("📊 Today's Overview")

c1, c2, c3, c4 = st.columns(4)

with c1:
    st.metric("🔥 Calories Goal", "2200")

with c2:
    st.metric("💪 Protein Goal", "140g")

with c3:
    st.metric("⚖️ Weight", "70 kg")

with c4:
    st.metric("🚶 Daily Steps", "8500")

st.divider()

# ==========================
# AI FEATURES
# ==========================

st.subheader("🚀 AI Features")

f1, f2, f3, f4 = st.columns(4)

with f1:
    st.info("🤖 AI Coach")

with f2:
    st.info("🥗 Diet Planner")

with f3:
    st.info("💪 Workout Planner")

with f4:
    st.info("📸 Food Scanner")

st.divider()

# ==========================
# DAILY PROGRESS
# ==========================

st.subheader("🎯 Daily Progress")

progress = 70
st.progress(progress)

st.success(
    f"You're {progress}% toward today's fitness goal. Keep going!"
)

st.divider()

# ==========================
# WEEKLY ACTIVITY
# ==========================

st.subheader("📈 Weekly Activity")

chart_data = {
    "Workouts": [2, 4, 5, 3, 6, 7, 4]
}

st.bar_chart(chart_data)

st.divider()

# ==========================
# FITNESS SCORE
# ==========================

st.subheader("🧠 Fitness Score")

fitness_score = 74

st.metric(
    label="Fitness Score",
    value=f"{fitness_score}/100"
)

if fitness_score >= 80:
    st.success("Excellent progress! Keep it up 🔥")
elif fitness_score >= 60:
    st.info("Good progress 👍 Stay consistent.")
else:
    st.warning("Let's improve your fitness habits this week.")

st.divider()

# ==========================
# AI FITNESS TIP
# ==========================

st.subheader("💡 AI Fitness Tip")

st.info(
    "Aim for 1.6–2.2g of protein per kg of body weight daily to support muscle growth and recovery."
)

# ==========================
# MOTIVATION
# ==========================

st.subheader("🏆 Daily Motivation")

st.success(
    "Small daily improvements lead to big long-term results. Stay consistent!"
)