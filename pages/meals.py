import streamlit as st
import sqlite3
import pandas as pd
import plotly.express as px
import utils.theme
from datetime import date
from utils.theme import load_css

load_css()

import streamlit as st
import sqlite3
from datetime import datetime, date, timedelta

import plotly.graph_objects as go

import ai_helper
from utils.i18n import t


st.set_page_config(page_title="Workout Streak", page_icon="🔥", layout="wide")
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

# ── HEADER ──────────────────────────────────────────────────
st.markdown("""
<div class="hero-card" style="padding:28px 36px;text-align:left;display:flex;align-items:center;gap:24px;">
    <div style="font-size:3.5rem;">🔥</div>
    <div>
        <h1 style="margin:0;font-size:2rem !important;">Workout Streak</h1>
        <h3 style="margin:0;font-size:1rem !important;color:#64748b !important;">
            Track your consistency and keep your streak alive!
        </h3>
    </div>
</div>
""", unsafe_allow_html=True)

# ── LOAD DATA ────────────────────────────────────────────────
cursor.execute("""
    SELECT DISTINCT date FROM workouts WHERE username=? ORDER BY date DESC
""", (username,))
date_rows = [row[0] for row in cursor.fetchall()]

# ── STREAK CALCULATION ────────────────────────────────────────
streak = 0
longest_streak = 0
temp_streak = 0

if date_rows:
    streak = 1
    for i in range(len(date_rows) - 1):
        try:
            d1 = datetime.strptime(date_rows[i], "%Y-%m-%d")
            d2 = datetime.strptime(date_rows[i+1], "%Y-%m-%d")
            if (d1 - d2).days == 1:
                streak += 1
            else:
                break
        except Exception:
            break

    # Compute longest streak
    temp_streak = 1
    for i in range(len(date_rows) - 1):
        try:
            d1 = datetime.strptime(date_rows[i], "%Y-%m-%d")
            d2 = datetime.strptime(date_rows[i+1], "%Y-%m-%d")
            if (d1 - d2).days == 1:
                temp_streak += 1
                longest_streak = max(longest_streak, temp_streak)
            else:
                temp_streak = 1
        except Exception:
            temp_streak = 1
    longest_streak = max(longest_streak, temp_streak)

total_days = len(date_rows)
worked_this_week = sum(
    1 for d in date_rows
    if (date.today() - datetime.strptime(d, "%Y-%m-%d").date()).days < 7
) if date_rows else 0

# ── STATS ───────────────────────────────────────────────────
st.markdown('<div class="section-header"><span class="icon">📊</span> Streak Overview</div>', unsafe_allow_html=True)

s1, s2, s3, s4 = st.columns(4)
streak_emoji = "🔥" if streak >= 7 else ("⚡" if streak >= 3 else "💪")
with s1:
    st.markdown(f'<div class="stat-card" style="border-color:rgba(251,146,60,0.3);"><span class="stat-icon">{streak_emoji}</span><div class="stat-value" style="color:#fb923c;">{streak}</div><div class="stat-label">Current Streak (Days)</div></div>', unsafe_allow_html=True)
with s2:
    st.markdown(f'<div class="stat-card"><span class="stat-icon">🏆</span><div class="stat-value" style="color:#fbbf24;">{longest_streak}</div><div class="stat-label">Longest Streak</div></div>', unsafe_allow_html=True)
with s3:
    st.markdown(f'<div class="stat-card"><span class="stat-icon">📅</span><div class="stat-value">{total_days}</div><div class="stat-label">Total Active Days</div></div>', unsafe_allow_html=True)
with s4:
    st.markdown(f'<div class="stat-card"><span class="stat-icon">🗓️</span><div class="stat-value">{worked_this_week}/7</div><div class="stat-label">Days Active This Week</div></div>', unsafe_allow_html=True)

st.write("")

# ── STREAK GAUGE ─────────────────────────────────────────────
left_col, right_col = st.columns([2, 3])

