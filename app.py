import streamlit as st

from backend.auth import login_user, register_user

# ======================================================
# PAGE CONFIG — CENTERED, NO SIDEBAR
# ======================================================
st.set_page_config(
    page_title="AI Resume Intelligence",
    page_icon="🧠",
    layout="centered"
)
st.markdown("""
<style>
[data-testid="stSidebar"] {
    display: none;
}
</style>
""", unsafe_allow_html=True)

# ======================================================
# USER STORAGE (LOCAL — DB READY)
# ======================================================


# ======================================================
# SESSION INIT
# ======================================================
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

# ======================================================
# IF LOGGED IN → DASHBOARD
# ======================================================
if st.session_state.logged_in:
    st.switch_page("pages/1_Student_Dashboard.py")

# ======================================================
# UI STYLES — CLEAN & PROFESSIONAL
# ======================================================
st.markdown("""
<style>
body {
    background: radial-gradient(circle at top, #0f172a, #020617);
    font-family: Inter, system-ui, sans-serif;
}

.brand {
    text-align: center;
    font-size: 28px;
    font-weight: 800;
    background: linear-gradient(90deg,#38bdf8,#a78bfa);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
}
.subtitle {
    text-align: center;
    color: #cbd5f5;
    margin-bottom: 28px;
}
.stTextInput input, .stPasswordInput input {
    background: rgba(255,255,255,0.05) !important;
    color: white !important;
    border-radius: 10px !important;
}
.stButton button {
    width: 100%;
    border-radius: 12px;
    padding: 10px;
    font-weight: 700;
}
.footer-note {
    text-align: center;
    margin-top: 18px;
    color: #94a3b8;
    font-size: 13px;
}
</style>
""", unsafe_allow_html=True)

# ======================================================
# LOGIN / REGISTER CARD
# ======================================================
st.markdown('<div class="login-card">', unsafe_allow_html=True)

st.markdown('<div class="brand">AI Resume Intelligence</div>', unsafe_allow_html=True)
st.markdown(
    '<div class="subtitle">ATS-ready resumes · Recruiter-aligned feedback · Real impact</div>',
    unsafe_allow_html=True
)

tabs = st.tabs(["Login", "Create account"])

# -------------------- LOGIN --------------------
with tabs[0]:
    with st.form("login_form"):
        email = st.text_input("Email address")
        password = st.text_input("Password", type="password")

        submitted = st.form_submit_button("Continue")

        if submitted:
            success, user = login_user(email, password)

            if success:
                st.session_state.logged_in = True
                st.session_state.user_email = email
                st.session_state.user_name = user["name"]
                st.switch_page("pages/1_Student_Dashboard.py")
            else:
                st.error("Invalid email or password")


# -------------------- REGISTER --------------------
with tabs[1]:
    with st.form("register_form"):
        name = st.text_input("Full name")
        email = st.text_input("Email address")
        password = st.text_input("Create password", type="password")

        submitted = st.form_submit_button("Create account")

        if submitted:
            if not name or not email or not password:
                st.warning("Please fill in all fields")
            else:
                success = register_user(name, email, password)

                if success:
                    st.success("Account created. You can now log in.")
                else:
                    st.error("An account with this email already exists")



st.markdown('</div>', unsafe_allow_html=True)

st.markdown(
    '<div class="footer-note">Not an ATS. An ATS readiness intelligence tool.</div>',
    unsafe_allow_html=True
)
