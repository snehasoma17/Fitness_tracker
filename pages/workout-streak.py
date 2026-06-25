import sqlite3
from datetime import date, datetime, timedelta

import plotly.graph_objects as go
import streamlit as st

import ai_helper
from utils.i18n import t
from utils.navigation import initialize_page

# 1. Initialize Page and Sidebar
initialize_page(t("workout_streak"), "🔥")

username = st.session_state.username

# 2. Database Connection
conn = sqlite3.connect("fitness.db", check_same_thread=False)
cursor = conn.cursor()

# Ensure table has username column
try:
    cursor.execute("ALTER TABLE workouts ADD COLUMN username TEXT")
    conn.commit()
except Exception:
    pass

# ── HEADER ──────────────────────────────────────────────────
st.markdown(
    f"""
<div class="hero-card" style="padding:28px 36px;text-align:left;display:flex;align-items:center;gap:24px;">
    <div style="font-size:3.5rem;">🔥</div>
    <div>
        <h1 style="margin:0;font-size:2rem !important;">{t("workout_streak")}</h1>
        <h3 style="margin:0;font-size:1rem !important;color:#64748b !important;">
            {t("streak_track_subtitle")}
        </h3>
    </div>
</div>
""",
    unsafe_allow_html=True,
)

st.write("")

# ── LOG A WORKOUT (ADD TO PREVENT EMPTY DATA) ───────────────
log_wk_lbl = t("log_workout")
ex_type_lbl = t("exercise_type")
duration_lbl = t("duration")
cals_burned_lbl = t("calories_burned")
save_wk_lbl = t("save_workout")

st.markdown(
    f'<div class="section-header"><span class="icon">➕</span> {log_wk_lbl}</div>',
    unsafe_allow_html=True,
)
with st.form("workout_form", clear_on_submit=True):
    col_w1, col_w2 = st.columns(2)
    with col_w1:
        exercise_name = st.text_input(
            ex_type_lbl, placeholder="e.g. Running, Strength Training, Yoga"
        )
        duration = st.number_input(duration_lbl, min_value=1, max_value=300, value=30)
    with col_w2:
        workout_date = st.date_input(t("date"), value=date.today())
        cals_burned = st.number_input(cals_burned_lbl, min_value=1, max_value=2000, value=150)

    submit_wk = st.form_submit_button(save_wk_lbl, type="primary")
    if submit_wk:
        if not exercise_name.strip():
            st.error("Please enter the exercise type.")
        else:
            try:
                cursor.execute(
                    """
                    INSERT INTO workouts (username, date, exercise, duration, calories)
                    VALUES (?, ?, ?, ?, ?)
                """,
                    (username, str(workout_date), exercise_name.strip(), duration, cals_burned),
                )
                conn.commit()
                st.success(f"✅ **{exercise_name}** logged successfully!")
            except Exception as e:
                st.error(f"Error saving workout: {e}")

st.write("")

# ── LOAD STREAK DATA ────────────────────────────────────────
cursor.execute(
    """
    SELECT DISTINCT date FROM workouts WHERE username=? ORDER BY date DESC
""",
    (username,),
)
date_rows = [row[0] for row in cursor.fetchall()]

# ── STREAK CALCULATION ────────────────────────────────────────
streak = 0
longest_streak = 0
temp_streak = 0

if date_rows:
    streak = 1
    # Check if the most recent workout is today or yesterday to keep streak active
    try:
        latest_d = datetime.strptime(date_rows[0], "%Y-%m-%d").date()
        today_d = date.today()
        if (today_d - latest_d).days > 1:
            # Streak broken
            streak = 0
        else:
            # Count continuous days
            for i in range(len(date_rows) - 1):
                d1 = datetime.strptime(date_rows[i], "%Y-%m-%d")
                d2 = datetime.strptime(date_rows[i + 1], "%Y-%m-%d")
                if (d1 - d2).days == 1:
                    streak += 1
                elif (d1 - d2).days == 0:
                    continue
                else:
                    break
    except Exception:
        pass

    # Compute longest streak
    temp_streak = 1
    for i in range(len(date_rows) - 1):
        try:
            d1 = datetime.strptime(date_rows[i], "%Y-%m-%d")
            d2 = datetime.strptime(date_rows[i + 1], "%Y-%m-%d")
            if (d1 - d2).days == 1:
                temp_streak += 1
                longest_streak = max(longest_streak, temp_streak)
            elif (d1 - d2).days == 0:
                continue
            else:
                temp_streak = 1
        except Exception:
            temp_streak = 1
    longest_streak = max(longest_streak, temp_streak, streak)
