import streamlit as st
import json
import os


USER_PROGRESS_FILE = "user_progress.json"
@st.cache_resource
def load_model():
    from sentence_transformers import SentenceTransformer
    return SentenceTransformer("all-MiniLM-L6-v2")

model = load_model()

def load_progress():
    if not os.path.exists(USER_PROGRESS_FILE):
        with open(USER_PROGRESS_FILE, "w") as f:
            json.dump({}, f)
    with open(USER_PROGRESS_FILE, "r") as f:
        return json.load(f)

def save_progress(data):
    with open(USER_PROGRESS_FILE, "w") as f:
        json.dump(data, f, indent=2)

def normalize_profile(profile):
    defaults = {
        "resumes_analyzed": 0,
        "avg_ats_score": 0,
        "grammar_fixes": 0,
        "ats_history": []
    }
    for k, v in defaults.items():
        profile.setdefault(k, v)
    return profile


if not st.session_state.get("logged_in", False):
    st.warning("Please log in to access this page.")
    st.stop()

import streamlit as st
import docx2txt
import re
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity

# ==========================================================
# PAGE CONFIG
# ==========================================================
st.set_page_config(
    page_title="ATS Resume Checker",
    page_icon="📊",
    layout="wide"
)

st.markdown("## 📊 ATS Resume Checker")
st.caption(
    "Professional ATS readiness & recruiter impact analysis · "
    "Clear guidance · Confidence-first UX"
)

# ==========================================================
# LOAD MODEL
# ==========================================================
@st.cache_resource
def load_model():
    return SentenceTransformer("all-MiniLM-L6-v2")

model = load_model()

# ==========================================================
# CONSTANTS
# ==========================================================
ACTION_VERBS = [
    "built","developed","designed","implemented","created",
    "optimized","improved","trained","deployed","analyzed"
]

LEADERSHIP_VERBS = [
    "led","owned","managed","coordinated","mentored"
]

RESULT_PATTERNS = [
    r"\d+%", r"\d+x", r"\d+\+?",
    "accuracy","reduced","improved","increased"
]

TECH_HINTS = [
    "opencv","mediapipe","tensorflow","pytorch",
    "machine learning","deep learning",
    "computer vision","ai","model","pipeline"
]

IGNORE_LINES = [
    "@","http","linkedin","github","email","phone",
    "skills","education","objective","summary"
]

# ==========================================================
# HELPERS
# ==========================================================
def extract_text(file):
    if file.name.endswith(".docx"):
        return docx2txt.process(file)
    return file.read().decode("utf-8", errors="ignore")

def clean_lines(text):
    return [l.strip() for l in text.split("\n") if len(l.strip()) > 10]

def extract_keywords(text):
    return set(re.findall(r"[a-zA-Z][a-zA-Z+.#]+", text.lower()))

def semantic_similarity(a, b):
    if not b.strip():
        return 0.55  # neutral baseline when JD is vague
    emb = model.encode([a, b])
    return cosine_similarity([emb[0]], [emb[1]])[0][0]

def extract_experience_bullets(lines):
    bullets = []
    for l in lines:
        low = l.lower()
        if any(i in low for i in IGNORE_LINES):
            continue
        if any(v in low for v in ACTION_VERBS):
            bullets.append(l)
    return bullets

# ==========================================================
# BULLET IMPACT SCORING (FAIR, RECRUITER-ALIGNED)
# ==========================================================
def impact_score(bullet, jd_keywords):
    t = bullet.lower()
    score = 0

    has_action = any(v in t for v in ACTION_VERBS)
    has_metric = any(re.search(p, t) for p in RESULT_PATTERNS)
    has_leadership = any(v in t for v in LEADERSHIP_VERBS)
    has_tech = any(k in t for k in jd_keywords) or any(h in t for h in TECH_HINTS)

    if has_action:
        score += 25
    if has_tech:
        score += 25
    if has_metric:
        score += 25
    if has_leadership:
        score += 15

    # Floors (important for UX fairness)
    if has_action and has_tech:
        score = max(score, 50)
    if has_action and has_tech and has_metric:
        score = max(score, 75)

    return min(score, 100)

