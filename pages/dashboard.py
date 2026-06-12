import streamlit as st
import sqlite3
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

st.set_page_config(page_title="Dashboard", page_icon="🏠", layout="wide")

# Load CSS
try:
    with open("data/style.css") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
except Exception:
    pass

username = st.session_state.get("username", "")
if not username:
    st.markdown("""<div class="hero-card">
    <h1>🔒 Access Denied</h1>
    <h3>Please login from the main page to view your dashboard.</h3>
    </div>""", unsafe_allow_html=True)
    st.stop()

conn = sqlite3.connect("fitness.db", check_same_thread=False)

# ── Load Data ─────────────────────────────────────────────
user_df  = pd.read_sql(f"SELECT * FROM users WHERE username='{username}'", conn)
if user_df.empty:
    st.error("User not found in database."); st.stop()
user = user_df.iloc[0]

workout_df = pd.read_sql(f"SELECT * FROM workouts WHERE username='{username}'", conn)
weight_df  = pd.read_sql(f"SELECT * FROM weight_log WHERE username='{username}' ORDER BY date", conn)
meals_df   = pd.read_sql(f"SELECT * FROM meals WHERE username='{username}'", conn)

current_weight  = float(user["weight"])
height_cm       = float(user["height"])
bmi             = round(current_weight / ((height_cm / 100) ** 2), 1)
total_workouts  = len(workout_df)
total_calories  = int(meals_df["calories"].sum()) if not meals_df.empty else 0
fitness_score   = min(50 + total_workouts * 2, 100)

if bmi < 18.5:   bmi_label, bmi_color = "Underweight", "#f59e0b"
elif bmi < 25:   bmi_label, bmi_color = "Healthy ✓",   "#10b981"
elif bmi < 30:   bmi_label, bmi_color = "Overweight",   "#f59e0b"
else:            bmi_label, bmi_color = "Obese",         "#ef4444"

# ── PAGE HEADER ────────────────────────────────────────────
st.markdown(f"""
<div class="hero-card" style="padding:32px 36px; text-align:left; display:flex; align-items:center; gap:24px;">
    <div style="font-size:4rem;">🏠</div>
    <div>
        <h1 style="margin:0; font-size:2rem !important;">Fitness Dashboard</h1>
        <h3 style="margin:0; font-size:1rem !important; color:#64748b !important;">
            Welcome back, <span style="color:#a5b4fc;">{username}</span> 👋 — Here's your health overview
        </h3>
    </div>
</div>
""", unsafe_allow_html=True)

# ── STAT CARDS ─────────────────────────────────────────────
st.markdown('<div class="section-header"><span class="icon">📊</span> Key Metrics</div>', unsafe_allow_html=True)

c1, c2, c3, c4, c5 = st.columns(5)
metrics = [
    (c1, "🏋️", total_workouts, "Total Workouts"),
    (c2, "⚖️", f"{current_weight} kg", "Body Weight"),
    (c3, "📏", bmi, "BMI Score"),
    (c4, "🔥", f"{total_calories} kcal", "Calories Logged"),
    (c5, "⭐", f"{fitness_score}/100", "Fitness Score"),
]
for col, icon, val, label in metrics:
    with col:
        st.markdown(f"""
        <div class="stat-card">
            <span class="stat-icon">{icon}</span>
            <div class="stat-value">{val}</div>
            <div class="stat-label">{label}</div>
        </div>
        """, unsafe_allow_html=True)

st.write("")

# ── PROFILE SUMMARY ────────────────────────────────────────
st.markdown('<div class="section-header"><span class="icon">👤</span> Profile Overview</div>', unsafe_allow_html=True)

p1, p2, p3, p4 = st.columns(4)
profile_items = [
    (p1, "🎯", "Fitness Goal", user["goal"]),
    (p2, "⚧️", "Gender",       user["gender"]),
    (p3, "📐", "Height",       f"{height_cm} cm"),
    (p4, f"<span style='color:{bmi_color}'>●</span>", "BMI Status", bmi_label),
]
for col, icon, label, val in profile_items:
    with col:
        st.markdown(f"""
        <div class="info-card">
            <div class="info-label">{icon} {label}</div>
            <div class="info-value">{val}</div>
        </div>
        """, unsafe_allow_html=True)

st.write("")

# ── CHARTS ─────────────────────────────────────────────────
left_col, right_col = st.columns([3, 2])

with left_col:
    st.markdown('<div class="section-header"><span class="icon">📈</span> Weight Progress</div>', unsafe_allow_html=True)
    if not weight_df.empty:
        fig = px.line(
            weight_df, x="date", y="weight", markers=True,
            labels={"date": "Date", "weight": "Weight (kg)"},
        )
        fig.update_traces(
            line=dict(color="#6366f1", width=3),
            marker=dict(size=9, color="#a5b4fc", line=dict(width=2, color="#6366f1")),
            fill="tozeroy", fillcolor="rgba(99,102,241,0.07)"
        )
        fig.update_layout(
            paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
            font=dict(color="#94a3b8", family="Plus Jakarta Sans"),
            xaxis=dict(gridcolor="rgba(255,255,255,0.05)", showline=False, tickfont=dict(color="#64748b")),
            yaxis=dict(gridcolor="rgba(255,255,255,0.05)", showline=False, tickfont=dict(color="#64748b")),
            margin=dict(l=0, r=0, t=10, b=0), height=280,
        )
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.markdown('<div class="info-card" style="text-align:center;padding:40px;"><div style="font-size:2.5rem">📭</div><div class="info-value" style="margin-top:10px;">No weight records yet</div><div class="info-label">Log your weight from the Progress page</div></div>', unsafe_allow_html=True)

