import streamlit as st
import json
import os
from firebase_config import db
# ======================================================
# 🔐 LOGIN PROTECTION (MANDATORY)
# ======================================================
if "logged_in" not in st.session_state or not st.session_state.logged_in:
    st.switch_page("app.py")

# ======================================================
# 📦 USER PROGRESS STORAGE (DB READY)
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

user_email = st.session_state.user_email
user_name = st.session_state.user_name

data = load_progress()
st.info(
    "👋 New here? Start by building your resume or upload an existing one "
    "to see ATS and recruiter insights."
)

# Default profile
if user_email not in data:
    data[user_email] = {
        "resumes_analyzed": 0,
        "avg_ats_score": 0,
        "grammar_fixes": 0,
        "ats_history": []
    }
    save_progress(data)


docs = db.collection("grammar_checks").where(
    "email", "==", st.session_state.get("user_email", "unknown")
).stream()

total_fixes = 0

for d in docs:
    doc_data = d.to_dict()
    total_fixes += doc_data.get("grammar_errors", 0)

profile = data.get(user_email, {})

profile.setdefault("resumes_analyzed", 0)
profile.setdefault("avg_ats_score", 0)

profile["grammar_fixes"] = total_fixes

data[user_email] = profile
save_progress(data)

# ======================================================
# 🔐 LOGIN PROTECTION (MANDATORY)
# ======================================================
if "logged_in" not in st.session_state or not st.session_state.logged_in:
    st.switch_page("app.py")

# ======================================================
# 📦 USER PROGRESS STORAGE (DB READY)
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

user_email = st.session_state.user_email
user_name = st.session_state.user_name

data = load_progress()
st.info(
    "👋 New here? Start by building your resume or upload an existing one "
    "to see ATS and recruiter insights."
)

# Default profile
if user_email not in data:
    data[user_email] = {
        "resumes_analyzed": 0,
        "avg_ats_score": 0,
        "grammar_fixes": 0,
        "ats_history": []
    }
    save_progress(data)

docs = db.collection("grammar_checks").where(
    "email", "==", st.session_state.get("user_email", "unknown")
).stream()

total_fixes = 0

for d in docs:
    import streamlit as st
import json
import os
from firebase_config import db
# ======================================================
# 🔐 LOGIN PROTECTION (MANDATORY)
# ======================================================
if "logged_in" not in st.session_state or not st.session_state.logged_in:
    st.switch_page("app.py")

# ======================================================
# 📦 USER PROGRESS STORAGE (DB READY)
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

user_email = st.session_state.user_email
user_name = st.session_state.user_name

data = load_progress()
st.info(
    "👋 New here? Start by building your resume or upload an existing one "
    "to see ATS and recruiter insights."
)

# Default profile
if user_email not in data:
    data[user_email] = {
        "resumes_analyzed": 0,
        "avg_ats_score": 0,
        "grammar_fixes": 0,
        "ats_history": []
    }
    save_progress(data)

docs = db.collection("grammar_checks").where(
    "email", "==", st.session_state.get("user_email", "unknown")
).stream()

total_fixes = 0

for d in docs:
    doc_data = d.to_dict()
    total_fixes += doc_data.get("grammar_errors", 0)
    
# -------------------------------
# Normalize user profile (schema-safe)
# -------------------------------
profile = data.get(user_email, {})
profile["grammar_fixes"] = total_fixes

profile.setdefault("resumes_analyzed", 0)
profile.setdefault("avg_ats_score", 0)
profile.setdefault("grammar_fixes", 0)

# Save back if new keys were added
data[user_email] = profile
save_progress(data)


# ======================================================
# 🎨 DASHBOARD STYLES (CLEAN SaaS)
# ======================================================
st.set_page_config(layout="wide")

st.markdown("""
<style>
body {
    background: linear-gradient(180deg, #020617, #020617);
    font-family: Inter, system-ui, sans-serif;
}

.metric {
    font-size: 34px;
    font-weight: 800;
    color: #38bdf8;
}
.subtle {
    color: #94a3b8;
    font-size: 14px;
}
.action-card:hover {
    border-color: #38bdf8;
    transform: translateY(-2px);
}
</style>
""", unsafe_allow_html=True)

