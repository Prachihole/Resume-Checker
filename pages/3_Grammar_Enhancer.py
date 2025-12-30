# pages/3_Grammar_Enhancer.py
import streamlit as st
import language_tool_python
from pathlib import Path
import json
import html
import re

# ====================== PAGE CONFIG (first Streamlit call) ======================
st.set_page_config(page_title="Grammar Highlighter", page_icon="✍️", layout="wide")

# ====================== LOGIN CHECK (defensive) ======================
if "logged_in" not in st.session_state:
    st.session_state["logged_in"] = True  # set to True for local dev; change as needed

if not st.session_state.get("logged_in", False):
    st.warning("⚠️ Please log in first.")
    st.stop()

# ====================== Init LanguageTool ======================
try:
    tool = language_tool_python.LanguageTool("en-US")
except Exception as e:
    st.error(
        "❌ Could not start LanguageTool. Ensure `language-tool-python` is installed and Java is available. "
        "Try `pip install language-tool-python` and make sure Java is on PATH."
    )
    st.stop()

# ====================== Helpers ======================
def safe_str(x):
    return "" if x is None else str(x)

def build_highlighted_html(text, matches, extra_issues):
    full = text or ""
    issues = []
    for m in matches:
        off = getattr(m, "offset", None)
        length = getattr(m, "errorLength", None) or getattr(m, "length", None)
        if off is None or length is None:
            continue
        start = int(off)
        end = int(off + length)
        repls = getattr(m, "replacements", None) or []
        replacement = repls[0] if repls else ""
        issues.append({
            "start": start,
            "end": end,
            "type": "grammar",
            "message": safe_str(getattr(m, "message", "")),
            "replacement": replacement,
            "ruleId": safe_str(getattr(m, "ruleId", "")),
        })

    for ei in extra_issues:
        issues.append({
            "start": int(ei["start"]),
            "end": int(ei["end"]),
            "type": ei.get("type", "other"),
            "message": safe_str(ei.get("message", "")),
            "replacement": safe_str(ei.get("replacement", "")),
        })

    issues = sorted(issues, key=lambda x: (x["start"], -(x["end"] - x["start"])))

    parts = []
    cursor = 0
    for issue in issues:
        s, e = issue["start"], issue["end"]
        if s < cursor:
            continue
        parts.append(html.escape(full[cursor:s]))
        snippet = full[s:e]
        title_msg = issue.get("message", "")
        repl = issue.get("replacement", "")
        if callable(repl):
            try:
                repl_val = repl(snippet)
            except Exception:
                repl_val = ""
        else:
            repl_val = "" if repl is None else str(repl)
        title = html.escape(title_msg)
        if repl_val:
            title += " | Suggestion: " + html.escape(repl_val)

        css_class = "issue-grammar"
        if issue.get("type") == "spacing":
            css_class = "issue-spacing"
        elif issue.get("type") == "punct":
            css_class = "issue-punct"

        parts.append(f"<mark class='{css_class}' title='{title}'>{html.escape(snippet)}</mark>")
        cursor = e

    parts.append(html.escape(full[cursor:]))

    highlighted = (
        "<div class='highlight-area'>"
        + "".join(parts)
        + "</div>"
        + """
        <style>
        .highlight-area { white-space: pre-wrap; font-family: inherit; line-height: 1.45; }
        mark.issue-grammar { background: #fff3b0; border-radius: 3px; padding: 0 2px; }
        mark.issue-spacing { background: #ffd1b3; border-radius: 3px; padding: 0 2px; }
        mark.issue-punct { background: #b3f0ff; border-radius: 3px; padding: 0 2px; }
        mark { cursor: help; }
        </style>
        """
    )
    return highlighted

def detect_extra_issues(text):
    extra = []
    if not text:
        return extra

    for m in re.finditer(r" {2,}", text):
        extra.append({
            "start": m.start(),
            "end": m.end(),
            "type": "spacing",
            "message": f"Extra spaces ({m.end() - m.start()} spaces).",
            "replacement": " "
        })

    idx = 0
    for line in text.splitlines(True):
        m_trail = re.search(r"\s+$", line)
        if m_trail:
            s = idx + m_trail.start()
            e = idx + m_trail.end()
            extra.append({
                "start": s,
                "end": e,
                "type": "spacing",
                "message": "Trailing whitespace on this line.",
                "replacement": ""
            })
        m_lead = re.match(r"^\s+", line)
        if m_lead:
            s = idx + m_lead.start()
            e = idx + m_lead.end()
            extra.append({
                "start": s,
                "end": e,
                "type": "spacing",
                "message": "Leading whitespace on this line.",
                "replacement": ""
            })
        idx += len(line)

    for m in re.finditer(r"\s+[,\.;:!?]", text):
        offending = text[m.start():m.end()]
        suggested = offending.strip()
        extra.append({
            "start": m.start(),
            "end": m.end(),
            "type": "punct",
            "message": "Unwanted space before punctuation.",
            "replacement": suggested
        })

    return extra

def apply_single_replacement(current_text, snippet, replacement, prefer_pos=0):
    if not snippet:
        return current_text, False, -1
    idx = current_text.find(snippet, max(0, prefer_pos - 10))
    if idx == -1 and snippet.strip() != snippet:
        idx = current_text.find(snippet.strip(), max(0, prefer_pos - 10))
    if idx == -1:
        sample = snippet.strip()[:6]
        if sample:
            idx = current_text.find(sample)
    if idx == -1:
        return current_text, False, -1
    new_text = current_text[:idx] + replacement + current_text[idx + len(snippet):]
    return new_text, True, idx