else:
    longest_streak = 0

total_days = len(date_rows)
worked_this_week = 0
if date_rows:
    today_d = date.today()
    worked_this_week = sum(
        1 for d in set(date_rows) if (today_d - datetime.strptime(d, "%Y-%m-%d").date()).days < 7
    )

# ── STATS OVERVIEW ──────────────────────────────────────────
st.markdown(
    f'<div class="section-header"><span class="icon">📊</span> {t("today_overview")}</div>',
    unsafe_allow_html=True,
)

s1, s2, s3, s4 = st.columns(4)
streak_emoji = "🔥" if streak >= 7 else ("⚡" if streak >= 3 else "💪")
with s1:
    st.markdown(
        f'<div class="stat-card" style="border-color:rgba(251,146,60,0.3);"><span class="stat-icon">{streak_emoji}</span><div class="stat-value" style="color:#fb923c;">{streak}</div><div class="stat-label">{t("current_streak")}</div></div>',
        unsafe_allow_html=True,
    )
with s2:
    st.markdown(
        f'<div class="stat-card"><span class="stat-icon">🏆</span><div class="stat-value" style="color:#fbbf24;">{longest_streak}</div><div class="stat-label">{t("longest_streak")}</div></div>',
        unsafe_allow_html=True,
    )
with s3:
    st.markdown(
        f'<div class="stat-card"><span class="stat-icon">📅</span><div class="stat-value">{total_days}</div><div class="stat-label">{t("total_active_days")}</div></div>',
        unsafe_allow_html=True,
    )
with s4:
    st.markdown(
        f'<div class="stat-card"><span class="stat-icon">🗓️</span><div class="stat-value">{worked_this_week}/7</div><div class="stat-label">{t("days_active_this_week")}</div></div>',
        unsafe_allow_html=True,
    )

st.write("")

# ── STREAK GAUGE & CALENDAR ──────────────────────────────────
left_col, right_col = st.columns([2, 3])

with left_col:
    st.markdown(
        f'<div class="section-header"><span class="icon">🎯</span> {t("streak_goal")}</div>',
        unsafe_allow_html=True,
    )
    goal = 30
    pct = min(streak / goal * 100, 100)
    fig = go.Figure(
        go.Indicator(
            mode="gauge+number",
            value=streak,
            number={
                "suffix": " days",
                "font": {"color": "#fb923c", "size": 44, "family": "Plus Jakarta Sans"},
            },
            gauge={
                "axis": {
                    "range": [0, goal],
                    "tickcolor": "#475569",
                    "tickfont": {"color": "#64748b"},
                },
                "bar": {"color": "#f97316", "thickness": 0.3},
                "bgcolor": "rgba(0,0,0,0)",
                "borderwidth": 0,
                "steps": [
                    {"range": [0, 7], "color": "rgba(99,102,241,0.08)"},
                    {"range": [7, 14], "color": "rgba(245,158,11,0.08)"},
                    {"range": [14, 30], "color": "rgba(249,115,22,0.1)"},
                ],
            },
            title={
                "text": f"<b>{t('streak_goal')}: {goal}-Day Streak</b>",
                "font": {"color": "#94a3b8", "size": 14, "family": "Plus Jakarta Sans"},
            },
        )
    )
    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        font=dict(family="Plus Jakarta Sans"),
        height=280,
        margin=dict(l=20, r=20, t=10, b=10),
    )
    st.plotly_chart(fig, use_container_width=True)

    # Progress bar
    st.markdown(
        f"""
    <div class="info-card" style="text-align:center;">
        <div class="info-label">{t("progress_to_goal")}</div>
        <div class="progress-bar-wrap" style="margin:12px 0 6px;">
            <div class="progress-bar-fill" style="width:{pct:.0f}%;background:linear-gradient(90deg,#f97316,#fb923c,#fbbf24);"></div>
        </div>
        <div class="stat-value" style="font-size:1.2rem;color:#fb923c;">{pct:.0f}%</div>
    </div>
    """,
        unsafe_allow_html=True,
    )