# ======================================================
# 🧭 SIDEBAR NAVIGATION (POST-LOGIN ONLY)
# ======================================================
with st.sidebar:
    st.markdown(f"👋 **{user_name}**")
    st.caption("Resume workspace")

 

    if st.button("🚪 Logout"):
        st.session_state.logged_in = False
        st.switch_page("app.py")

# ======================================================
# 🧠 HEADER
# ======================================================
st.markdown("## 📊 Dashboard")
st.caption("Your resume performance at a glance")





# ======================================================
# 📊 CORE METRICS
# ======================================================
c1, c2, c3 = st.columns(3)

with c1:
    st.markdown(f"""
    <div class="card">
        <div class="metric">{profile["resumes_analyzed"]}</div>
        <div class="subtle">Resumes analyzed</div>
    </div>
    """, unsafe_allow_html=True)

with c2:
    st.markdown(f"""
    <div class="card">
        <div class="metric">{profile["avg_ats_score"]}%</div>
        <div class="subtle">Average ATS readiness</div>
    </div>
    """, unsafe_allow_html=True)

with c3:
    st.markdown(f"""
    <div class="card">
        <div class="metric">{profile["grammar_fixes"]}</div>
        <div class="subtle">Grammar improvements</div>
    </div>
    """, unsafe_allow_html=True)

# ======================================================
# 🧑‍💼 RECRUITER IMPRESSION (HUMAN FRIENDLY)
# ======================================================
st.markdown("### 🧑‍💼 Recruiter Impression")

if profile["avg_ats_score"] >= 80:
    st.success("Your resume is recruiter-ready. Strong technical signals detected.")
elif profile["avg_ats_score"] >= 65:
    st.info("Your resume is competitive. Minor refinements can improve outcomes.")
else:
    st.warning("Your experience is valuable, but impact clarity can be improved.")

# ======================================================
# 🚀 NEXT BEST ACTION
# ======================================================
st.markdown("### 🚀 Recommended Next Step")

if profile["resumes_analyzed"] == 0:
    st.markdown("➡ Start with an ATS analysis to understand how your resume performs.")
elif profile["avg_ats_score"] < 70:
    st.markdown("➡ Improve one experience bullet by adding a measurable outcome.")
else:
    st.markdown("➡ Tailor your resume for a specific job description.")

# ======================================================
# 🧭 QUICK ACTIONS
# ======================================================
st.markdown("### 🧭 Tools")

a1, a2, a3 = st.columns(3)

with a1:
    st.markdown('<div class="card action-card">', unsafe_allow_html=True)
    st.markdown("📊 **ATS Score Checker**")
    st.caption("Understand how ATS & recruiters read your resume")
    if st.button("Open ATS Checker"):
        st.switch_page("pages/2_ATS_Score_Checker.py")
    st.markdown('</div>', unsafe_allow_html=True)

with a2:
    st.markdown('<div class="card action-card">', unsafe_allow_html=True)
    st.markdown("✍️ **Grammar Enhancer**")
    st.caption("Improve clarity, tone, and professionalism")
    if st.button("Open Grammar Enhancer"):
        st.switch_page("pages/3_Grammar_Enhancer.py")
    st.markdown('</div>', unsafe_allow_html=True)

with a3:
   

    st.markdown('<div class="card action-card">', unsafe_allow_html=True)
    st.markdown("🧠 **Resume Builder**")
    st.caption("Create recruiter-ready bullets")
    if  st.button("⭐ Open Resume Builder", use_container_width=True):       
        st.switch_page("pages/4_Resume_Builder.py")
    st.markdown('</div>', unsafe_allow_html=True)

    total_fixes += data.get("grammar_errors", 0)
# -------------------------------
# Normalize user profile (schema-safe)
# -------------------------------
profile = data.get(user_email, {})

profile.setdefault("resumes_analyzed", 0)
profile.setdefault("avg_ats_score", 0)
profile.setdefault("grammar_fixes", 0)

# Save back if new keys were added
data[user_email] = profile
save_progress(data)


# ======================================================
# 🎨 DASHBOARD STYLES (CLEAN SaaS)
# ======================================================
st.set_page_config(layout="wide")

