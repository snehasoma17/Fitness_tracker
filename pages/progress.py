import streamlit as st
import sqlite3
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import date, timedelta
import ai_helper
from utils.i18n import t
import utils.theme
from utils.theme import load_css
load_css()

st.set_page_config(page_title="Progress Tracker", page_icon="📈", layout="wide")
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

# Ensure username column exists in weight_log
try:
    cursor.execute("ALTER TABLE weight_log ADD COLUMN username TEXT")
    conn.commit()
except Exception:
    pass

# ── PAGE HEADER ─────────────────────────────────────────────
st.markdown("""
<div class="hero-card" style="padding:28px 36px;text-align:left;display:flex;align-items:center;gap:24px;">
    <div style="font-size:3.5rem;">📈</div>
    <div>
        <h1 style="margin:0;font-size:2rem !important;">Progress Tracker</h1>
        <h3 style="margin:0;font-size:1rem !important;color:#64748b !important;">
            Log your weight and visualize your transformation journey
        </h3>
    </div>
</div>
""", unsafe_allow_html=True)

# ── LOG WEIGHT ──────────────────────────────────────────────
st.markdown('<div class="section-header"><span class="icon">➕</span> Log Today\'s Weight</div>', unsafe_allow_html=True)

log_col, info_col = st.columns([2, 1])

with log_col:
    with st.form("weight_form", clear_on_submit=True):
        wc1, wc2 = st.columns(2)
        with wc1:
            new_weight = st.number_input("⚖️ Weight (kg)", min_value=20.0, max_value=300.0, value=70.0, step=0.1)
        with wc2:
            log_date = st.date_input("📅 Date", value=date.today())
        photo_progress = st.file_uploader("📸 Progress Photo (optional)", type=["png", "jpg", "jpeg"])
        notes = st.text_input("📝 Notes (optional)", placeholder="e.g. After morning fast, post-workout")
        save_btn = st.form_submit_button("💾 Save Weight Entry", type="primary")

        if save_btn:
            try:
                cursor.execute(
                    "INSERT INTO weight_log (date, weight, username) VALUES (?, ?, ?)",
                    (str(log_date), new_weight, username)
                )
                conn.commit()
                st.success(f"✅ Weight **{new_weight} kg** logged for **{log_date}**!")
                if photo_progress:
                    st.image(photo_progress, caption=f"📸 Progress Photo — {log_date}", width=280)
                    st.info(f"📝 Note: {notes}" if notes else "")
            except Exception as e:
                st.error(f"Error: {str(e)}")

