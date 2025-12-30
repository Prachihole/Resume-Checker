# pages/2_ATS_Score_Checker.py

import streamlit as st
import re, time
from collections import Counter
import plotly.graph_objects as go
from docx import Document
import language_tool_python

# =========================
# 🔐 LOGIN PROTECTION
# =========================
if "logged_in" not in st.session_state or not st.session_state.logged_in:
    st.warning("⚠️ Please login first")
    st.stop()

# =========================
# 🎨 HEADER
# =========================
st.title("📊 ATS Resume Score Checker")
st.caption("Resume-centric | Explains exactly WHY your score changes")

st.markdown("""
<style>
.kpi {
    background:#ffffff;
    padding:18px;
    border-radius:14px;
    text-align:center;
    box-shadow:0 4px 14px rgba(0,0,0,0.08);
}
.kpi h1 {margin:0;color:#0b7a75;}
.kpi p {margin:0;color:#555;font-size:0.9rem;}
</style>
""", unsafe_allow_html=True)

# =========================
# 🧠 CONSTANTS
# =========================
LANG_TOOL = language_tool_python.LanguageTool('en-US')

ACTION_VERBS = [
    "developed","designed","implemented","led","managed",
    "built","optimized","analyzed","created","improved"
]

SECTIONS = ["experience","education","skills","projects","certifications"]

# =========================
# 📄 TEXT EXTRACTION
# =========================
def extract_text(file):
    if file.name.endswith(".docx"):
        doc = Document(file)
        return "\n".join(p.text for p in doc.paragraphs if p.text)
    return file.getvalue().decode("utf-8", errors="ignore")

# =========================
# 🔍 JD KEYWORDS
# =========================
def extract_jd_keywords(jd_text, top_n=35):
    words = re.findall(r'\b[a-zA-Z][a-zA-Z+\-# ]{2,}\b', jd_text.lower())
    freq = Counter(words)
    return [w for w, _ in freq.most_common(top_n)]

