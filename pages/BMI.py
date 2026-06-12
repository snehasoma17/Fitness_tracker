import streamlit as st
import plotly.graph_objects as go

st.set_page_config(page_title="BMI Calculator", page_icon="⚖️", layout="wide")
try:
    with open("data/style.css") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
except Exception:
    pass

# ── HEADER ──────────────────────────────────────────────────
st.markdown("""
<div class="hero-card" style="padding:28px 36px;text-align:left;display:flex;align-items:center;gap:24px;">
    <div style="font-size:3.5rem;">⚖️</div>
    <div>
        <h1 style="margin:0;font-size:2rem !important;">BMI Calculator</h1>
        <h3 style="margin:0;font-size:1rem !important;color:#64748b !important;">
            Calculate your Body Mass Index and understand your health range
        </h3>
    </div>
</div>
""", unsafe_allow_html=True)

# ── FORM + GAUGE ─────────────────────────────────────────────
left, right = st.columns([1, 1])

with left:
    st.markdown('<div class="section-header"><span class="icon">📝</span> Enter Your Details</div>', unsafe_allow_html=True)
    with st.form("bmi_form"):
        weight = st.number_input("⚖️ Weight (kg)", min_value=10.0, max_value=300.0, value=70.0, step=0.5)
        height_cm = st.number_input("📏 Height (cm)", min_value=100.0, max_value=250.0, value=170.0, step=0.5)
        age = st.number_input("🎂 Age", min_value=5, max_value=100, value=25)
        gender = st.selectbox("⚧️ Gender", ["Male", "Female"])
        calc = st.form_submit_button("📊 Calculate BMI", type="primary")

with right:
    st.markdown('<div class="section-header"><span class="icon">📊</span> BMI Chart Reference</div>', unsafe_allow_html=True)
    st.markdown("""
    <div class="info-card">
        <table style="width:100%;color:#94a3b8;font-size:0.9rem;border-collapse:collapse;">
            <thead>
                <tr style="border-bottom:1px solid rgba(99,102,241,0.2);">
                    <th style="padding:10px 8px;text-align:left;color:#a5b4fc;">BMI Range</th>
                    <th style="padding:10px 8px;text-align:left;color:#a5b4fc;">Category</th>
                    <th style="padding:10px 8px;text-align:left;color:#a5b4fc;">Status</th>
                </tr>
            </thead>
            <tbody>
                <tr style="border-bottom:1px solid rgba(255,255,255,0.04);">
                    <td style="padding:10px 8px;">Below 18.5</td>
                    <td style="padding:10px 8px;">Underweight</td>
                    <td style="padding:10px 8px;color:#f59e0b;">⚠️ Low</td>
                </tr>
                <tr style="border-bottom:1px solid rgba(255,255,255,0.04);">
                    <td style="padding:10px 8px;">18.5 – 24.9</td>
                    <td style="padding:10px 8px;">Normal Weight</td>
                    <td style="padding:10px 8px;color:#10b981;">✅ Healthy</td>
                </tr>
                <tr style="border-bottom:1px solid rgba(255,255,255,0.04);">
                    <td style="padding:10px 8px;">25.0 – 29.9</td>
                    <td style="padding:10px 8px;">Overweight</td>
                    <td style="padding:10px 8px;color:#f59e0b;">⚠️ Caution</td>
                </tr>
                <tr>
                    <td style="padding:10px 8px;">30.0 and above</td>
                    <td style="padding:10px 8px;">Obese</td>
                    <td style="padding:10px 8px;color:#ef4444;">🔴 High Risk</td>
                </tr>
            </tbody>
        </table>
    </div>
    """, unsafe_allow_html=True)