# ==========================================================
# INPUTS
# ==========================================================
resume_file = st.file_uploader(
    "📤 Upload Resume (DOCX / TXT)",
    type=["docx","txt"]
)

jd_text = st.text_area(
    "🧾 Paste Job Description (optional but recommended)",
    height=120
)

if not resume_file:
    st.info("Upload your resume to begin analysis.")
    st.stop()

# ==========================================================
# PROCESS RESUME
# ==========================================================
resume_text = extract_text(resume_file)
lines = clean_lines(resume_text)
bullets = extract_experience_bullets(lines)

jd_keywords = extract_keywords(jd_text)
resume_keywords = extract_keywords(resume_text)

semantic_match = semantic_similarity(resume_text, jd_text)
matched_keywords = [k for k in jd_keywords if k in resume_keywords]

high_impact_bullets = sum(
    1 for b in bullets if impact_score(b, jd_keywords) >= 75
)

# ==========================================================
# ATS SCORE (CALIBRATED, CONFIDENCE-SAFE)
# ==========================================================
skill_score = min(semantic_match * 40, 40)
keyword_score = (len(matched_keywords) / max(len(jd_keywords), 1)) * 25
experience_score = 20 if high_impact_bullets >= 1 else 12
formatting_score = 15

overall_ats = round(
    skill_score + keyword_score + experience_score + formatting_score
)

# Confidence floor (VERY IMPORTANT)
if experience_score >= 12 and formatting_score == 15 and overall_ats < 65:
    overall_ats = 65

from firebase_config import db
from datetime import datetime

missing_keywords = [k for k in jd_keywords if k not in resume_keywords]

data = {
    "email": st.session_state.get("email", "unknown"),
    "ats_score": overall_ats,
    "missing_keywords": missing_keywords,
    "grammar_issues": 0,
    "timestamp": datetime.utcnow()
}

db.collection("ats_results").add(data)


# ======================================================
# 📊 UPDATE DASHBOARD METRICS (SOURCE OF TRUTH)
# ======================================================
user_email = st.session_state.user_email

data = load_progress()

if user_email not in data:
    data[user_email] = normalize_profile({})

profile = normalize_profile(data[user_email])

# Update resume count
previous_count = profile["resumes_analyzed"]
previous_avg = profile["avg_ats_score"]

new_count = previous_count + 1

# Running average formula
new_avg = round(
    ((previous_avg * previous_count) + overall_ats) / new_count,
    1
)

profile["resumes_analyzed"] = new_count
profile["avg_ats_score"] = new_avg

data[user_email] = profile
save_progress(data)


# ==========================================================
# BADGES (PRIMARY UX)
# ==========================================================
badges = []

if overall_ats >= 70:
    badges.append("🏷️ ATS-Ready")

if high_impact_bullets >= 1:
    badges.append("🏷️ Recruiter-Ready")

if overall_ats >= 65 and high_impact_bullets == 0:
    badges.append("🏷️ Impact Can Be Strengthened")


from datetime import datetime

# ======================================================
# 🕒 SAVE ATS ANALYSIS HISTORY
# ======================================================
# Ensure verdict is defined before creating the analysis entry
if overall_ats >= 80:
    verdict = "🟢 High confidence for ATS & recruiter review"
elif overall_ats >= 65:
    verdict = "🟡 Good ATS confidence · Moderate recruiter clarity"
else:
    verdict = "🟠 Needs clarity for ATS screening"
jd_keywords_list = list(jd_keywords)
matched_keywords_list = list(matched_keywords)

analysis_entry = {
    "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M"),
    "ats_score": overall_ats,
    "verdict": verdict.replace("🟢","").replace("🟡","").replace("🟠","").replace("🔴","").strip(),
    "jd_keywords": jd_keywords_list[:5],
