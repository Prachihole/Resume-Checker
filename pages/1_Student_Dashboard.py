import streamlit as st
import json
import os

# ===========================================
# 🔐 LOGIN CHECK
# ===========================================
if "logged_in" not in st.session_state or not st.session_state.logged_in:
    st.warning("⚠️ Please log in first.")
    st.stop()

# ===========================================
# 📦 USER DATA STORAGE (LOCAL JSON)
# ===========================================
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

user_email = st.session_state.get("user_email", "")
data = load_progress()
if user_email not in data:
    data[user_email] = {"resumes_built": 0, "ats_score_avg": 0, "grammar_fixes": 0}
    save_progress(data)

progress = data[user_email]

# ===========================================
# 🎨 PAGE CONFIG
# ===========================================
st.set_page_config(page_title="Student Dashboard", page_icon="🎓", layout="wide")

st.markdown("""
<style>
body {
  background: linear-gradient(135deg, #0a0f1e, #122635, #0a0f1e);
  color: #E8EEF5;
  font-family: "Inter", sans-serif;
}
h1 {
  text-align: center;
  background: linear-gradient(90deg, #00FFFF, #FF63E0);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  font-weight: 800;
}
.metric-box {
  text-align: center;
  background: rgba(255,255,255,0.06);
  border-radius: 16px;
  padding: 20px;
  box-shadow: 0 10px 30px rgba(0,255,255,0.08);
  backdrop-filter: blur(10px);
  transition: transform .3s ease;
}
.metric-box:hover { transform: scale(1.03); }
.metric-title { color: #9ed7f9; font-weight: 600; }
.metric-value { font-size: 2rem; font-weight: 800; color: #00FFFF; }
.progress-bar {
  height: 12px;
  border-radius: 8px;
  background: rgba(255,255,255,0.15);
  margin-top: 6px;
}
.progress-fill {
  height: 12px;
  border-radius: 8px;
  background: linear-gradient(90deg, #00FFFF, #FF63E0);
}
</style>
""", unsafe_allow_html=True)

st.markdown("<h1>🎓 Student Progress Dashboard</h1>", unsafe_allow_html=True)
st.caption("Track your resume growth, ATS performance, and grammar improvement over time 🚀")

# ===========================================
# 📊 METRICS
# ===========================================
col1, col2, col3 = st.columns(3)

col1.markdown(f"""
<div class='metric-box'>
  <div class='metric-title'>📄 Resumes Built</div>
  <div class='metric-value'>{progress["resumes_built"]}</div>
</div>
""", unsafe_allow_html=True)

col2.markdown(f"""
<div class='metric-box'>
  <div class='metric-title'>🧠 Avg ATS Score</div>
  <div class='metric-value'>{progress["ats_score_avg"]}%</div>
</div>
""", unsafe_allow_html=True)

col3.markdown(f"""
<div class='metric-box'>
  <div class='metric-title'>✍️ Grammar Fixes</div>
  <div class='metric-value'>{progress["grammar_fixes"]}</div>
</div>
""", unsafe_allow_html=True)

# ===========================================
# 📈 VISUAL PROGRESS
# ===========================================
def render_progress(label, percent):
    filled = int(percent)
    st.markdown(f"""
    <div style='margin-top:10px;'>
        <div style='font-weight:600;margin-bottom:4px;'>{label}</div>
        <div class='progress-bar'>
            <div class='progress-fill' style='width:{filled}%;'></div>
        </div>
    </div>
    """, unsafe_allow_html=True)

st.markdown("### 📈 Progress Overview")

render_progress("Resume Building", min(progress["resumes_built"] * 20, 100))
render_progress("ATS Optimization", progress["ats_score_avg"])
render_progress("Grammar Mastery", min(progress["grammar_fixes"] * 10, 100))

st.markdown("---")
st.markdown("### 🧭 Tools to Improve Your Profile")

colA, colB, colC = st.columns(3)
colA.page_link("pages/2_ATS_Score_Checker.py", label="📊 ATS Score Checker", icon="📄")
colB.page_link("pages/3_Grammar_Enhancer.py", label="✍️ Grammar Enhancer", icon="🪄")
colC.page_link("pages/4_Resume_Builder.py", label="🧠 Resume Builder", icon="📜")

# ===========================================
# ⚙️ LOGOUT
# ===========================================
st.sidebar.markdown(f"👋 Logged in as: **{st.session_state.user_name}**")
if st.sidebar.button("🚪 Logout"):
    st.session_state.logged_in = False
    st.switch_page("app.py")