with right_col:
    st.markdown(
        f'<div class="section-header"><span class="icon">📅</span> {t("recent_activity")}</div>',
        unsafe_allow_html=True,
    )

    active_dates = set(date_rows)
    today = date.today()
    cal_data = []
    for i in range(13, -1, -1):
        d = today - timedelta(days=i)
        ds = d.strftime("%Y-%m-%d")
        cal_data.append(
            {
                "date": ds,
                "day": d.strftime("%a"),
                "active": 1 if ds in active_dates else 0,
                "label": d.strftime("%b %d"),
            }
        )

    row1 = cal_data[:7]
    row2 = cal_data[7:]

    def day_cell(d):
        color = "rgba(249,115,22,0.7)" if d["active"] else "rgba(30,41,59,0.5)"
        icon = "🔥" if d["active"] else "○"
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
    st.markdown(
        f"""
    <div style="display:flex;gap:6px;margin-bottom:8px;">{row1_html}</div>
    <div style="display:flex;gap:6px;">{row2_html}</div>
    """,
        unsafe_allow_html=True,
    )

    # Motivational banner
    st.write("")
    if streak >= 14:
        msg = t("streak_msg_outstanding")
        icon_color = "#fbbf24"
    elif streak >= 7:
        msg = t("streak_msg_week")
        icon_color = "#fb923c"
    elif streak >= 3:
        msg = t("streak_msg_momentum")
        icon_color = "#6366f1"
    elif streak >= 1:
        msg = t("streak_msg_day1")
        icon_color = "#10b981"
    else:
        msg = t("streak_msg_none")
        icon_color = "#64748b"

    st.markdown(
        f"""
    <div class="animated-banner" style="margin-top:16px;color:{icon_color} !important;font-size:1rem;">
        {msg}
    </div>
    """,
        unsafe_allow_html=True,
    )

# ── AI STREAK MOTIVATOR (NEW AI FEATURE) ────────────────────
st.write("")
st.markdown(
    f'<div class="section-header"><span class="icon">🤖</span> {t("ai_streak_motivator")}</div>',
    unsafe_allow_html=True,
)

motivate_btn_lbl = t("keep_streak_alive")

if st.button(f"⚡ {motivate_btn_lbl}", type="secondary", use_container_width=True):
    with st.spinner(t("loading")):
        # Fetch profile for context
        cursor.execute("SELECT goal, gender, age FROM users WHERE username=?", (username,))
        prof_row = cursor.fetchone()
        u_goal = prof_row[0] if prof_row else "General Fitness"

        prompt = f"""
The user has a current workout streak of {streak} days.
Goal: {u_goal}

They want a quick 10-minute home workout (bodyweight only) to do today to keep their streak alive.
Provide:
1. A 3-step quick home routine (e.g. Jumping jacks, Squats, Planks) with durations or reps.
2. A short motivational sentence.
Keep the entire output extremely short, well-structured, and formatted with bullet points and emojis.
"""
        sys_p = "You are a highly motivating personal trainer. Keep it short."
        motivation_res = ai_helper.get_ai_response(prompt, sys_p)

        st.markdown(ai_helper.provider_badge(), unsafe_allow_html=True)
        st.markdown(
            f"""
        <div class="info-card" style="padding:20px;border-left:4px solid #fb923c;">
            <h4 style="margin-top:0;color:#fb923c;">🔥 Quick Streak Workout</h4>
            <div>{motivation_res}</div>
        </div>
        """,
            unsafe_allow_html=True,
        )

conn.close()
