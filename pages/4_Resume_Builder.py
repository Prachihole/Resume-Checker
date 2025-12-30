import streamlit as st
from docx import Document
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from datetime import datetime
from io import BytesIO
from PIL import Image
import language_tool_python
import re, json, os
from pathlib import Path

# ====================== LOGIN CHECK ======================
if "logged_in" not in st.session_state or not st.session_state.logged_in:
    st.warning("⚠️ Please log in first.")
    st.stop()

st.set_page_config(page_title="Smart Resume Builder 4.0", page_icon="🧠", layout="wide")

st.markdown("""
<h1 style='text-align:center;background: -webkit-linear-gradient(#00FFFF,#FF63E0);
-webkit-background-clip: text;-webkit-text-fill-color: transparent;'>🧠 Smart Resume Builder 4.0</h1>
""", unsafe_allow_html=True)
st.caption("Design your own one-page resume. Add, remove, and reorder sections easily 🚀")

# ====================== BASIC INFO ======================
col1, col2 = st.columns([2, 1])
with col1:
    name = st.text_input("👤 Full Name", st.session_state.get("user_name", ""))
    job_title = st.text_input("💼 Target Job Title", placeholder="e.g., AI Engineer / Data Scientist")
    email = st.text_input("✉️ Email", st.session_state.get("user_email", ""))
    phone = st.text_input("📞 Phone Number", placeholder="+91 9876543210")
    linkedin = st.text_input("🔗 LinkedIn", placeholder="https://linkedin.com/in/yourprofile")
    github = st.text_input("💻 GitHub", placeholder="https://github.com/yourprofile")
with col2:
    st.markdown("📸 **Upload Profile Photo (optional)**")
    photo = st.file_uploader("Upload JPG/PNG", type=["jpg", "jpeg", "png"])
    img_path = None
    if photo:
        image = Image.open(photo)
        image.thumbnail((150, 150))
        st.image(image, caption="Profile Preview")
        img_path = f"profile_{st.session_state['user_email']}.png"
        image.save(img_path)

# ====================== SECTION TOGGLES ======================
st.markdown("## 🧩 Select Sections to Include")
default_sections = {
    "Professional Summary": True,
    "Skills": True,
    "Experience": True,
    "Projects": True,
    "Education": True
}
section_states = {}
for sec, default in default_sections.items():
    section_states[sec] = st.checkbox(f"Include {sec}", value=default, key=f"chk_{sec}")

# ====================== EXTRA CUSTOM SECTIONS ======================
st.markdown("## ➕ Add Custom Sections")
if "custom_sections" not in st.session_state:
    st.session_state.custom_sections = []

new_section = st.text_input("Enter a new section name (e.g., Certifications, Achievements)")
if st.button("Add Section"):
    if new_section and new_section not in st.session_state.custom_sections:
        st.session_state.custom_sections.append(new_section)
        st.success(f"✅ Added '{new_section}'")

for sec in st.session_state.custom_sections:
    st.text_area(f"✏️ {sec} Details", key=f"custom_{sec}")

# ====================== MAIN SECTIONS (conditional) ======================
if section_states["Professional Summary"]:
    summary = st.text_area("🧠 Professional Summary",
        placeholder="Passionate AI engineer skilled in machine learning, NLP, and Python development.")
else:
    summary = ""

if section_states["Skills"]:
    skills = st.text_area("🧩 Skills", placeholder="Python, TensorFlow, Machine Learning, Communication")
else:
    skills = ""

if section_states["Experience"]:
    experience = st.text_area("🏢 Experience", placeholder="Intern at ABC Corp – Built automation scripts for ML pipelines.")
else:
    experience = ""

if section_states["Projects"]:
    projects = st.text_area("💼 Projects", placeholder="AI Chatbot – Flask, NLP\nResume Analyzer – Python, Streamlit")
else:
    projects = ""

if section_states["Education"]:
    education = st.text_area("🎓 Education", placeholder="B.Tech in Computer Science – XYZ University (2021–2025)")
else:
    education = ""

