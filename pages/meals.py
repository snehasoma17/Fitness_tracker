import sqlite3
from datetime import date

import pandas as pd
import plotly.express as px
import streamlit as st

import ai_helper
from utils.i18n import t
from utils.navigation import initialize_page

# 1. Initialize Page and Sidebar
initialize_page(t("meals"), "🍽️")

username = st.session_state.username

# 2. Database Connection
conn = sqlite3.connect("fitness.db", check_same_thread=False)
cursor = conn.cursor()

# Ensure table has username column
try:
    cursor.execute("ALTER TABLE meals ADD COLUMN username TEXT")
    conn.commit()
except Exception:
    pass

# Ensure full meals schema works
try:
    cursor.execute("ALTER TABLE meals ADD COLUMN food TEXT")
    conn.commit()
except Exception:
    pass

try:
    cursor.execute("ALTER TABLE meals ADD COLUMN protein INTEGER DEFAULT 0")
    conn.commit()
    cursor.execute("ALTER TABLE meals ADD COLUMN carbs INTEGER DEFAULT 0")
    conn.commit()
except Exception:
    pass

# ── PAGE HEADER ────────────────────────────────────────────
st.markdown(
    f"""
<div class="hero-card" style="padding:28px 36px;text-align:left;display:flex;align-items:center;gap:24px;">
    <div style="font-size:3.5rem;">🍽️</div>
    <div>
        <h1 style="margin:0;font-size:2rem !important;">{t("meals")}</h1>
        <h3 style="margin:0;font-size:1rem !important;color:#64748b !important;">
            {t("log_meal")} & {t("calories")}
        </h3>
    </div>
</div>
""",
    unsafe_allow_html=True,
)

st.write("")

# ── LOG MEAL FORM ──────────────────────────────────────────
st.markdown(
    f'<div class="section-header"><span class="icon">➕</span> {t("log_meal")}</div>',
    unsafe_allow_html=True,
)

col_form, col_tips = st.columns([3, 2])

with col_form:
    with st.form("meal_form", clear_on_submit=True):
        f1, f2 = st.columns(2)
        with f1:
            # Multi-language meal types
            breakfast_lbl = f"🌅 {t('meal_breakfast')}"
            lunch_lbl = f"☀️ {t('meal_lunch')}"
            dinner_lbl = f"🌙 {t('meal_dinner')}"
            snacks_lbl = f"🍎 {t('meal_snacks')}"

            meal_type = st.selectbox(
                t("meal_type"), [breakfast_lbl, lunch_lbl, dinner_lbl, snacks_lbl]
            )
        with f2:
            meal_date = st.date_input(t("date"), value=date.today())

        food = st.text_input(t("food_name"), placeholder="e.g. Grilled Chicken with Brown Rice")

        c1, c2, c3 = st.columns(3)
        with c1:
            calories = st.number_input(
                f"🔥 {t('calories')} (kcal)", min_value=0, max_value=5000, value=0, step=10
            )
        with c2:
            protein = st.number_input(
                f"💪 {t('protein')} (g)", min_value=0, max_value=500, value=0, step=1
            )
        with c3:
            carbs = st.number_input(
                f"🍞 {t('carbs')} (g)", min_value=0, max_value=500, value=0, step=1
            )

        submitted = st.form_submit_button(t("save_meal"), type="primary")

        if submitted:
            if not food.strip():
                st.error("Please enter the food name.")
            else:
                try:
                    # Save details
                    cursor.execute(
                        """
                        INSERT INTO meals (username, date, meal, food, calories, protein, carbs)
                        VALUES (?, ?, ?, ?, ?, ?, ?)
                    """,
                        (
                            username,
                            str(meal_date),
                            meal_type.split(" ", 1)[1],
                            food,
                            calories,
                            protein,
                            carbs,
                        ),
                    )
                    conn.commit()
                    st.success(f"✅ **{food}** {t('success')}!")
                except Exception:
                    # Fallback to base meals schema if needed
                    try:
                        cursor.execute(
                            """
                            INSERT INTO meals (username, date, meal, calories)
                            VALUES (?, ?, ?, ?)
                        """,
                            (username, str(meal_date), meal_type.split(" ", 1)[1], calories),
                        )
                        conn.commit()
                        st.success(f"✅ **{food}** {t('success')} (Basic)!")
                    except Exception as fallback_err:
                        st.error(f"Error saving: {str(fallback_err)}")