"matched_keywords": matched_keywords_list[:5],

    "high_impact_bullets": high_impact_bullets
}

profile["ats_history"].insert(0, analysis_entry)

# Keep last 10 analyses only (UX choice)
profile["ats_history"] = profile["ats_history"][:10]

data[user_email] = profile
save_progress(data)





# ==========================================================
# CONFIDENCE METER
# ==========================================================
if overall_ats >= 80:
    confidence_level = "🟢 High confidence for ATS & recruiter review"
elif overall_ats >= 65:
    confidence_level = "🟡 Good ATS confidence · Moderate recruiter clarity"
else:
    confidence_level = "🟠 Needs clarity for ATS screening"

# ==========================================================
# DISPLAY — SCORE & BADGES
# ==========================================================
st.divider()
c1, c2 = st.columns([1,2])

with c1:
    st.metric("ATS Readiness Score", f"{overall_ats} / 100")
    st.caption(
        "This score reflects how clearly your resume communicates "
        "its value to ATS systems and recruiters."
    )

with c2:
    st.markdown("### Readiness Badges")
    for b in badges:
        st.markdown(f"- {b}")

    st.markdown("### 📈 Resume Confidence Level")
    st.info(confidence_level)

# ==========================================================
# RECRUITER IMPRESSION (HUMAN VIEW)
# ==========================================================
st.divider()
st.subheader("🧑‍💼 Recruiter Impression")

if high_impact_bullets >= 1:
    st.success(
        "Strong technical profile. Your resume demonstrates real "
        "AI-driven project impact and is likely to engage recruiters."
    )
else:
    st.info(
        "Technically solid resume. Recruiters will understand your skills, "
        "but clearer impact statements can improve engagement."
    )

# ==========================================================
# CONDITIONAL UX MESSAGING (CRITICAL)
# ==========================================================
st.divider()

if overall_ats >= 80 and high_impact_bullets >= 1:
    st.subheader("✅ What’s Working Well")
    st.markdown(
        """
        Your resume clearly communicates:
        • Real AI / technical project experience  
        • Practical, real-world relevance  
        • Measurable or validated outcomes  

        Only optional refinements are shown below.
        """
    )

elif overall_ats >= 65:
    st.subheader("🚀 One Opportunity to Strengthen Impact")
    st.markdown(
        """
        Your resume contains strong technical work.
        A **small change** in how one project is presented
        can significantly improve recruiter clarity.

        **Best next step:**  
        → Combine related bullets and highlight one clear result.
        """
    )

else:
    st.subheader("⚠️ Needs Attention")
    st.markdown(
        """
        Your resume has relevant content, but impact is not yet clear
        to ATS systems. Improving experience descriptions will
        greatly increase visibility.
        """
    )


# ==========================================================
# PROJECT-LEVEL INSIGHT
# ==========================================================
st.divider()
st.subheader("🧠 Project-Level Insight")

if bullets:
    st.write(
        "One or more strong technical projects detected. "
        "Impact is best communicated when related details are "
        "combined into 1–2 complete, results-driven bullets."
    )
else:
    st.warning("No clear experience or project bullets detected.")

# ==========================================================
# OPTIONAL BULLET DETAILS (SUPPORTING ONLY)
# ==========================================================
with st.expander("🔍 Supporting Project Details (Optional)"):
    st.caption(
        "These bullets support your main project impact and "
        "do not negatively affect ATS screening."
    )

    for i, b in enumerate(bullets[:6], 1):
        s = impact_score(b, jd_keywords)
        badge = "🟢" if s >= 75 else "🟡" if s >= 60 else "⚪"

        st.markdown(f"**Detail {i} — Impact Strength: {s} / 100 {badge}**")
        st.markdown(f"> {b}")

# ==========================================================
# FOOTER
# ==========================================================
st.divider()
st.caption(
    "Professional, resume-based ATS analysis · "
    "Recruiter-aligned · Confidence-first UX · No fake penalties"
)


