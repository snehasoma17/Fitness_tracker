import streamlit as st
import sqlite3
import pandas as pd
import plotly.express as px
from datetime import date

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
        st.plotly_chart(fig, use_container_width=True)

    # Table
    display_df = meals_df.drop(columns=["id", "username"], errors="ignore")
    st.dataframe(display_df, use_container_width=True, hide_index=True)
else:
    st.markdown("""
    <div class="info-card" style="text-align:center;padding:48px;">
        <div style="font-size:3rem;">🥗</div>
        <div class="info-value" style="margin-top:12px;">No meals logged yet</div>
        <div class="info-label" style="margin-top:6px;">Use the form above to track your first meal!</div>
    </div>
    """, unsafe_allow_html=True)

conn.close()