with left_col:
    st.markdown('<div class="section-header"><span class="icon">🎯</span> Streak Goal</div>', unsafe_allow_html=True)
    goal = 30
    pct = min(streak / goal * 100, 100)
    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=streak,
        number={"suffix": " days", "font": {"color": "#fb923c", "size": 44, "family": "Plus Jakarta Sans"}},
        gauge={
            "axis": {"range": [0, goal], "tickcolor": "#475569", "tickfont": {"color": "#64748b"}},
            "bar": {"color": "#f97316", "thickness": 0.3},
            "bgcolor": "rgba(0,0,0,0)",
            "borderwidth": 0,
            "steps": [
                {"range": [0, 7],    "color": "rgba(99,102,241,0.08)"},
                {"range": [7, 14],   "color": "rgba(245,158,11,0.08)"},
                {"range": [14, 30],  "color": "rgba(249,115,22,0.1)"},
            ],
        },
        title={"text": f"<b>Goal: {goal}-Day Streak</b>", "font": {"color": "#94a3b8", "size": 14, "family": "Plus Jakarta Sans"}},
    ))
    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        font=dict(family="Plus Jakarta Sans"),
        height=280, margin=dict(l=20, r=20, t=10, b=10)
    )
    st.plotly_chart(fig, use_container_width="stretch")

    # Progress bar
    st.markdown(f"""
    <div class="info-card" style="text-align:center;">
        <div class="info-label">Progress to 30-Day Goal</div>
        <div class="progress-bar-wrap" style="margin:12px 0 6px;">
            <div class="progress-bar-fill" style="width:{pct:.0f}%;background:linear-gradient(90deg,#f97316,#fb923c,#fbbf24);"></div>
        </div>
        <div class="stat-value" style="font-size:1.2rem;color:#fb923c;">{pct:.0f}%</div>
    </div>
    """, unsafe_allow_html=True)

with right_col:
    st.markdown('<div class="section-header"><span class="icon">📅</span> Recent 14-Day Activity</div>', unsafe_allow_html=True)
    # Calendar heatmap for last 14 days
    active_dates = set(date_rows)
    today = date.today()
    cal_data = []
    for i in range(13, -1, -1):
        d = today - timedelta(days=i)
        ds = d.strftime("%Y-%m-%d")
        cal_data.append({
            "date": ds,
            "day": d.strftime("%a"),
            "active": 1 if ds in active_dates else 0,
            "label": d.strftime("%b %d"),
        })

    # Build grid display
    row1 = cal_data[:7]
    row2 = cal_data[7:]

    def day_cell(d):
        color = "rgba(249,115,22,0.7)" if d["active"] else "rgba(30,41,59,0.5)"
        icon  = "🔥" if d["active"] else "○"
        border = "rgba(249,115,22,0.4)" if d["active"] else "rgba(255,255,255,0.06)"
        return f"""
        <div style="text-align:center;background:{color};border:1px solid {border};
                    border-radius:12px;padding:12px 8px;min-width:60px;flex:1;">
            <div style="font-size:1.3rem;">{icon}</div>
            <div style="color:#e2e8f0;font-size:0.7rem;font-weight:600;margin-top:4px;">{d["day"]}</div>
            <div style="color:#94a3b8;font-size:0.65rem;">{d["label"][-2:]}</div>
        </div>"""

    row1_html = "".join(day_cell(d) for d in row1)
    row2_html = "".join(day_cell(d) for d in row2)
    st.markdown(f"""
    <div style="display:flex;gap:6px;margin-bottom:8px;">{row1_html}</div>
    <div style="display:flex;gap:6px;">{row2_html}</div>
    """, unsafe_allow_html=True)

    # Motivational message
    st.write("")
    if streak >= 14:
        msg, icon = "🏆 Outstanding! You're unstoppable — keep the fire burning!", "#fbbf24"
    elif streak >= 7:
        msg, icon = "🔥 Fantastic! One full week of consistency. You're building real habits!", "#fb923c"
    elif streak >= 3:
        msg, icon = "⚡ Great start! Keep going — you're building momentum!", "#6366f1"
    elif streak >= 1:
        msg, icon = "💪 Day 1 starts a journey. Show up tomorrow and start a streak!", "#10b981"
    else:
        msg, icon = "🚀 No active streak yet. Start today — your first workout is the most important!", "#64748b"

    st.markdown(f"""
    <div class="animated-banner" style="margin-top:16px;color:{icon} !important;font-size:1rem;">
        {msg}
    </div>
    """, unsafe_allow_html=True)