with right_col:
    st.markdown('<div class="section-header"><span class="icon">🏃</span> Workout Breakdown</div>', unsafe_allow_html=True)
    if not workout_df.empty and "exercise" in workout_df.columns:
        exercise_counts = workout_df["exercise"].value_counts().head(5).reset_index()
        exercise_counts.columns = ["Exercise", "Count"]
        fig2 = px.bar(
            exercise_counts, x="Count", y="Exercise", orientation="h",
            color="Count", color_continuous_scale=["#312e81","#6366f1","#a5b4fc"],
        )
        fig2.update_layout(
            paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
            font=dict(color="#94a3b8", family="Plus Jakarta Sans"),
            xaxis=dict(gridcolor="rgba(255,255,255,0.05)", tickfont=dict(color="#64748b")),
            yaxis=dict(gridcolor="rgba(255,255,255,0.05)", tickfont=dict(color="#94a3b8")),
            coloraxis_showscale=False, margin=dict(l=0, r=0, t=10, b=0), height=280,
        )
        st.plotly_chart(fig2, use_container_width=True)
    else:
        st.markdown('<div class="info-card" style="text-align:center;padding:40px;"><div style="font-size:2.5rem">🏋️</div><div class="info-value" style="margin-top:10px;">No workouts logged</div><div class="info-label">Add workouts from the Workout Planner</div></div>', unsafe_allow_html=True)

# ── RECENT WORKOUTS TABLE ──────────────────────────────────
st.markdown('<div class="section-header"><span class="icon">📋</span> Recent Workout Sessions</div>', unsafe_allow_html=True)
if not workout_df.empty:
    display_df = workout_df.tail(8).copy()
    if "username" in display_df.columns:
        display_df = display_df.drop(columns=["username"])
    st.dataframe(display_df, use_container_width=True, hide_index=True)
else:
    st.markdown('<div class="info-card" style="text-align:center;padding:32px;"><div style="font-size:2rem">📭</div><p style="margin-top:8px;">No workout history found. Start logging today!</p></div>', unsafe_allow_html=True)

# ── CALORIE CHART ──────────────────────────────────────────
if not meals_df.empty:
    st.markdown('<div class="section-header"><span class="icon">🍽️</span> Calorie Intake Trend</div>', unsafe_allow_html=True)
    calorie_trend = meals_df.groupby("date")["calories"].sum().reset_index()
    fig3 = px.area(
        calorie_trend, x="date", y="calories",
        labels={"date": "Date", "calories": "Total Calories"},
        color_discrete_sequence=["#8b5cf6"],
    )
    fig3.update_traces(fillcolor="rgba(139,92,246,0.1)", line=dict(color="#8b5cf6", width=2))
    fig3.update_layout(
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color="#94a3b8", family="Plus Jakarta Sans"),
        xaxis=dict(gridcolor="rgba(255,255,255,0.05)", tickfont=dict(color="#64748b")),
        yaxis=dict(gridcolor="rgba(255,255,255,0.05)", tickfont=dict(color="#64748b")),
        margin=dict(l=0, r=0, t=10, b=0), height=240,
    )
    st.plotly_chart(fig3, use_container_width=True)

# ── AI INSIGHT ─────────────────────────────────────────────
st.markdown('<div class="section-header"><span class="icon">🧠</span> AI Health Insight</div>', unsafe_allow_html=True)

score_pct = fitness_score
st.markdown(f"""
<div class="info-card" style="margin-bottom:16px;">
    <div class="info-label">🎯 Fitness Score Progress</div>
    <div style="display:flex;align-items:center;gap:14px;margin-top:8px;">
        <div class="progress-bar-wrap" style="flex:1;">
            <div class="progress-bar-fill" style="width:{score_pct}%;"></div>
        </div>
        <div class="stat-value" style="font-size:1.4rem;">{score_pct}/100</div>
    </div>
</div>
""", unsafe_allow_html=True)

if total_workouts >= 10:
    st.success("✅ **Excellent Consistency!** Your workout frequency is outstanding. Focus on increasing protein intake and tracking recovery metrics.")
elif total_workouts >= 5:
    st.warning("⚡ **Good Progress!** You're building solid habits. Try adding one extra workout session per week to accelerate results.")
else:
    st.info("🚀 **Just Getting Started!** Aim for at least 3 workouts this week. Consistency is the key to transformation!")

# ── MOTIVATION ─────────────────────────────────────────────
import random
quotes = [
    "💪 \"The only bad workout is the one that didn't happen.\"",
    "🔥 \"Small daily improvements are the key to staggering long-term results.\"",
    "🎯 \"Your body achieves what your mind believes.\"",
    "⚡ \"Don't stop when you're tired. Stop when you're done.\"",
    "🌟 \"Take care of your body — it's the only place you have to live.\"",
]
st.markdown(f"""
<div class="animated-banner" style="margin-top:24px;">
    {random.choice(quotes)}
</div>
""", unsafe_allow_html=True)

conn.close()