with col_tips:
    guide_lbl = t("calorie_guide")
    daily_water_lbl = t("daily_water_goal")
    oatmeal_lbl = t("oatmeal_lbl")
    chicken_lbl = t("chicken_lbl")
    egg_lbl = t("egg_lbl")
    rice_lbl = t("rice_lbl")
    avocado_lbl = t("avocado_lbl")
    salmon_lbl = t("salmon_lbl")

    st.markdown(
        f"""
    <div class="info-card" style="padding:24px;">
        <div class="info-label">💡 {guide_lbl}</div>
        <br>
        <table style="width:100%;color:#94a3b8;font-size:0.88rem;border-collapse:collapse;">
            <tr style="border-bottom:1px solid rgba(255,255,255,0.06);">
                <td style="padding:8px 4px;">🥣 {oatmeal_lbl}</td>
                <td style="padding:8px 4px;text-align:right;color:#a5b4fc;font-weight:700;">~150 kcal</td>
            </tr>
            <tr style="border-bottom:1px solid rgba(255,255,255,0.06);">
                <td style="padding:8px 4px;">🍗 {chicken_lbl}</td>
                <td style="padding:8px 4px;text-align:right;color:#a5b4fc;font-weight:700;">~165 kcal</td>
            </tr>
            <tr style="border-bottom:1px solid rgba(255,255,255,0.06);">
                <td style="padding:8px 4px;">🥚 {egg_lbl}</td>
                <td style="padding:8px 4px;text-align:right;color:#a5b4fc;font-weight:700;">~78 kcal</td>
            </tr>
            <tr style="border-bottom:1px solid rgba(255,255,255,0.06);">
                <td style="padding:8px 4px;">🍚 {rice_lbl}</td>
                <td style="padding:8px 4px;text-align:right;color:#a5b4fc;font-weight:700;">~206 kcal</td>
            </tr>
            <tr style="border-bottom:1px solid rgba(255,255,255,0.06);">
                <td style="padding:8px 4px;">🥑 {avocado_lbl}</td>
                <td style="padding:8px 4px;text-align:right;color:#a5b4fc;font-weight:700;">~120 kcal</td>
            </tr>
            <tr>
                <td style="padding:8px 4px;">🐟 {salmon_lbl}</td>
                <td style="padding:8px 4px;text-align:right;color:#a5b4fc;font-weight:700;">~208 kcal</td>
            </tr>
        </table>
        <br>
        <div class="info-label">💧 {daily_water_lbl}: <span style="color:#38bdf8;font-weight:700;">8 glasses / 2L</span></div>
    </div>
    """,
        unsafe_allow_html=True,
    )

# ── AI MEAL ADVISOR (NEW AI FEATURE) ───────────────────────
st.write("")
st.markdown(
    f'<div class="section-header"><span class="icon">🤖</span> {t("ai_meal_advisor")}</div>',
    unsafe_allow_html=True,
)

today_str = str(date.today())
# Fetch meals for advisor
cursor.execute(
    "SELECT meal, food, calories FROM meals WHERE username=? AND date=?", (username, today_str)
)
today_meals = cursor.fetchall()

adv_btn_lbl = t("ask_ai_nutritionist")