# =========================
# 🧮 ATS ENGINE
# =========================
def ats_engine(resume_text, jd_keywords):
    resume = resume_text.lower()

    matched = [k for k in jd_keywords if k in resume]
    missing = [k for k in jd_keywords if k not in resume]

    keyword_score = int((len(matched)/len(jd_keywords))*30) if jd_keywords else 0

    verb_count = sum(1 for v in ACTION_VERBS if v in resume)
    verb_score = min(12, verb_count * 2)

    metrics = re.findall(r'\b\d+%|\b\d+\s+years?', resume)
    metric_score = min(8, len(metrics) * 2)

    section_count = sum(1 for s in SECTIONS if s in resume)
    structure_score = int((section_count / len(SECTIONS)) * 20)

    grammar_issues = LANG_TOOL.check(resume_text)
    grammar_score = max(0, 15 - (len(grammar_issues)//3))

    formatting_score = 15 if "-" in resume or "•" in resume else 9

    final = min(
        100,
        keyword_score + verb_score + metric_score +
        structure_score + grammar_score + formatting_score
    )

    return {
        "final": final,
        "matched": matched,
        "missing": missing,
        "metrics": metrics,
        "grammar": grammar_issues[:10],
        "scores": {
            "Keywords": keyword_score,
            "Action Verbs": verb_score,
            "Metrics": metric_score,
            "Structure": structure_score,
            "Grammar": grammar_score,
            "Formatting": formatting_score
        }
    }

# =========================
# 🧾 INPUT
# =========================
col1, col2 = st.columns([2,1])

with col1:
    resume_file = st.file_uploader("📤 Upload Resume (DOCX / TXT)", type=["docx","txt"])

with col2:
    jd_text = st.text_area("🧾 Paste Job Description", height=220)

analyze = st.button("🚀 Analyze Resume")

# =========================
# 🚀 OUTPUT
# =========================
if analyze and resume_file and jd_text:
    with st.spinner("Analyzing resume with ATS rules..."):
        resume_text = extract_text(resume_file)
        jd_keywords = extract_jd_keywords(jd_text)
        result = ats_engine(resume_text, jd_keywords)
        time.sleep(0.3)

    # =========================
    # 📌 KPI CARDS
    # =========================
    k1,k2,k3,k4 = st.columns(4)
    k1.markdown(f"<div class='kpi'><h1>{result['final']}%</h1><p>ATS Score</p></div>", unsafe_allow_html=True)
    k2.markdown(f"<div class='kpi'><h1>{len(result['matched'])}</h1><p>Matched JD Keywords</p></div>", unsafe_allow_html=True)
    k3.markdown(f"<div class='kpi'><h1>{len(result['missing'])}</h1><p>Missing Keywords</p></div>", unsafe_allow_html=True)
    k4.markdown(f"<div class='kpi'><h1>{len(result['metrics'])}</h1><p>Metrics Found</p></div>", unsafe_allow_html=True)

    st.divider()

    # =========================
    # 🎯 ATS PROBABILITY
    # =========================
    if result["final"] >= 85:
        st.success("🟢 High ATS shortlisting probability (≈85–90%)")
    elif result["final"] >= 70:
        st.warning("🟡 Moderate probability (≈55–70%)")
    else:
        st.error("🔴 Low probability (<40%)")

    # =========================
    # 🎯 GAUGE
    # =========================
    st.plotly_chart(
        go.Figure(go.Indicator(
            mode="gauge+number",
            value=result["final"],
            title={"text":"ATS Compatibility"},
            gauge={"axis":{"range":[0,100]}}
        )),
        use_container_width=True
    )

    # =========================
    # 📉 SCORE LOSS BREAKDOWN (KEY FIX)
    # =========================
    st.markdown("## 📉 Why your ATS score dropped")

    loss = {
        "Keywords": 30 - result["scores"]["Keywords"],
        "Action Verbs": 12 - result["scores"]["Action Verbs"],
        "Metrics": 8 - result["scores"]["Metrics"],
        "Structure": 20 - result["scores"]["Structure"],
        "Grammar": 15 - result["scores"]["Grammar"],
        "Formatting": 15 - result["scores"]["Formatting"]
    }

    loss_sorted = sorted(loss.items(), key=lambda x: x[1], reverse=True)

    for sec, pts in loss_sorted:
        if pts > 0:
            st.write(f"❌ **{sec}** reduced your score by **{pts} points**")

    # =========================
    # 🔍 KEYWORD ANALYSIS (TEXT ONLY)
    # =========================
    matched_pct = int((len(result["matched"]) / len(jd_keywords))*100) if jd_keywords else 0

    st.markdown("## 🔍 Keyword Match Analysis")
    st.write(f"You matched **{len(result['matched'])}/{len(jd_keywords)} JD keywords** (**{matched_pct}% match rate**).")

    if result["missing"]:
        st.write("### 🔴 Highest-impact missing keywords:")
        for kw in result["missing"][:6]:
            st.write(f"- {kw}")

    # =========================
    # ✍️ GRAMMAR IMPACT
    # =========================
    grammar_loss = 15 - result["scores"]["Grammar"]
    st.markdown("## ✍️ Grammar Impact")
    st.write(f"Grammar issues reduced your ATS score by **{grammar_loss} points**.")

    # =========================
    # 🚀 PRIORITY FIXES
    # =========================
    st.markdown("## 🚀 Top 3 Actions to Increase Score Fast")

    priority = []
    if loss["Keywords"] > 6:
        priority.append("Add missing JD keywords naturally into Skills & Experience")
    if loss["Metrics"] > 4:
        priority.append("Add measurable results (%, years, scale, impact)")
    if loss["Grammar"] > 4:
        priority.append("Fix grammar issues")
    if loss["Structure"] > 4:
        priority.append("Ensure clear sections: Experience, Skills, Education")

    for i, p in enumerate(priority[:3], 1):
        st.write(f"**{i}.** {p}")

else:
    st.info("Upload resume and JD, then click **Analyze Resume**")