# ====================== Callbacks (safe modifications) ======================
def cb_clear_text():
    st.session_state["input_text"] = ""
    # no need to call experimental_rerun() here — Streamlit will rerun after callback returns

def cb_apply_all():
    cur = st.session_state.get("input_text", "")
    try:
        corrected_all = tool.correct(cur or "")
        st.session_state["input_text"] = corrected_all
    except Exception as e:
        st.session_state["_last_error"] = f"Bulk apply error: {e}"

def cb_apply_single(snippet, replacement, prefer_pos):
    current = st.session_state.get("input_text", "")
    new_text, applied, pos = apply_single_replacement(current, snippet, replacement or "", prefer_pos=prefer_pos or 0)
    if applied:
        st.session_state["input_text"] = new_text
        st.session_state["_last_msg"] = f"Applied single replacement at pos {pos}."
    else:
        st.session_state["_last_msg"] = "Could not apply single replacement (snippet not found)."

# ====================== Page UI ======================
st.markdown("<h1 style='text-align:center'>✍️ Grammar Highlighter</h1>", unsafe_allow_html=True)
st.caption("Highlights grammar, spacing and punctuation issues — hover over highlights to see suggestions.")

# create text area (value comes from session_state)
if "input_text" not in st.session_state:
    st.session_state["input_text"] = ""

text = st.text_area("Paste your text here", value=st.session_state["input_text"], height=350, key="input_text")

col1, col2, col3, col4 = st.columns([1,1,1,1])
with col1:
    check = st.button("🔍 Highlight Issues")
with col2:
    # use on_click to safely mutate session_state
    st.button("✅ Apply All Suggestions", on_click=cb_apply_all)
with col3:
    st.button("🧹 Clear Text", on_click=cb_clear_text)
with col4:
    if st.button("⬇️ Download Original"):
        st.download_button("Download original (TXT)", data=st.session_state.get("input_text",""), file_name="original_text.txt")

# show last messages from callbacks
if st.session_state.get("_last_msg"):
    st.info(st.session_state.pop("_last_msg"))
if st.session_state.get("_last_error"):
    st.error(st.session_state.pop("_last_error"))

# Main check flow (only runs when check pressed)
if check:
    cur_text = st.session_state.get("input_text", "")
    if not (cur_text and cur_text.strip()):
        st.warning("Please enter some text to check.")
    else:
        with st.spinner("Analyzing text..."):
            try:
                matches = tool.check(cur_text)
            except Exception as e:
                st.error("LanguageTool error: " + str(e))
                matches = []

            extra = detect_extra_issues(cur_text)
            highlighted_html = build_highlighted_html(cur_text, matches, extra)
            st.markdown("### 🔎 Highlighted Text (hover to see suggestions):")
            st.markdown(highlighted_html, unsafe_allow_html=True)

            # Show list with per-item Apply buttons (use on_click + args)
            if matches or extra:
                st.markdown("### ✨ Detected Issues & Actions")
                for i, m in enumerate(matches, start=1):
                    off = getattr(m, "offset", None)
                    length = getattr(m, "errorLength", None) or getattr(m, "length", None)
                    snippet = (cur_text[off: off + length] if (off is not None and length is not None) else "")
                    replacements = getattr(m, "replacements", None) or []
                    suggested = replacements[0] if replacements else ""
                    st.markdown(f"**{i}.** {safe_str(getattr(m, 'message', ''))}")
                    if snippet:
                        st.write(f"Problem: `{snippet}` — position {off}:{off+length}")
                    if suggested:
                        st.write(f"Suggestion: `{suggested}`")
                    # per-item apply button using on_click
                    btn_key = f"apply_match_btn_{i}"
                    st.button(f"Apply suggestion {i}", key=btn_key,
                              on_click=cb_apply_single, args=(snippet, suggested, off or 0))
                    st.markdown("---")

                base_idx = len(matches)
                for j, ei in enumerate(extra, start=1):
                    idx_label = base_idx + j
                    snip = cur_text[ei["start"]:ei["end"]]
                    st.markdown(f"**{idx_label}.** {ei.get('message','')}")
                    if snip:
                        st.write(f"Problem: `{snip}` — position {ei['start']}:{ei['end']}")
                    if ei.get("replacement") is not None:
                        st.write(f"Suggestion: `{ei.get('replacement')}`")
                    btn_key = f"apply_extra_btn_{idx_label}"
                    st.button(f"Apply suggestion {idx_label}", key=btn_key,
                              on_click=cb_apply_single, args=(snip, ei.get("replacement",""), ei["start"]))
                    st.markdown("---")
            else:
                st.success("No issues detected by LanguageTool or extra detectors.")

            # Show corrected preview (bulk)
            try:
                corrected = tool.correct(cur_text)
            except Exception:
                corrected = cur_text
            st.markdown("### ✅ Corrected Text (bulk preview)")
            st.text_area("Corrected version", value=corrected, height=250, key="corrected_preview")

            # Download corrected
            st.download_button("Download corrected text", data=corrected, file_name="corrected_text.txt")

            # update progress file safely
            fpath = Path("user_progress.json")
            data = {}
            if fpath.exists():
                try:
                    with fpath.open("r", encoding="utf-8") as fh:
                        data = json.load(fh)
                except Exception:
                    data = {}
            email_key = st.session_state.get("user_email")
            if email_key:
                if email_key not in data:
                    data[email_key] = {"grammar_fixes": 0}
                data[email_key]["grammar_fixes"] = data[email_key].get("grammar_fixes", 0) + len(matches)
                try:
                    with fpath.open("w", encoding="utf-8") as fh:
                        json.dump(data, fh, indent=2)
                except Exception:
                    st.warning("Could not write to progress file.")