st.markdown("""
<style>
body {
    background: linear-gradient(180deg, #020617, #020617);
    font-family: Inter, system-ui, sans-serif;
}

.metric {
    font-size: 34px;
    font-weight: 800;
    color: #38bdf8;
}
.subtle {
    color: #94a3b8;
    font-size: 14px;
}
.action-card:hover {
    border-color: #38bdf8;
    transform: translateY(-2px);
}
</style>
""", unsafe_allow_html=True)

# ======================================================
# 🧭 SIDEBAR NAVIGATION (POST-LOGIN ONLY)
# ======================================================
with st.sidebar:
    st.markdown(f"👋 **{user_name}**")
    st.caption("Resume workspace")

 

    if st.button("🚪 Logout"):
        st.session_state.logged_in = False
        st.switch_page("app.py")

# ======================================================
# 🧠 HEADER
# ======================================================
st.markdown("## 📊 Dashboard")
st.caption("Your resume performance at a glance")





# ======================================================
# 📊 CORE METRICS
# ======================================================
c1, c2, c3 = st.columns(3)

with c1:
    st.markdown(f"""
    <div class="card">
        <div class="metric">{profile["resumes_analyzed"]}</div>
        <div class="subtle">Resumes analyzed</div>
    </div>
    """, unsafe_allow_html=True)

with c2:
    st.markdown(f"""
    <div class="card">
        <div class="metric">{profile["avg_ats_score"]}%</div>
        <div class="subtle">Average ATS readiness</div>
    </div>
    """, unsafe_allow_html=True)

with c3:
    st.markdown(f"""
    <div class="card">
        <div class="metric">{profile["grammar_fixes"]}</div>
        <div class="subtle">Grammar improvements</div>
    </div>
    """, unsafe_allow_html=True)

# ======================================================
# 🧑‍💼 RECRUITER IMPRESSION (HUMAN FRIENDLY)
# ======================================================
st.markdown("### 🧑‍💼 Recruiter Impression")

if profile["avg_ats_score"] >= 80:
    st.success("Your resume is recruiter-ready. Strong technical signals detected.")
elif profile["avg_ats_score"] >= 65:
    st.info("Your resume is competitive. Minor refinements can improve outcomes.")
else:
    st.warning("Your experience is valuable, but impact clarity can be improved.")

# ======================================================
# 🚀 NEXT BEST ACTION
# ======================================================
st.markdown("### 🚀 Recommended Next Step")

if profile["resumes_analyzed"] == 0:
    st.markdown("➡ Start with an ATS analysis to understand how your resume performs.")
elif profile["avg_ats_score"] < 70:
    st.markdown("➡ Improve one experience bullet by adding a measurable outcome.")
else:
    st.markdown("➡ Tailor your resume for a specific job description.")

# ======================================================
# 🧭 QUICK ACTIONS
# ======================================================
st.markdown("### 🧭 Tools")

a1, a2, a3 = st.columns(3)

with a1:
    st.markdown('<div class="card action-card">', unsafe_allow_html=True)
    st.markdown("📊 **ATS Score Checker**")
    st.caption("Understand how ATS & recruiters read your resume")
    if st.button("Open ATS Checker"):
        st.switch_page("pages/2_ATS_Score_Checker.py")
    st.markdown('</div>', unsafe_allow_html=True)

with a2:
    st.markdown('<div class="card action-card">', unsafe_allow_html=True)
    st.markdown("✍️ **Grammar Enhancer**")
    st.caption("Improve clarity, tone, and professionalism")
    if st.button("Open Grammar Enhancer"):
        st.switch_page("pages/3_Grammar_Enhancer.py")
    st.markdown('</div>', unsafe_allow_html=True)

with a3:
   

    st.markdown('<div class="card action-card">', unsafe_allow_html=True)
    st.markdown("🧠 **Resume Builder**")
    st.caption("Create recruiter-ready bullets")
    if  st.button("⭐ Open Resume Builder", use_container_width=True):        st.switch_page("pages/4_Resume_Builder.py")
    st.markdown('</div>', unsafe_allow_html=True)

    total_fixes += data.get("grammar_errors", 0)
# -------------------------------
# Normalize user profile (schema-safe)
# -------------------------------
profile = data.get(user_email, {})

profile.setdefault("resumes_analyzed", 0)
profile.setdefault("avg_ats_score", 0)
profile.setdefault("grammar_fixes", 0)

