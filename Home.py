"""
Multi-Domain Intelligence Platform - Home Page
Role-Based Login and Registration Interface
"""

import streamlit as st
from app.services.database_manager import DatabaseManager
from app.services.auth_manager import AuthManager
from app.data.schema import create_all_tables

# Page configuration
st.set_page_config(
    page_title="Login | Intelligence Platform",
    page_icon="🔐",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# Initialise database on first run
@st.cache_resource
def init_database():
    """Initialise the database and create tables if they don't exist."""
    try:
        db_path = st.secrets.get("DB_PATH", "DATA/intelligence_platform.db")
    except:
        db_path = "DATA/intelligence_platform.db"
    
    db = DatabaseManager(db_path)
    db.connect()
    create_all_tables(db.get_connection())
    return db

# Get database and auth manager
db = init_database()
auth = AuthManager(db)

# Initialise session state
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "username" not in st.session_state:
    st.session_state.username = ""
if "user_role" not in st.session_state:
    st.session_state.user_role = ""
if "user_object" not in st.session_state:
    st.session_state.user_object = None

# Header
st.title("🔐 Multi-Domain Intelligence Platform")
st.markdown("### Secure Access Portal")
st.caption("Role-based access to specialized intelligence domains")
st.divider()

# If already logged in, show access information
if st.session_state.logged_in:
    user = st.session_state.user_object
    
    st.success(f"✅ Logged in as **{st.session_state.username}**")
    st.info(f"**Role:** {user.get_role_display_name()}")
    
    # Show accessible domains
    st.markdown("### 📂 Your Accessible Domains:")
    
    allowed_domains = user.get_allowed_domains()
    
    domain_info = {
        'cybersecurity': ('🛡️', 'Cybersecurity Operations', 'Manage security incidents and threats'),
        'datascience': ('📊', 'Data Science Analytics', 'Analyse datasets and generate insights'),
        'itoperations': ('💻', 'IT Operations Management', 'Handle support tickets and infrastructure'),
        'ai_assistant': ('🤖', 'AI Assistant', 'Get AI-powered help for your domain')
    }
    
    cols = st.columns(2)
    col_idx = 0
    
    for domain in allowed_domains:
        if domain == 'admin_panel':
            continue  # Skip admin panel in this view
            
        if domain in domain_info:
            icon, title, desc = domain_info[domain]
            
            with cols[col_idx % 2]:
                st.markdown(f"""
                <div style="padding: 20px; border: 2px solid #0EA5E9; border-radius: 10px; margin-bottom: 10px;">
                    <h3>{icon} {title}</h3>
                    <p style="color: #666;">{desc}</p>
                </div>
                """, unsafe_allow_html=True)
            
            col_idx += 1
    
    st.divider()
    
    # Navigation buttons
    button_col1, button_col2, button_col3 = st.columns(3)
    
    with button_col1:
        if st.button("🏠 Go to Dashboard", use_container_width=True, type="primary"):
            st.switch_page(user.get_home_page())
    
    with button_col2:
        if user.can_access_domain('ai_assistant'):
            if st.button("🤖 AI Assistant", use_container_width=True):
                st.switch_page("pages/4_🤖_AI_Assistant.py")
    
    with button_col3:
        if st.button("🚪 Logout", use_container_width=True, type="secondary"):
            st.session_state.logged_in = False
            st.session_state.username = ""
            st.session_state.user_role = ""
            st.session_state.user_object = None
            st.rerun()
    
    st.stop()

# Login / Register tabs
tab_login, tab_register = st.tabs(["🔑 Login", "📝 Register"])

# ========== LOGIN TAB ==========
with tab_login:
    st.subheader("Login to Your Account")
    
    with st.form("login_form"):
        login_username = st.text_input(
            "Username",
            placeholder="Enter your username",
            key="login_username"
        )
        login_password = st.text_input(
            "Password",
            type="password",
            placeholder="Enter your password",
            key="login_password"
        )
        
        submitted = st.form_submit_button("🔓 Login", use_container_width=True, type="primary")
        
        if submitted:
            if not login_username or not login_password:
                st.error("⚠️ Please fill in all fields")
            else:
                # Authenticate user
                success, user, message = auth.login_user(login_username, login_password)
                
                if success:
                    # Store user info in session state
                    st.session_state.logged_in = True
                    st.session_state.username = user.get_username()
                    st.session_state.user_role = user.get_role()
                    st.session_state.user_object = user
                    
                    st.success(f"✅ {message}")
                    
                    # Redirect to user's home page based on role
                    st.info(f"Redirecting to {user.get_role_display_name()} dashboard...")
                    st.switch_page(user.get_home_page())
                else:
                    st.error(f"❌ {message}")
    
    # Demo accounts information
    with st.expander("🎯 Demo Accounts (for testing)"):
        st.markdown("""
        **Role-Based Demo Accounts:**
        
        🛡️ **Cybersecurity Analyst**
        - Username: `cyber_analyst`
        - Password: `CyberPass123!`
        - Access: Cybersecurity + AI Assistant only
        
        📊 **Data Scientist**
        - Username: `data_scientist`
        - Password: `DataPass123!`
        - Access: Data Science + AI Assistant only
        
        💻 **IT Operations Engineer**
        - Username: `it_engineer`
        - Password: `ITPass123!`
        - Access: IT Operations + AI Assistant only
        
        👑 **System Administrator**
        - Username: `admin`
        - Password: `AdminPass123!`
        - Access: All domains + Admin panel
        """)

# ========== REGISTER TAB ==========
with tab_register:
    st.subheader("Create New Account")
    
    with st.form("register_form"):
        new_username = st.text_input(
            "Choose Username",
            placeholder="Enter a unique username",
            key="register_username",
            help="Username must be unique"
        )
        new_password = st.text_input(
            "Choose Password",
            type="password",
            placeholder="Minimum 8 characters",
            key="register_password",
            help="Password must be at least 8 characters long"
        )
        confirm_password = st.text_input(
            "Confirm Password",
            type="password",
            placeholder="Re-enter your password",
            key="register_confirm"
        )
        
        # Role selection with descriptions
        st.markdown("**Select Your Domain:**")
        user_role = st.selectbox(
            "Domain Role",
            options=["cybersecurity", "datascience", "itoperations"],
            format_func=lambda x: {
                'cybersecurity': '🛡️ Cybersecurity Analyst',
                'datascience': '📊 Data Scientist',
                'itoperations': '💻 IT Operations Engineer'
            }[x],
            help="Choose the domain you'll work in"
        )
        
        # Show role description
        role_descriptions = {
            'cybersecurity': 'Access security incident management and threat analysis',
            'datascience': 'Access dataset analytics and data science tools',
            'itoperations': 'Access IT ticketing system and infrastructure management'
        }
        st.caption(role_descriptions[user_role])
        
        submitted = st.form_submit_button("📝 Create Account", use_container_width=True, type="primary")
        
        if submitted:
            # Validation
            if not new_username or not new_password or not confirm_password:
                st.error("⚠️ Please fill in all fields")
            elif len(new_password) < 8:
                st.error("⚠️ Password must be at least 8 characters long")
            elif new_password != confirm_password:
                st.error("⚠️ Passwords do not match")
            else:
                # Register user
                success, message = auth.register_user(new_username, new_password, user_role)
                
                if success:
                    st.success(f"✅ {message}")
                    st.info("👈 You can now login using the **Login** tab")
                else:
                    st.error(f"❌ {message}")

# Footer
st.divider()
st.caption("🔒 Secure authentication powered by bcrypt | Role-based access control enabled")
st.caption("CST1510 Multi-Domain Intelligence Platform | Middlesex University")