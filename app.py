import streamlit as st
import json, os, bcrypt

# ====================================================
# 🌐 PAGE CONFIGURATION
# ====================================================
st.set_page_config(
    page_title="AI Resume Builder | Login",
    page_icon="🧠",
    layout="centered",
)

USERS_FILE = "users.json"


# ====================================================
# 🧰 HELPER FUNCTIONS
# ====================================================
def load_users():
    """Load users from local JSON file."""
    if not os.path.exists(USERS_FILE):
        with open(USERS_FILE, "w") as f:
            json.dump({}, f)
    with open(USERS_FILE, "r") as f:
        try:
            return json.load(f)
        except json.JSONDecodeError:
            return {}


def save_users(users):
    """Save updated user data."""
    with open(USERS_FILE, "w") as f:
        json.dump(users, f, indent=2)


# ====================================================
# 🧠 INITIALIZE SESSION
# ====================================================
users = load_users()
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "user_name" not in st.session_state:
    st.session_state.user_name = ""
if "user_email" not in st.session_state:
    st.session_state.user_email = ""

if not st.session_state.logged_in:
    st.markdown("""
        <style>
            [data-testid="stSidebar"] {
                display: none;
            }
        </style>
    """, unsafe_allow_html=True)

# ====================================================
# 💅 CUSTOM CSS STYLING
# ====================================================
st.markdown("""
<style>
body {
  background: linear-gradient(135deg, #0A0F1E, #0E2433 50%, #08121C);
  color: #E8EEF5;
  font-family: "Inter", sans-serif;
}
h1 {
  text-align: center;
  background: linear-gradient(90deg, #00FFFF, #FF63E0);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  font-weight: 800;
  margin-bottom: 10px;
}
.subtitle {
  text-align: center;
  color: #a4bdd1;
  margin-bottom: 25px;
  font-size: 1.05rem;
}
.container {
  background: rgba(255,255,255,0.06);
  border: 1px solid rgba(255,255,255,0.15);
  border-radius: 16px;
  padding: 35px 40px;
  box-shadow: 0 10px 40px rgba(0,255,255,0.08);
  backdrop-filter: blur(10px);
  max-width: 400px;
  margin: 0 auto;
}
.stTextInput > div > div > input, .stPasswordInput > div > div > input {
  background: rgba(255,255,255,0.05)!important;
  color: #E6EEF6!important;
  border-radius: 10px!important;
}
.stButton > button {
  background: linear-gradient(90deg, #00FFFF, #FF63E0)!important;
  color: #0a0a0a!important;
  font-weight: 700!important;
  border-radius: 12px!important;
  padding: 8px 18px!important;
  border: none!important;
  transition: all 0.3s ease!important;
}
.stButton > button:hover {
  transform: scale(1.05);
  box-shadow: 0 0 15px rgba(255,99,224,0.4);
}
.footer {
  text-align: center;
  color: #8faabb;
  margin-top: 15px;
  font-size: 0.9rem;
}
</style>
""", unsafe_allow_html=True)


# ====================================================
# 🔐 LOGIN PAGE
# ====================================================
def login_page():
    st.markdown("<h1>🧠 AI Resume Builder</h1>", unsafe_allow_html=True)
    st.markdown("<p class='subtitle'>Your free AI-powered career companion 🚀</p>", unsafe_allow_html=True)

    tab1, tab2 = st.tabs(["🔐 Login", "📝 Register"])

    # ---------------- LOGIN TAB ----------------
    with tab1:
        with st.form("login_form"):
            email = st.text_input("📧 Email")
            password = st.text_input("🔑 Password", type="password")
            submitted = st.form_submit_button("🚀 Login")

            if submitted:
                if not email or not password:
                    st.warning("⚠️ Please fill in all fields.")
                elif email in users:
                    stored_hash = users[email]["password"].encode("utf-8")
                    if bcrypt.checkpw(password.encode("utf-8"), stored_hash):
                        st.session_state.logged_in = True
                        st.session_state.user_email = email
                        st.session_state.user_name = users[email]["name"]
                        st.success(f"✅ Welcome back, {users[email]['name']}!")
                        st.switch_page("pages/1_Student_Dashboard.py")
                    else:
                        st.error("❌ Incorrect password.")
                else:
                    st.error("⚠️ No account found with that email.")

    # ---------------- REGISTER TAB ----------------
    with tab2:
        with st.form("register_form"):
            name = st.text_input("👤 Full Name")
            email = st.text_input("✉️ Email")
            password = st.text_input("🔒 Create Password", type="password")
            confirm = st.text_input("🔑 Confirm Password", type="password")
            create = st.form_submit_button("✨ Register")

            if create:
                if not name or not email or not password:
                    st.warning("Please fill all fields.")
                elif password != confirm:
                    st.warning("Passwords do not match.")
                elif email in users:
                    st.warning("⚠️ Email already registered.")
                else:
                    hashed_pw = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt())
                    users[email] = {"name": name, "password": hashed_pw.decode("utf-8")}
                    save_users(users)
                    st.success(f"🎉 Account created successfully! Welcome, {name}. Please login.")

    st.markdown("<div class='footer'>Made with ❤️ for students — 100% Free</div>", unsafe_allow_html=True)


# ====================================================
# 🚪 MAIN CONTROLLER
# ====================================================
if not st.session_state.logged_in:
    login_page()
else:
    st.switch_page("1_Student_Dashboard.py")