theme = st.selectbox("🎨 Choose Theme", ["Elegant (Blue)", "Minimal (Gray)"])
heading_color = RGBColor(0, 102, 255) if "Blue" in theme else RGBColor(90, 90, 90)

# ====================== DOCX GENERATION ======================
def create_resume():
    doc = Document()
    for s in doc.sections:
        s.top_margin = s.bottom_margin = Inches(0.5)
        s.left_margin = s.right_margin = Inches(0.6)

    # Header
    hdr = doc.add_paragraph()
    hdr.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r = hdr.add_run(name)
    r.bold = True; r.font.size = Pt(22); r.font.color.rgb = heading_color
    doc.add_paragraph(job_title).alignment = WD_ALIGN_PARAGRAPH.CENTER
    doc.add_paragraph(f"{email} | {phone} | {linkedin} | {github}").alignment = WD_ALIGN_PARAGRAPH.CENTER
    if img_path and os.path.exists(img_path):
        doc.add_picture(img_path, width=Inches(1.1))

    # Add sections dynamically
    def add_section(title, text):
        if text.strip():
            doc.add_heading(title, level=1)
            for line in text.split("\n"):
                if line.strip():
                    doc.add_paragraph("• " + line.strip())

    add_section("Professional Summary", summary)
    add_section("Skills", skills.replace(",", "\n"))
    add_section("Experience", experience)
    add_section("Projects", projects)
    add_section("Education", education)

    # Custom user-added sections
    for sec in st.session_state.custom_sections:
        add_section(sec, st.session_state.get(f"custom_{sec}", ""))

    doc.add_paragraph(f"\nGenerated on {datetime.now().strftime('%d-%b-%Y')} • Smart Resume Builder 4.0").alignment = WD_ALIGN_PARAGRAPH.CENTER

    buffer = BytesIO()
    doc.save(buffer)
    buffer.seek(0)
    return buffer

# ====================== ATS + GRAMMAR ANALYSIS ======================
def ats_analysis(text):
    score = 50
    keywords = ["python","machine learning","data analysis","tensorflow","pytorch","nlp","sql","communication","leadership","problem solving"]
    found = [k for k in keywords if k in text.lower()]
    score += len(found)*3
    if len(text.split()) > 200: score += 5
    if "linkedin" in text.lower(): score += 3
    if job_title.lower() in text.lower(): score += 5
    return min(score,100), found

def grammar_feedback(text):
    tool = language_tool_python.LanguageTool("en-US")
    issues = tool.check(text)
    return [f"{m.message} → Suggestion: {m.replacements[0] if m.replacements else ''}" for m in issues[:8]]

# ====================== GENERATE BUTTON ======================
if st.button("🚀 Generate Resume and Analyze"):
    if not name or not email or not phone:
        st.warning("Please fill your basic details first.")
    else:
        docx_file = create_resume()
        combined_text = " ".join([
            summary, skills, projects, experience, education,
            *[st.session_state.get(f"custom_{sec}", "") for sec in st.session_state.custom_sections]
        ])
        ats_score, found_keys = ats_analysis(combined_text)
        grammar_issues = grammar_feedback(combined_text)

        st.success(f"✅ Resume generated! ATS Score: {ats_score}%")

        st.markdown("### 📊 ATS Insights")
        st.progress(ats_score / 100)
        st.write(f"**Matched Keywords:** {', '.join(found_keys) or 'None'}")
        st.write(f"**Grammar Suggestions:** {len(grammar_issues)} found")
        for g in grammar_issues:
            st.markdown(f"- {g}")

        st.download_button("⬇️ Download DOCX",
            data=docx_file,
            file_name=f"{name}_Resume.docx",
            mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document")

        # Save progress
        fpath = Path("user_progress.json")
        if fpath.exists():
            data = json.load(open(fpath))
            email_key = st.session_state["user_email"]
            if email_key in data:
                data[email_key]["resumes_built"] += 1
                data[email_key]["ats_score_avg"] = (data[email_key]["ats_score_avg"] + ats_score) / 2
                json.dump(data, open(fpath, "w"), indent=2)