if calc:
    height_m = height_cm / 100
    bmi = round(weight / (height_m ** 2), 1)

    if bmi < 18.5:   cat, color, tip = "Underweight",  "#f59e0b", "Consider increasing caloric intake with nutrient-dense foods and consult a dietitian."
    elif bmi < 25:   cat, color, tip = "Healthy Weight","#10b981", "Great job! Maintain your current lifestyle with balanced diet and regular exercise."
    elif bmi < 30:   cat, color, tip = "Overweight",    "#f59e0b", "Focus on gradual weight loss through caloric deficit and increased physical activity."
    else:            cat, color, tip = "Obese",          "#ef4444", "Consult a healthcare professional for a structured weight management program."

    # Result cards
    r1, r2, r3 = st.columns(3)
    with r1:
        st.markdown(f'<div class="stat-card"><span class="stat-icon">📊</span><div class="stat-value" style="color:{color};">{bmi}</div><div class="stat-label">Your BMI</div></div>', unsafe_allow_html=True)
    with r2:
        ideal_low  = round(18.5 * height_m ** 2, 1)
        ideal_high = round(24.9 * height_m ** 2, 1)
        st.markdown(f'<div class="stat-card"><span class="stat-icon">🎯</span><div class="stat-value" style="font-size:1.3rem;">{ideal_low}–{ideal_high} kg</div><div class="stat-label">Ideal Weight Range</div></div>', unsafe_allow_html=True)
    with r3:
        diff = round(weight - (ideal_low + ideal_high) / 2, 1)
        sign = "+" if diff > 0 else ""
        st.markdown(f'<div class="stat-card"><span class="stat-icon">{"📉" if diff > 0 else "📈"}</span><div class="stat-value" style="font-size:1.5rem;">{sign}{diff} kg</div><div class="stat-label">From Ideal Midpoint</div></div>', unsafe_allow_html=True)

    st.write("")

    # Gauge chart
    gauge_col, tip_col = st.columns([3, 2])
    with gauge_col:
        fig = go.Figure(go.Indicator(
            mode="gauge+number",
            value=bmi,
            number={"font": {"color": color, "size": 52, "family": "Plus Jakarta Sans"}, "suffix": " BMI"},
            gauge={
                "axis": {"range": [10, 45], "tickwidth": 1, "tickcolor": "#475569", "tickfont": {"color": "#64748b"}},
                "bar": {"color": color, "thickness": 0.3},
                "bgcolor": "rgba(0,0,0,0)",
                "borderwidth": 0,
                "steps": [
                    {"range": [10, 18.5], "color": "rgba(245,158,11,0.12)"},
                    {"range": [18.5, 25],  "color": "rgba(16,185,129,0.14)"},
                    {"range": [25, 30],    "color": "rgba(245,158,11,0.12)"},
                    {"range": [30, 45],    "color": "rgba(239,68,68,0.12)"},
                ],
                "threshold": {"line": {"color": color, "width": 4}, "thickness": 0.8, "value": bmi},
            },
            title={"text": f"<b>{cat}</b>", "font": {"color": color, "size": 20, "family": "Plus Jakarta Sans"}},
        ))
        fig.update_layout(
            paper_bgcolor="rgba(0,0,0,0)",
            font=dict(family="Plus Jakarta Sans"),
            height=320, margin=dict(l=20, r=20, t=20, b=10)
        )
        st.plotly_chart(fig, use_container_width=True)

    with tip_col:
        st.markdown(f"""
        <div class="info-card" style="margin-top:24px;padding:28px;">
            <div class="info-label">💡 Personalized Tip</div>
            <div style="font-size:1.5rem;margin:14px 0 10px;">{"⚠️" if bmi < 18.5 or bmi >= 25 else "✅"}</div>
            <div style="color:#e2e8f0;font-size:0.97rem;line-height:1.7;">{tip}</div>
            <br>
            <div class="info-label">📌 BMR Estimate (Mifflin–St Jeor)</div>
            <div class="info-value" style="margin-top:6px;">
                { round(10*weight + 6.25*height_cm - 5*age + (5 if gender=="Male" else -161)) } kcal/day
            </div>
        </div>
        """, unsafe_allow_html=True)