# Save back if new keys were added
data[user_email] = profile
save_progress(data)


# ======================================================
# 🎨 DASHBOARD STYLES (CLEAN SaaS)
# ======================================================
st.set_page_config(layout="wide")

st.markdown("""
<style>
body {
    background: linear-gradient(180deg, #020617, #020617);
    font-family: Inter, system-ui, sans-serif;
}

.metric {
    font-size: 34px;
    font-weight: 800;
    color: #38bdf8;
}
.subtle {
    color: #94a3b8;
    font-size: 14px;
}
.action-card:hover {
    border-color: #38bdf8;
    transform: translateY(-2px);
}
</style>
""", unsafe_allow_html=True)

# ======================================================
# 🧭 SIDEBAR NAVIGATION (POST-LOGIN ONLY)
# ======================================================
with st.sidebar:
    st.markdown(f"👋 **{user_name}**")
    st.caption("Resume workspace")

 

    if st.button("🚪 Logout"):
        st.session_state.logged_in = False
        st.switch_page("app.py")

# ======================================================
# 🧠 HEADER
# ======================================================
st.markdown("## 📊 Dashboard")
st.caption("Your resume performance at a glance")





# ======================================================
# 📊 CORE METRICS
# ======================================================
c1, c2, c3 = st.columns(3)

with c1:
    st.markdown(f"""
    <div class="card">
        <div class="metric">{profile["resumes_analyzed"]}</div>
        <div class="subtle">Resumes analyzed</div>
    </div>
    """, unsafe_allow_html=True)

with c2:
    st.markdown(f"""
    <div class="card">
        <div class="metric">{profile["avg_ats_score"]}%</div>
        <div class="subtle">Average ATS readiness</div>
    </div>
    """, unsafe_allow_html=True)

with c3:
    st.markdown(f"""
    <div class="card">
        <div class="metric">{profile["grammar_fixes"]}</div>
        <div class="subtle">Grammar improvements</div>
    </div>
    """, unsafe_allow_html=True)

# ======================================================
# 🧑‍💼 RECRUITER IMPRESSION (HUMAN FRIENDLY)
# ======================================================
st.markdown("### 🧑‍💼 Recruiter Impression")

if profile["avg_ats_score"] >= 80:
    st.success("Your resume is recruiter-ready. Strong technical signals detected.")
elif profile["avg_ats_score"] >= 65:
    st.info("Your resume is competitive. Minor refinements can improve outcomes.")
else:
    st.warning("Your experience is valuable, but impact clarity can be improved.")

# ======================================================
# 🚀 NEXT BEST ACTION
# ======================================================
st.markdown("### 🚀 Recommended Next Step")

if profile["resumes_analyzed"] == 0:
    st.markdown("➡ Start with an ATS analysis to understand how your resume performs.")
elif profile["avg_ats_score"] < 70:
    st.markdown("➡ Improve one experience bullet by adding a measurable outcome.")
else:
    st.markdown("➡ Tailor your resume for a specific job description.")

# ======================================================
# 🧭 QUICK ACTIONS
# ======================================================
st.markdown("### 🧭 Tools")

a1, a2, a3 = st.columns(3)

with a1:
    st.markdown('<div class="card action-card">', unsafe_allow_html=True)
    st.markdown("📊 **ATS Score Checker**")
    st.caption("Understand how ATS & recruiters read your resume")
    if st.button("Open ATS Checker"):
        st.switch_page("pages/2_ATS_Score_Checker.py")
    st.markdown('</div>', unsafe_allow_html=True)

with a2:
    st.markdown('<div class="card action-card">', unsafe_allow_html=True)
    st.markdown("✍️ **Grammar Enhancer**")
    st.caption("Improve clarity, tone, and professionalism")
    if st.button("Open Grammar Enhancer"):
        st.switch_page("pages/3_Grammar_Enhancer.py")
    st.markdown('</div>', unsafe_allow_html=True)

with a3:
   

    st.markdown('<div class="card action-card">', unsafe_allow_html=True)
    st.markdown("🧠 **Resume Builder**")
    st.caption("Create recruiter-ready bullets")
    if  st.button("⭐ Open Resume Builder", use_container_width=True):        st.switch_page("pages/4_Resume_Builder.py")
    st.markdown('</div>', unsafe_allow_html=True)
