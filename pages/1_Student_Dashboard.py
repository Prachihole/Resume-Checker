import streamlit as st
import json
import os
from firebase_config import db

# ======================================================

# PAGE CONFIG

# ======================================================

st.set_page_config(layout="wide")

# ======================================================

# LOGIN PROTECTION

# ======================================================

if "logged_in" not in st.session_state or not st.session_state.logged_in:
 st.switch_page("app.py")

user_email = st.session_state.user_email
user_name = st.session_state.user_name

# ======================================================

# USER PROGRESS FILE

# ======================================================

USER_PROGRESS_FILE = "user_progress.json"

def load_progress():
 if not os.path.exists(USER_PROGRESS_FILE):
  with open(USER_PROGRESS_FILE, "w") as f:
   json.dump({}, f)
 with open(USER_PROGRESS_FILE, "r") as f:
   return json.load(f)

def save_progress(data):
 with open(USER_PROGRESS_FILE, "w") as f:
  json.dump(data, f, indent=2)

data = load_progress()

# ======================================================

# DEFAULT USER PROFILE

# ======================================================

if user_email not in data:
 data[user_email] = {
"resumes_analyzed": 0,
"avg_ats_score": 0,
"grammar_fixes": 0,
"ats_history": []
}
save_progress(data)

profile = data[user_email]

# ======================================================

# GET GRAMMAR IMPROVEMENTS FROM FIREBASE

# ======================================================

docs = db.collection("grammar_checks").where(
"email", "==", user_email
).stream()

total_fixes = 0
for d in docs:
 doc_data = d.to_dict()
total_fixes += doc_data.get("grammar_errors", 0)

profile["grammar_fixes"] = total_fixes
data[user_email] = profile
save_progress(data)

# ======================================================

# STYLES

# ======================================================

st.markdown("""
<style>

.main-title{
font-size:42px;
font-weight:800;
background: linear-gradient(90deg,#38bdf8,#6366f1);
-webkit-background-clip:text;
-webkit-text-fill-color:transparent;
}

.subtitle{
color:#94a3b8;
font-size:16px;
}

.metric-card{
background:#0f172a;
padding:25px;
border-radius:14px;
border:1px solid #1e293b;
text-align:center;
}

.metric-value{
font-size:36px;
font-weight:800;
color:#38bdf8;
}

.metric-label{
color:#94a3b8;
}

</style>
""", unsafe_allow_html=True)

st.markdown('<div class="main-title">📊 Resume Analytics Dashboard</div>', unsafe_allow_html=True)
st.markdown('<div class="subtitle">Track ATS performance, grammar improvements and resume insights</div>', unsafe_allow_html=True)

# ======================================================

# SIDEBAR

# ======================================================

with st.sidebar:
 st.markdown(f"👋 **{user_name}**")
 st.caption("Resume workspace")

if st.button("🚪 Logout", key="logout_btn"):
    st.session_state.logged_in = False
    st.switch_page("app.py")
# ======================================================

# HEADER

# ======================================================

st.markdown("## 📊 Dashboard")
st.caption("Your resume performance at a glance")

st.info(
"👋 New here? Start by building your resume or upload an existing one "
"to see ATS and recruiter insights."
)

# ======================================================

# CORE METRICS

# ======================================================
col1, col2, col3 = st.columns(3)

with col1:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-value">{profile["resumes_analyzed"]}</div>
        <div class="metric-label">Resumes Analyzed</div>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-value">{profile["avg_ats_score"]}%</div>
        <div class="metric-label">Average ATS Score</div>
    </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-value">{profile["grammar_fixes"]}</div>
        <div class="metric-label">Grammar Improvements</div>
    </div>
    """, unsafe_allow_html=True)

# ======================================================
import plotly.express as px
import pandas as pd

docs = db.collection("ats_results").where(
    "email","==",user_email
).stream()

history = []

for doc in docs:
    d = doc.to_dict()

    history.append({
        "score": d.get("ats_score",0),
        "time": str(d.get("timestamp"))
    })

if history:

    df = pd.DataFrame(history)

    fig = px.line(
        df,
        x="time",
        y="score",
        markers=True,
        title="📈 ATS Score Progress"
    )

    st.plotly_chart(fig, use_container_width=True)


import plotly.graph_objects as go

fig = go.Figure(go.Indicator(
    mode = "gauge+number",
    value = profile["avg_ats_score"],
    title = {'text': "Resume Strength"},
    gauge = {
        'axis': {'range': [0,100]},
        'bar': {'color': "#38bdf8"}
    }
))

st.plotly_chart(fig,use_container_width=True)

# RECRUITER IMPRESSION

# ======================================================

st.markdown("### 🧑‍💼 Recruiter Impression")

if profile["avg_ats_score"] >= 80:
 st.success("Your resume is recruiter-ready. Strong technical signals detected.")
elif profile["avg_ats_score"] >= 65:
 st.info("Your resume is competitive. Minor refinements can improve outcomes.")
else:
 st.warning("Your experience is valuable, but impact clarity can be improved.")

# ======================================================

# NEXT BEST ACTION

# ======================================================

st.markdown("### 🚀 Recommended Next Step")

if profile["resumes_analyzed"] == 0:
 st.markdown("➡ Start with an ATS analysis to understand how your resume performs.")
elif profile["avg_ats_score"] < 70:
 st.markdown("➡ Improve one experience bullet by adding a measurable outcome.")
else:
 st.markdown("➡ Tailor your resume for a specific job description.")

# ======================================================

# QUICK ACTIONS

# ======================================================

st.markdown("### 🧭 Tools")

st.markdown("""
<style>
.tool-card {
    background: #0f172a;
    padding: 28px;
    border-radius: 14px;
    border: 1px solid #1e293b;
    text-align: center;
    transition: 0.25s;
}

.tool-card:hover {
    transform: translateY(-6px);
    border: 1px solid #38bdf8;
    box-shadow: 0 6px 20px rgba(56,189,248,0.15);
}

.tool-title {
    font-size: 22px;
    font-weight: 700;
    margin-bottom: 10px;
}

.tool-desc {
    color: #94a3b8;
    font-size: 14px;
    margin-bottom: 20px;
}
</style>
""", unsafe_allow_html=True)

col1, col2, col3 = st.columns(3)

# ATS TOOL
with col1:
    st.markdown("""
    <div class="tool-card">
        <div class="tool-title">📊 ATS Score Checker</div>
        <div class="tool-desc">
        Analyze how ATS systems evaluate your resume
        </div>
    """, unsafe_allow_html=True)

    if st.button("Launch Tool", key="ats_tool"):
        st.switch_page("pages/2_ATS_Score_Checker.py")

    st.markdown("</div>", unsafe_allow_html=True)


# GRAMMAR TOOL
with col2:
    st.markdown("""
    <div class="tool-card">
        <div class="tool-title">✍️ Grammar Enhancer</div>
        <div class="tool-desc">
        Improve clarity, grammar, and professionalism
        </div>
    """, unsafe_allow_html=True)

    if st.button("Launch Tool", key="grammar_tool"):
        st.switch_page("pages/3_Grammar_Enhancer.py")

    st.markdown("</div>", unsafe_allow_html=True)


# RESUME BUILDER
with col3:
    st.markdown("""
    <div class="tool-card">
        <div class="tool-title">🧠 Resume Builder</div>
        <div class="tool-desc">
        Generate recruiter-ready experience bullets
        </div>
    """, unsafe_allow_html=True)

    if st.button("Launch Tool", key="resume_tool"):
        st.switch_page("pages/4_Resume_Builder.py")

    st.markdown("</div>", unsafe_allow_html=True)