if st.button(f"🤖 {adv_btn_lbl}", type="secondary", use_container_width=True):
    if not today_meals:
        no_meals_log = t("no_meals_today")
        st.warning(no_meals_log)
    else:
        with st.spinner(t("loading")):
            meals_desc = []
            total_today_cals = 0
            for row in today_meals:
                m_type, f_name, cals = row
                # Handle old schema where food is None
                f_name = f_name if f_name else m_type
                meals_desc.append(f"- {m_type}: {f_name} ({cals} kcal)")
                total_today_cals += cals

            meals_text = "\n".join(meals_desc)
            prompt = f"""
Today is {today_str}. The user has logged the following meals:
{meals_text}

Total calories logged today: {total_today_cals} kcal.

Analyze today's meal choices.
Provide:
1. Calorie and macronutrient evaluation.
2. Positives (What's Great).
3. Areas of improvement.
4. 3 actionable tips for their next meal.
Keep it extremely concise and direct.
"""
            sys_p = "You are an expert sports nutritionist and dietitian. Answer in the requested language."
            response = ai_helper.get_ai_response(prompt, sys_p)

            st.markdown(ai_helper.provider_badge(), unsafe_allow_html=True)
            st.markdown(
                f"""
            <div class="info-card" style="padding:20px;border-left:4px solid #10b981;">
                <h4 style="margin-top:0;color:#10b981;">📋 {t("ai_meal_advisor")} Report</h4>
                <div>{response}</div>
            </div>
            """,
                unsafe_allow_html=True,
            )

# ── MEAL HISTORY ───────────────────────────────────────────
st.write("")
st.markdown(
    f'<div class="section-header"><span class="icon">📋</span> {t("meal_history")}</div>',
    unsafe_allow_html=True,
)

try:
    # Use pandas to pull
    meals_df = pd.read_sql(
        f"SELECT * FROM meals WHERE username='{username}' ORDER BY date DESC", conn
    )
except Exception:
    meals_df = pd.DataFrame()

if not meals_df.empty:
    today_df = (
        meals_df[meals_df["date"] == today_str] if "date" in meals_df.columns else pd.DataFrame()
    )
    today_cals = int(today_df["calories"].sum()) if not today_df.empty else 0

    s1, s2, s3 = st.columns(3)

    today_cals_lbl = t("today_calories_lbl")
    total_cals_lbl = t("total_calories_logged")
    avg_cals_lbl = t("avg_calories_meal")

    with s1:
        st.markdown(
            f'<div class="stat-card"><span class="stat-icon">🔥</span><div class="stat-value">{today_cals}</div><div class="stat-label">{today_cals_lbl}</div></div>',
            unsafe_allow_html=True,
        )
    with s2:
        st.markdown(
            f'<div class="stat-card"><span class="stat-icon">📊</span><div class="stat-value">{int(meals_df["calories"].sum())}</div><div class="stat-label">{total_cals_lbl}</div></div>',
            unsafe_allow_html=True,
        )
    with s3:
        avg = int(meals_df["calories"].mean()) if not meals_df.empty else 0
        st.markdown(
            f'<div class="stat-card"><span class="stat-icon">📈</span><div class="stat-value">{avg}</div><div class="stat-label">{avg_cals_lbl}</div></div>',
            unsafe_allow_html=True,
        )

    st.write("")

    # Calorie trend chart
    if "date" in meals_df.columns:
        trend = meals_df.groupby("date")["calories"].sum().reset_index()
        fig = px.bar(
            trend,
            x="date",
            y="calories",
            labels={"date": t("date"), "calories": t("calories")},
            color="calories",
            color_continuous_scale=["#312e81", "#6366f1", "#a5b4fc"],
        )
        fig.update_layout(
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            font=dict(color="#94a3b8", family="Plus Jakarta Sans"),
            xaxis=dict(gridcolor="rgba(255,255,255,0.05)", tickfont=dict(color="#64748b")),
            yaxis=dict(gridcolor="rgba(255,255,255,0.05)", tickfont=dict(color="#64748b")),
            coloraxis_showscale=False,
            margin=dict(l=0, r=0, t=10, b=0),
            height=240,
        )
        st.plotly_chart(fig, use_container_width=True)

    # Table
    cols_to_keep = ["date", "meal", "food", "calories", "protein", "carbs"]
    # Gracefully match schema
    display_cols = [c for c in cols_to_keep if c in meals_df.columns]
    display_df = meals_df[display_cols].copy()
    st.dataframe(display_df, use_container_width=True, hide_index=True)
else:
    st.markdown(
        f"""
    <div class="info-card" style="text-align:center;padding:48px;">
        <div style="font-size:3rem;">🥗</div>
        <div class="info-value" style="margin-top:12px;">{t("no_meals")}</div>
        <div class="info-label" style="margin-top:6px;">Log some meals to start!</div>
    </div>
    """,
        unsafe_allow_html=True,
    )

conn.close()