conn.close()
st.set_page_config(page_title="Meals Tracker", page_icon="🍽️", layout="wide")

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

# Ensure meals table has username column
try:
    cursor.execute("ALTER TABLE meals ADD COLUMN username TEXT")
    conn.commit()
except Exception:
    pass

# ── PAGE HEADER ────────────────────────────────────────────
st.markdown(f"""
<div class="hero-card" style="padding:28px 36px;text-align:left;display:flex;align-items:center;gap:24px;">
    <div style="font-size:3.5rem;">🍽️</div>
    <div>
        <h1 style="margin:0;font-size:2rem !important;">Meal Tracker</h1>
        <h3 style="margin:0;font-size:1rem !important;color:#64748b !important;">
            Log your daily nutrition and monitor calorie intake
        </h3>
    </div>
</div>
""", unsafe_allow_html=True)

# ── LOG MEAL FORM ──────────────────────────────────────────
st.markdown('<div class="section-header"><span class="icon">➕</span> Log a Meal</div>', unsafe_allow_html=True)

col_form, col_tips = st.columns([3, 2])

with col_form:
    with st.form("meal_form", clear_on_submit=True):
        f1, f2 = st.columns(2)
        with f1:
            meal_type = st.selectbox("🕐 Meal Type", ["🌅 Breakfast", "☀️ Lunch", "🌙 Dinner", "🍎 Snacks"])
        with f2:
            meal_date = st.date_input("📅 Date", value=date.today())

        food = st.text_input("🥘 Food / Dish Name", placeholder="e.g. Grilled Chicken with Brown Rice")

        c1, c2, c3 = st.columns(3)
        with c1:
            calories = st.number_input("🔥 Calories (kcal)", min_value=0, max_value=5000, value=0, step=10)
        with c2:
            protein = st.number_input("💪 Protein (g)", min_value=0, max_value=500, value=0, step=1)
        with c3:
            carbs = st.number_input("🍞 Carbs (g)", min_value=0, max_value=500, value=0, step=1)

        photo = st.file_uploader("📸 Attach Food Photo (optional)", type=["png", "jpg", "jpeg"])

        submitted = st.form_submit_button("💾 Save Meal", type="primary")

        if submitted:
            if not food.strip():
                st.error("Please enter the food name.")
            else:
                try:
                    cursor.execute("""
                        INSERT INTO meals (username, date, meal, calories)
                        VALUES (?, ?, ?, ?)
                    """, (username, str(meal_date), meal_type.split(" ", 1)[1], calories))
                    conn.commit()
                    st.success(f"✅ **{food}** logged successfully under {meal_type}!")
                    if photo:
                        st.image(photo, caption=f"📸 {food}", width=200)
                except Exception as e:
                    st.error(f"Error saving: {str(e)}")

