"""Home Page - Professional Login"""

import streamlit as st
import time
from datetime import datetime
from app.services.database_manager import DatabaseManager
from app.services.auth_manager import AuthManager
from app.data.schema import create_all_tables

st.set_page_config(
    page_title="Login | Intelligence Platform",
    page_icon="🔐",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# custom styling
st.markdown("""
<style>
    [data-testid="stSidebar"] {display: none;}
    
    .main-header {
        text-align: center;
        padding: 20px 0;
        background: linear-gradient(135deg, #1e3a5f 0%, #0f172a 100%);
        border-radius: 16px;
        margin-bottom: 30px;
        box-shadow: 0 4px 20px rgba(0,0,0,0.15);
    }
    
    .main-header h1 {
        color: #ffffff;
        font-size: 2.2rem;
        margin-bottom: 5px;
        font-weight: 700;
    }
    
    .main-header p {
        color: #94a3b8;
        font-size: 1rem;
        margin: 0;
    }
    
    .login-card {
        background: #ffffff;
        border-radius: 12px;
        padding: 30px;
        box-shadow: 0 2px 12px rgba(0,0,0,0.08);
        border: 1px solid #e2e8f0;
    }
    
    .stats-row {
        display: flex;
        justify-content: space-around;
        padding: 15px 0;
        margin-top: 20px;
        border-top: 1px solid #e2e8f0;
    }
    
    .stat-item {
        text-align: center;
    }
    
    .stat-value {
        font-size: 1.5rem;
        font-weight: 700;
        color: #1e40af;
    }
    
    .stat-label {
        font-size: 0.75rem;
        color: #64748b;
        text-transform: uppercase;
    }
    
    .feature-badge {
        display: inline-block;
        background: #dbeafe;
        color: #1e40af;
        padding: 4px 12px;
        border-radius: 20px;
        font-size: 0.8rem;
        margin: 3px;
    }
    
    .security-notice {
        background: #f0fdf4;
        border-left: 4px solid #22c55e;
        padding: 12px 16px;
        border-radius: 0 8px 8px 0;
        margin-top: 20px;
    }
    
    .security-notice p {
        margin: 0;
        color: #166534;
        font-size: 0.85rem;
    }
    
    .footer-text {
        text-align: center;
        color: #94a3b8;
        font-size: 0.8rem;
        margin-top: 30px;
        padding-top: 20px;
        border-top: 1px solid #e2e8f0;
    }
    
    .stProgress .st-bo {background-color: #3b82f6;}
</style>
""", unsafe_allow_html=True)

# init database
@st.cache_resource
def init_db():
    try:
        db_path = st.secrets.get("DB_PATH", "DATA/intelligence_platform.db")
    except:
        db_path = "DATA/intelligence_platform.db"
    db = DatabaseManager(db_path)
    db.connect()
    create_all_tables(db.get_connection())
    return db

db = init_db()
auth = AuthManager(db)

# get platform stats for display
@st.cache_data(ttl=300)
def get_platform_stats():
    try:
        incidents = db.fetch_all("SELECT COUNT(*) FROM cyber_incidents")[0][0] or 0
        datasets = db.fetch_all("SELECT COUNT(*) FROM datasets_metadata")[0][0] or 0
        tickets = db.fetch_all("SELECT COUNT(*) FROM it_tickets")[0][0] or 0
        users = db.fetch_all("SELECT COUNT(*) FROM users")[0][0] or 0
        return {"incidents": incidents, "datasets": datasets, "tickets": tickets, "users": users}
    except:
        return {"incidents": 0, "datasets": 0, "tickets": 0, "users": 0}

# session state
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "username" not in st.session_state:
    st.session_state.username = ""
if "user_role" not in st.session_state:
    st.session_state.user_role = ""
if "user_object" not in st.session_state:
    st.session_state.user_object = None

# if logged in, show dashboard redirect
if st.session_state.logged_in:
    user = st.session_state.user_object
    
    st.markdown(f"""
    <div class="main-header">
        <h1>👋 Welcome back, {st.session_state.username}!</h1>
        <p>{user.get_role_display_name()}</p>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button("🚀 Continue to Dashboard", use_container_width=True, type="primary"):
            st.switch_page(user.get_home_page())
        
        st.write("")
        
        if st.button("🚪 Sign Out", use_container_width=True):
            st.session_state.logged_in = False
            st.session_state.username = ""
            st.session_state.user_role = ""
            st.session_state.user_object = None
            st.rerun()
    st.stop()

# main header
st.markdown("""
<div class="main-header">
    <h1>🛡️ Intelligence Platform</h1>
    <p>Multi-Domain Security & Analytics System</p>
</div>
""", unsafe_allow_html=True)

# platform stats
stats = get_platform_stats()

#login/register tabs
tab_login, tab_register = st.tabs(["🔑 Sign In", "📝 Create Account"])

with tab_login:
    st.markdown("#### Welcome back")
    st.caption("Enter your credentials to access the platform")
    
    with st.form("login_form", clear_on_submit=False):
        username = st.text_input("Username", placeholder="Enter your username")
        password = st.text_input("Password", type="password", placeholder="Enter your password")
        
        col1, col2 = st.columns([1, 1])
        with col1:
            remember = st.checkbox("Remember me", value=True)
        with col2:
            st.caption("")  # spacing
        
        submit = st.form_submit_button("Sign In", use_container_width=True, type="primary")
        
        if submit:
            if not username or not password:
                st.error("Please enter both username and password")
            else:
                success, user, message = auth.login_user(username, password)
                
                if success:
                    # show loading
                    progress = st.progress(0, text="Authenticating...")
                    for i in range(100):
                        time.sleep(0.006)
                        if i < 30:
                            progress.progress(i + 1, text="Verifying credentials...")
                        elif i < 60:
                            progress.progress(i + 1, text="Loading user profile...")
                        elif i < 90:
                            progress.progress(i + 1, text="Preparing dashboard...")
                        else:
                            progress.progress(i + 1, text="Almost ready...")
                    
                    # save session
                    st.session_state.logged_in = True
                    st.session_state.username = user.get_username()
                    st.session_state.user_role = user.get_role()
                    st.session_state.user_object = user
                    
                    st.success(f"✅ Welcome, {user.get_username()}!")
                    time.sleep(0.5)
                    st.switch_page(user.get_home_page())
                else:
                    st.error(f"❌ {message}")
    
    # the demo accounts section
    with st.expander("🎯 Demo Accounts", expanded=False):
        st.markdown("""
        | Role | Username | Password |
        |:-----|:---------|:---------|
        | 🛡️ Cybersecurity | `cyber_analyst` | `CyberPass123!` |
        | 📊 Data Science | `data_scientist` | `DataPass123!` |
        | 💻 IT Operations | `it_engineer` | `ITPass123!` |
        | 👑 Administrator | `admin` | `AdminPass123!` |
        """)

with tab_register:
    st.markdown("#### Create your account")
    st.caption("Join the platform to access domain-specific tools")
    
    with st.form("register_form", clear_on_submit=True):
        new_user = st.text_input("Username", placeholder="Choose a username", key="reg_user")
        
        col1, col2 = st.columns(2)
        with col1:
            new_pass = st.text_input("Password", type="password", placeholder="Min 8 characters", key="reg_pass")
        with col2:
            confirm = st.text_input("Confirm", type="password", placeholder="Re-enter password", key="reg_confirm")
        
        role = st.selectbox("Select your role", ["cybersecurity", "datascience", "itoperations"],
            format_func=lambda x: {
                "cybersecurity": "🛡️ Cybersecurity Analyst", 
                "datascience": "📊 Data Scientist",
                "itoperations": "💻 IT Operations Engineer"
            }[x])
        
        # role description
        role_desc = {
            "cybersecurity": "Access security incidents, threat analysis, and AI-powered incident response.",
            "datascience": "Manage datasets, analytics tools, and ML recommendations.",
            "itoperations": "Handle IT tickets, troubleshooting, and infrastructure support."
        }
        st.caption(f"ℹ️ {role_desc[role]}")
        
        agree = st.checkbox("I agree to the terms of service and privacy policy")
        
        submit = st.form_submit_button("Create Account", use_container_width=True, type="primary")
        
        if submit:
            if not new_user or not new_pass or not confirm:
                st.error("Please fill in all fields")
            elif len(new_pass) < 8:
                st.error("Password must be at least 8 characters")
            elif new_pass != confirm:
                st.error("Passwords do not match")
            elif not agree:
                st.error("Please accept the terms to continue")
            else:
                success, message = auth.register_user(new_user, new_pass, role)
                if success:
                    st.success(f"✅ {message}")
                    st.info("You can now sign in with your credentials")
                else:
                    st.error(f"❌ {message}")

# platform features
st.markdown("---")
st.markdown("#### Platform Features")

col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("""
    **🛡️ Cybersecurity**
    
    Incident tracking, threat analysis, and AI-powered security insights.
    """)

with col2:
    st.markdown("""
    **📊 Data Science**
    
    Dataset management, analytics, and ML recommendations.
    """)

with col3:
    st.markdown("""
    **💻 IT Operations**
    
    Ticket management, troubleshooting, and workload analytics.
    """)

# stats row
st.markdown("---")
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric("Security Incidents", stats["incidents"])
with col2:
    st.metric("Datasets", stats["datasets"])
with col3:
    st.metric("IT Tickets", stats["tickets"])
with col4:
    st.metric("Active Users", stats["users"])

# security notice
st.markdown("""
<div class="security-notice">
    <p>🔒 <strong>Secure Connection</strong> — Your data is protected with bcrypt encryption and role-based access control.</p>
</div>
""", unsafe_allow_html=True)

# footer
st.markdown(f"""
<div class="footer-text">
    <p>Multi-Domain Intelligence Platform • CST1510 • {datetime.now().strftime('%Y')}</p>
    <p style="font-size: 0.7rem; margin-top: 5px;">Version 2.0 • Last updated: {datetime.now().strftime('%B %d, %Y')}</p>
</div>
""", unsafe_allow_html=True)