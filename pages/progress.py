import sqlite3
from datetime import date

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

import ai_helper
from utils.i18n import t
from utils.navigation import initialize_page

# 1. Initialize Page and Sidebar
initialize_page(t("progress"), "📈")

username = st.session_state.username

# 2. Database Connection
conn = sqlite3.connect("fitness.db", check_same_thread=False)
cursor = conn.cursor()

# Ensure table has username column
try:
    cursor.execute("ALTER TABLE weight_log ADD COLUMN username TEXT")
    conn.commit()
except Exception:
    pass

# Ensure full weight_log columns exist
try:
    cursor.execute("ALTER TABLE weight_log ADD COLUMN notes TEXT")
    conn.commit()
except Exception:
    pass

# ── PAGE HEADER ─────────────────────────────────────────────
st.markdown(
    f"""
<div class="hero-card" style="padding:28px 36px;text-align:left;display:flex;align-items:center;gap:24px;">
    <div style="font-size:3.5rem;">📈</div>
    <div>
        <h1 style="margin:0;font-size:2rem !important;">{t("progress")}</h1>
        <h3 style="margin:0;font-size:1rem !important;color:#64748b !important;">
            {t("weight_progress_subtitle")}
        </h3>
    </div>
</div>
""",
    unsafe_allow_html=True,
)

st.write("")

# ── LOG WEIGHT ──────────────────────────────────────────────
st.markdown(
    f'<div class="section-header"><span class="icon">➕</span> {t("log_weight")}</div>',
    unsafe_allow_html=True,
)

log_col, info_col = st.columns([2, 1])

with log_col:
    with st.form("weight_form", clear_on_submit=True):
        wc1, wc2 = st.columns(2)
        with wc1:
            new_weight = st.number_input(
                f"⚖️ {t('weight_entry')}", min_value=20.0, max_value=300.0, value=70.0, step=0.1
            )
        with wc2:
            log_date = st.date_input(t("date"), value=date.today())
        notes_lbl = t("notes_optional")
        notes = st.text_input(notes_lbl, placeholder="e.g. Morning fasting weight, post-workout")
        save_btn = st.form_submit_button(t("save_weight"), type="primary")

        if save_btn:
            try:
                cursor.execute(
                    "INSERT INTO weight_log (date, weight, username, notes) VALUES (?, ?, ?, ?)",
                    (str(log_date), new_weight, username, notes),
                )
                conn.commit()
                st.success(f"✅ Weight **{new_weight} kg** logged for **{log_date}**!")
            except Exception:
                try:
                    cursor.execute(
                        "INSERT INTO weight_log (date, weight, username) VALUES (?, ?, ?)",
                        (str(log_date), new_weight, username),
                    )
                    conn.commit()
                    st.success(f"✅ Weight **{new_weight} kg** logged for **{log_date}**!")
                except Exception as ex_err:
                    st.error(f"Error saving entry: {str(ex_err)}")

with info_col:
    st.markdown(
        f"""
    <div class="info-card" style="padding:24px;height:100%;">
        <div class="info-label">📌 {t("tracking_tips")}</div>
        <br>
        <ul style="color:#94a3b8;font-size:0.88rem;line-height:2;padding-left:16px;margin:0;">
            <li>Weigh yourself at the same time daily</li>
            <li>Best time: morning, after waking up</li>
            <li>Avoid weighing after large meals or workouts</li>
            <li>Focus on weekly average trends</li>
        </ul>
    </div>
    """,
        unsafe_allow_html=True,
    )

# ── LOAD DATA ────────────────────────────────────────────────
try:
    df = pd.read_sql(f"SELECT * FROM weight_log WHERE username='{username}' ORDER BY date", conn)
except Exception:
    df = pd.DataFrame()

# ── AI PROGRESS ANALYST (NEW AI FEATURE) ──────────────────────
st.write("")
st.markdown(
    f'<div class="section-header"><span class="icon">🤖</span> {t("ai_progress_analyst")}</div>',
    unsafe_allow_html=True,
)

analyst_btn_lbl = t("ai_weight_analysis")

if st.button(f"📊 {analyst_btn_lbl}", type="secondary", use_container_width=True):
    if df.empty or len(df) < 2:
        warning_msg = t("min_2_entries")
        st.warning(warning_msg)
    else:
        with st.spinner(t("loading")):
            # Fetch goal
            cursor.execute("SELECT goal FROM users WHERE username=?", (username,))
            user_g_row = cursor.fetchone()
            u_goal = user_g_row[0] if user_g_row else "Weight Loss"

            # Create history string
            history_rows = []
            for _, r in df.iterrows():
                history_rows.append(f"- {r['date']}: {r['weight']} kg")
            history_text = "\n".join(history_rows)

            prompt = f"""
The user has the fitness goal: {u_goal}
Here is their logged weight history over time (chronological):
{history_text}

Analyze their weight trend.
Provide:
1. Average weight change (e.g. rate per week).
2. Trend analysis (Is it moving in the correct direction for their goal?).
3. Recommendation/Forecast (How can they optimize their diet/workout to hit their goal).
Keep it short, professional, and science-backed.
"""
            sys_p = "You are a professional fitness analyst and sports scientist. Respond in the requested language."
            analysis_res = ai_helper.get_ai_response(prompt, sys_p)

            st.markdown(ai_helper.provider_badge(), unsafe_allow_html=True)
            st.markdown(
                f"""
            <div class="info-card" style="padding:20px;border-left:4px solid #6366f1;">
                <h4 style="margin-top:0;color:#6366f1;">📋 AI Progress Report</h4>
                <div>{analysis_res}</div>
            </div>
            """,
                unsafe_allow_html=True,
            )