with col_tips:
    st.markdown("""
    <div class="info-card" style="padding:24px;">
        <div class="info-label">💡 Calorie Reference Guide</div>
        <br>
        <table style="width:100%;color:#94a3b8;font-size:0.88rem;border-collapse:collapse;">
            <tr style="border-bottom:1px solid rgba(255,255,255,0.06);">
                <td style="padding:8px 4px;">🥣 Oatmeal (1 cup)</td>
                <td style="padding:8px 4px;text-align:right;color:#a5b4fc;font-weight:700;">~150 kcal</td>
            </tr>
            <tr style="border-bottom:1px solid rgba(255,255,255,0.06);">
                <td style="padding:8px 4px;">🍗 Chicken Breast (100g)</td>
                <td style="padding:8px 4px;text-align:right;color:#a5b4fc;font-weight:700;">~165 kcal</td>
            </tr>
            <tr style="border-bottom:1px solid rgba(255,255,255,0.06);">
                <td style="padding:8px 4px;">🥚 Boiled Egg (1 pc)</td>
                <td style="padding:8px 4px;text-align:right;color:#a5b4fc;font-weight:700;">~78 kcal</td>
            </tr>
            <tr style="border-bottom:1px solid rgba(255,255,255,0.06);">
                <td style="padding:8px 4px;">🍚 Rice (1 cup cooked)</td>
                <td style="padding:8px 4px;text-align:right;color:#a5b4fc;font-weight:700;">~206 kcal</td>
            </tr>
            <tr style="border-bottom:1px solid rgba(255,255,255,0.06);">
                <td style="padding:8px 4px;">🥑 Avocado (half)</td>
                <td style="padding:8px 4px;text-align:right;color:#a5b4fc;font-weight:700;">~120 kcal</td>
            </tr>
            <tr>
                <td style="padding:8px 4px;">🐟 Salmon (100g)</td>
                <td style="padding:8px 4px;text-align:right;color:#a5b4fc;font-weight:700;">~208 kcal</td>
            </tr>
        </table>
        <br>
        <div class="info-label">💧 Daily Water Goal: <span style="color:#38bdf8;font-weight:700;">8 glasses / 2L</span></div>
    </div>
    """, unsafe_allow_html=True)

# ── MEAL HISTORY ───────────────────────────────────────────
st.markdown('<div class="section-header"><span class="icon">📋</span> Meal History</div>', unsafe_allow_html=True)

try:
    meals_df = pd.read_sql(f"SELECT * FROM meals WHERE username='{username}' ORDER BY date DESC", conn)
except Exception:
    meals_df = pd.DataFrame()

if not meals_df.empty:
    # Today's summary cards
    today = str(date.today())
    today_df = meals_df[meals_df["date"] == today] if "date" in meals_df.columns else pd.DataFrame()
    today_cals = int(today_df["calories"].sum()) if not today_df.empty else 0

    s1, s2, s3 = st.columns(3)
    with s1:
        st.markdown(f'<div class="stat-card"><span class="stat-icon">🔥</span><div class="stat-value">{today_cals}</div><div class="stat-label">Today\'s Calories</div></div>', unsafe_allow_html=True)
    with s2:
        st.markdown(f'<div class="stat-card"><span class="stat-icon">📊</span><div class="stat-value">{int(meals_df["calories"].sum())}</div><div class="stat-label">Total Calories Logged</div></div>', unsafe_allow_html=True)
    with s3:
        avg = int(meals_df["calories"].mean()) if not meals_df.empty else 0
        st.markdown(f'<div class="stat-card"><span class="stat-icon">📈</span><div class="stat-value">{avg}</div><div class="stat-label">Avg Calories / Meal</div></div>', unsafe_allow_html=True)

    st.write("")

    # Calorie trend chart
    if "date" in meals_df.columns:
        trend = meals_df.groupby("date")["calories"].sum().reset_index()
        fig = px.bar(
            trend, x="date", y="calories",
            labels={"date": "Date", "calories": "Calories"},
            color="calories",
            color_continuous_scale=["#312e81", "#6366f1", "#a5b4fc"],
        )
        fig.update_layout(
            paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
            font=dict(color="#94a3b8", family="Plus Jakarta Sans"),
            xaxis=dict(gridcolor="rgba(255,255,255,0.05)", tickfont=dict(color="#64748b")),
            yaxis=dict(gridcolor="rgba(255,255,255,0.05)", tickfont=dict(color="#64748b")),
            coloraxis_showscale=False,
            margin=dict(l=0, r=0, t=10, b=0), height=240,
        )
        st.plotly_chart(fig, use_container_width="stretch")

    # Table
    display_df = meals_df.drop(columns=["id", "username"], errors="ignore")
    st.dataframe(display_df, use_container_width="stretch", hide_index=True)
else:
    st.markdown("""
    <div class="info-card" style="text-align:center;padding:48px;">
        <div style="font-size:3rem;">🥗</div>
        <div class="info-value" style="margin-top:12px;">No meals logged yet</div>
        <div class="info-label" style="margin-top:6px;">Use the form above to track your first meal!</div>
    </div>
    """, unsafe_allow_html=True)

conn.close()