with info_col:
    st.markdown("""
    <div class="info-card" style="padding:24px;height:100%;">
        <div class="info-label">📌 Tracking Tips</div>
        <br>
        <ul style="color:#94a3b8;font-size:0.88rem;line-height:2;padding-left:16px;">
            <li>Weigh yourself at the same time daily</li>
            <li>Best time: morning, after bathroom</li>
            <li>Avoid weighing after large meals</li>
            <li>Weekly average is more reliable</li>
            <li>Track progress photos monthly</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)

# ── LOAD DATA ────────────────────────────────────────────────
try:
    df = pd.read_sql(f"SELECT * FROM weight_log WHERE username='{username}' ORDER BY date", conn)
except Exception:
    df = pd.DataFrame()

if not df.empty and "weight" in df.columns and "date" in df.columns:
    df["weight"] = pd.to_numeric(df["weight"], errors="coerce")
    df = df.dropna(subset=["weight"])

    first_w = df["weight"].iloc[0]
    last_w  = df["weight"].iloc[-1]
    min_w   = df["weight"].min()
    max_w   = df["weight"].max()
    change  = round(last_w - first_w, 1)
    sign    = "+" if change > 0 else ""

    # ── SUMMARY STATS ──────────────────────────────────────
    st.markdown('<div class="section-header"><span class="icon">📊</span> Progress Summary</div>', unsafe_allow_html=True)
    s1, s2, s3, s4 = st.columns(4)
    with s1:
        st.markdown(f'<div class="stat-card"><span class="stat-icon">📉</span><div class="stat-value">{last_w} kg</div><div class="stat-label">Current Weight</div></div>', unsafe_allow_html=True)
    with s2:
        clr = "#10b981" if change <= 0 else "#f59e0b"
        st.markdown(f'<div class="stat-card"><span class="stat-icon">🔄</span><div class="stat-value" style="color:{clr};">{sign}{change} kg</div><div class="stat-label">Total Change</div></div>', unsafe_allow_html=True)
    with s3:
        st.markdown(f'<div class="stat-card"><span class="stat-icon">🏆</span><div class="stat-value">{min_w} kg</div><div class="stat-label">Lowest Recorded</div></div>', unsafe_allow_html=True)
    with s4:
        st.markdown(f'<div class="stat-card"><span class="stat-icon">📌</span><div class="stat-value">{len(df)}</div><div class="stat-label">Total Entries</div></div>', unsafe_allow_html=True)

    st.write("")

    # ── CHARTS ─────────────────────────────────────────────
    chart_col, hist_col = st.columns([3, 2])

    with chart_col:
        st.markdown('<div class="section-header"><span class="icon">📉</span> Weight Journey</div>', unsafe_allow_html=True)
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=df["date"], y=df["weight"],
            mode="lines+markers",
            line=dict(color="#6366f1", width=3),
            marker=dict(size=9, color="#a5b4fc", line=dict(width=2, color="#6366f1")),
            fill="tozeroy", fillcolor="rgba(99,102,241,0.07)",
            name="Weight",
            hovertemplate="<b>%{x}</b><br>Weight: %{y} kg<extra></extra>"
        ))
        # Rolling avg
        if len(df) >= 3:
            df["rolling"] = df["weight"].rolling(3, min_periods=1).mean().round(1)
            fig.add_trace(go.Scatter(
                x=df["date"], y=df["rolling"],
                mode="lines", line=dict(color="#c084fc", width=2, dash="dot"),
                name="3-day Avg",
                hovertemplate="<b>%{x}</b><br>3-day Avg: %{y} kg<extra></extra>"
            ))
        fig.update_layout(
            paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
            font=dict(color="#94a3b8", family="Plus Jakarta Sans"),
            xaxis=dict(gridcolor="rgba(255,255,255,0.05)", tickfont=dict(color="#64748b")),
            yaxis=dict(gridcolor="rgba(255,255,255,0.05)", tickfont=dict(color="#64748b")),
            legend=dict(bgcolor="rgba(0,0,0,0)", font=dict(color="#94a3b8")),
            margin=dict(l=0, r=0, t=10, b=0), height=300,
        )
        st.plotly_chart(fig, use_container_width="stretch")

    with hist_col:
        st.markdown('<div class="section-header"><span class="icon">📊</span> Weight Distribution</div>', unsafe_allow_html=True)
        fig2 = px.histogram(
            df, x="weight", nbins=12,
            color_discrete_sequence=["#6366f1"],
            labels={"weight": "Weight (kg)", "count": "Entries"},
        )
        fig2.update_layout(
            paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
            font=dict(color="#94a3b8", family="Plus Jakarta Sans"),
            xaxis=dict(gridcolor="rgba(255,255,255,0.05)", tickfont=dict(color="#64748b")),
            yaxis=dict(gridcolor="rgba(255,255,255,0.05)", tickfont=dict(color="#64748b")),
            margin=dict(l=0, r=0, t=10, b=0), height=300,
            bargap=0.1,
        )
        st.plotly_chart(fig2, use_container_width="stretch")

    # ── DATA TABLE ──────────────────────────────────────────
    st.markdown('<div class="section-header"><span class="icon">📋</span> Weight Log History</div>', unsafe_allow_html=True)
    display_df = df.drop(columns=["id", "username"], errors="ignore").sort_values("date", ascending=False)
    st.dataframe(display_df, use_container_width="stretch", hide_index=True)

else:
    st.markdown("""
    <div class="info-card" style="text-align:center;padding:56px;">
        <div style="font-size:3.5rem;">📭</div>
        <div class="info-value" style="margin-top:14px;">No weight records yet</div>
        <div class="info-label" style="margin-top:6px;">Use the form above to log your first weight entry and start tracking your progress!</div>
    </div>
    """, unsafe_allow_html=True)

conn.close()