# ── SUMMARY STATS ──────────────────────────────────────
if not df.empty and "weight" in df.columns and "date" in df.columns:
    df["weight"] = pd.to_numeric(df["weight"], errors="coerce")
    df = df.dropna(subset=["weight"])

    first_w = df["weight"].iloc[0]
    last_w = df["weight"].iloc[-1]
    min_w = df["weight"].min()
    max_w = df["weight"].max()
    change = round(last_w - first_w, 1)
    sign = "+" if change > 0 else ""

    st.write("")
    st.markdown(
        f'<div class="section-header"><span class="icon">📊</span> {t("progress_summary")}</div>',
        unsafe_allow_html=True,
    )

    s1, s2, s3, s4 = st.columns(4)
    with s1:
        st.markdown(
            f'<div class="stat-card"><span class="stat-icon">📉</span><div class="stat-value">{last_w} kg</div><div class="stat-label">{t("current_weight")}</div></div>',
            unsafe_allow_html=True,
        )
    with s2:
        clr = "#10b981" if change <= 0 else "#f59e0b"
        st.markdown(
            f'<div class="stat-card"><span class="stat-icon">🔄</span><div class="stat-value" style="color:{clr};">{sign}{change} kg</div><div class="stat-label">{t("total_change")}</div></div>',
            unsafe_allow_html=True,
        )
    with s3:
        st.markdown(
            f'<div class="stat-card"><span class="stat-icon">🏆</span><div class="stat-value">{min_w} kg</div><div class="stat-label">{t("lowest_recorded")}</div></div>',
            unsafe_allow_html=True,
        )
    with s4:
        st.markdown(
            f'<div class="stat-card"><span class="stat-icon">📌</span><div class="stat-value">{len(df)}</div><div class="stat-label">{t("total_entries")}</div></div>',
            unsafe_allow_html=True,
        )

    st.write("")

    # ── CHARTS ─────────────────────────────────────────────
    chart_col, hist_col = st.columns([3, 2])

    with chart_col:
        st.markdown(
            f'<div class="section-header"><span class="icon">📉</span> {t("weight_journey")}</div>',
            unsafe_allow_html=True,
        )
        fig = go.Figure()
        fig.add_trace(
            go.Scatter(
                x=df["date"],
                y=df["weight"],
                mode="lines+markers",
                line=dict(color="#6366f1", width=3),
                marker=dict(size=9, color="#a5b4fc", line=dict(width=2, color="#6366f1")),
                fill="tozeroy",
                fillcolor="rgba(99,102,241,0.07)",
                name=t("weight"),
                hovertemplate="<b>%{x}</b><br>Weight: %{y} kg<extra></extra>",
            )
        )

        # Rolling avg
        if len(df) >= 3:
            df["rolling"] = df["weight"].rolling(3, min_periods=1).mean().round(1)
            fig.add_trace(
                go.Scatter(
                    x=df["date"],
                    y=df["rolling"],
                    mode="lines",
                    line=dict(color="#c084fc", width=2, dash="dot"),
                    name="3-day Avg",
                    hovertemplate="<b>%{x}</b><br>3-day Avg: %{y} kg<extra></extra>",
                )
            )

        fig.update_layout(
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            font=dict(color="#94a3b8", family="Plus Jakarta Sans"),
            xaxis=dict(gridcolor="rgba(255,255,255,0.05)", tickfont=dict(color="#64748b")),
            yaxis=dict(gridcolor="rgba(255,255,255,0.05)", tickfont=dict(color="#64748b")),
            legend=dict(bgcolor="rgba(0,0,0,0)", font=dict(color="#94a3b8")),
            margin=dict(l=0, r=0, t=10, b=0),
            height=300,
        )
        st.plotly_chart(fig, use_container_width=True)

    with hist_col:
        st.markdown(
            f'<div class="section-header"><span class="icon">📊</span> {t("weight_distribution")}</div>',
            unsafe_allow_html=True,
        )
        fig2 = px.histogram(
            df,
            x="weight",
            nbins=12,
            color_discrete_sequence=["#6366f1"],
            labels={"weight": t("weight") + " (kg)", "count": "Entries"},
        )
        fig2.update_layout(
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            font=dict(color="#94a3b8", family="Plus Jakarta Sans"),
            xaxis=dict(gridcolor="rgba(255,255,255,0.05)", tickfont=dict(color="#64748b")),
            yaxis=dict(gridcolor="rgba(255,255,255,0.05)", tickfont=dict(color="#64748b")),
            margin=dict(l=0, r=0, t=10, b=0),
            height=300,
            bargap=0.1,
        )
        st.plotly_chart(fig2, use_container_width=True)

    # ── DATA TABLE ──────────────────────────────────────────
    st.markdown(
        f'<div class="section-header"><span class="icon">📋</span> {t("weight_log_history")}</div>',
        unsafe_allow_html=True,
    )
    display_df = df.drop(columns=["id", "username"], errors="ignore").sort_values(
        "date", ascending=False
    )
    st.dataframe(display_df, use_container_width=True, hide_index=True)

else:
    st.markdown(
        f"""
    <div class="info-card" style="text-align:center;padding:56px;">
        <div style="font-size:3.5rem;">📭</div>
        <div class="info-value" style="margin-top:14px;">{t("no_weight_records")}</div>
        <div class="info-label" style="margin-top:6px;">Use the form above to log weight!</div>
    </div>
    """,
        unsafe_allow_html=True,
    )

conn.close()
