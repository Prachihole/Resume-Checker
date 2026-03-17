# =
from firebase_config import db
from datetime import datetime

import json
import os
import streamlit as st
import language_tool_python
import html
import re

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
# ====================== PAGE CONFIG (FIRST CALL) ======================
st.set_page_config(
    page_title="Grammar Enhancer",
    page_icon="✍️",
    layout="wide"
)

# ====================== LOGIN CHECK ======================
if not st.session_state.get("logged_in", False):
    st.warning("⚠️ Please log in to access Grammar Enhancer.")
    st.stop()

# ====================== SESSION STATE INIT ======================
if "input_text" not in st.session_state:
    st.session_state.input_text = ""

if "last_msg" not in st.session_state:
    st.session_state.last_msg = ""

# ====================== INIT LANGUAGE TOOL ======================
@st.cache_resource
def load_tool():
    try:
        return language_tool_python.LanguageToolPublicAPI("en-US")
    except Exception:
        return None

tool = load_tool()


# ====================== HELPERS ======================
def detect_extra_issues(text):
    issues = []

    for m in re.finditer(r" {2,}", text):
        issues.append({
            "start": m.start(),
            "end": m.end(),
            "msg": "Extra spaces detected",
            "fix": " "
        })

    for m in re.finditer(r"\s+[.,!?;:]", text):
        issues.append({
            "start": m.start(),
            "end": m.end(),
            "msg": "Unwanted space before punctuation",
            "fix": text[m.start():m.end()].strip()
        })

    return issues


def build_highlighted_html(text, matches, extra):
    items = []

    for m in matches:
        items.append({
            "start": m.offset,
            "end": m.offset + m.errorLength,
            "msg": m.message,
            "fix": m.replacements[0] if m.replacements else ""
        })

    items.extend(extra)
    items.sort(key=lambda x: x["start"])

    out, last = [], 0
    for it in items:
        out.append(html.escape(text[last:it["start"]]))
        snippet = html.escape(text[it["start"]:it["end"]])
        title = html.escape(it["msg"] + (" → " + it["fix"] if it["fix"] else ""))
        out.append(f"<mark title='{title}'>{snippet}</mark>")
        last = it["end"]

    out.append(html.escape(text[last:]))

    return f"""
    <div class="box">{''.join(out)}</div>
    <style>
        .box {{
            white-space: pre-wrap;
            line-height: 1.6;
            font-size: 16px;
        }}
        mark {{
            background: #fff3b0;
            border-radius: 4px;
            padding: 2px 3px;
            cursor: help;
        }}
    </style>
    """

# ====================== CALLBACKS ======================
def apply_all():
    if tool:
        st.session_state.input_text = tool.correct(st.session_state.input_text)
        st.session_state.last_msg = "✅ All suggestions applied"
    else:
        st.session_state.last_msg = "⚠️ Grammar service unavailable"

def clear_text():
    st.session_state.input_text = ""
    st.session_state.last_msg = "🧹 Text cleared"

# ====================== UI ======================
st.markdown("<h1 style='text-align:center'>✍️ Grammar Enhancer</h1>", unsafe_allow_html=True)
st.caption("Professional grammar correction with smart highlighting — ATS friendly ✨")

st.text_area(
    "Paste your text below",
    key="input_text",
    height=260
)

c1, c2, c3 = st.columns(3)
with c1:
    check = st.button("🔍 Check Grammar", use_container_width=True)
with c2:
    st.button("✅ Apply All Fixes", on_click=apply_all, use_container_width=True)
with c3:
    st.button("🧹 Clear", on_click=clear_text, use_container_width=True)

if st.session_state.last_msg:
    st.success(st.session_state.last_msg)
    st.session_state.last_msg = ""

# ====================== ANALYSIS ======================

# ====================== ANALYSIS ======================
if check:
    text = st.session_state.input_text.strip()
    if len(text) > 5000:
         st.warning("Text too long. Please shorten it.")
         st.stop()
    if not text:
        st.warning("Please paste some text first.")
    else:
        with st.spinner("Analyzing text..."):
            try:
               if tool:
                 matches = tool.check(text)
               else:
                  matches = []
                  st.warning("⚠️ Grammar service is temporarily busy. Please try again in a few seconds.")
            except Exception:
                  matches = []
                  st.warning("Grammar service temporarily unavailable.")
            extra = detect_extra_issues(text)

        grammar_errors = len(matches)

        # ================= FIREBASE SAVE =================
        firebase_data = {
          "email": st.session_state.user_email,
          "grammar_errors": grammar_errors,
          "timestamp": datetime.utcnow()
}

        db.collection("grammar_checks").add(firebase_data)

        # ================= LOCAL DASHBOARD UPDATE =================
        user_email = st.session_state.user_email
        progress_data = load_progress()

        if user_email not in progress_data:
            progress_data[user_email] = normalize_profile({})

        profile = normalize_profile(progress_data[user_email])
        profile["grammar_fixes"] += grammar_errors

        progress_data[user_email] = profile
        save_progress(progress_data)

        # ================= HIGHLIGHT ERRORS =================
        st.markdown("### 🔎 Highlighted Grammar Issues")

        st.markdown(
            build_highlighted_html(text, matches, extra),
            unsafe_allow_html=True
        )

        # ================= SUMMARY =================
        st.markdown("### 📊 Analysis Summary")

        st.info(
            f"Grammar mistakes detected: {len(matches)}  \n"
            f"Spacing / punctuation issues: {len(extra)}  \n"
            f"Total issues: {len(matches) + len(extra)}"
        )

        # ================= CORRECTED VERSION =================
        corrected = tool.correct(text) if tool else text

        st.markdown("### ✅ Corrected Version")

        st.text_area(
            "Improved text",
            corrected,
            height=220,
            disabled=True
        )

        st.download_button(
            "⬇ Download Corrected Text",
            data=corrected,
            file_name="corrected_text.txt",
            use_container_width=True
        )
# ================= DASHBOARD UPDATE =================
