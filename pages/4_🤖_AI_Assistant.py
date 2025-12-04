"""AI Assistant Dashboard"""

import streamlit as st
from app.services.ai_assistant import GeminiClient
from app.services.database_manager import DatabaseManager

# Page configuration
st.set_page_config(page_title="AI Assistant | Intelligence Platform", page_icon="🤖", layout="wide")

#Authentication & Authorisation
if not st.session_state.get("logged_in", False):
    st.error("🔒 Access Denied")
    st.warning("You must be logged in to view this page.")
    if st.button("Go to Login"):
        st.switch_page("Home.py")
    st.stop()

user = st.session_state.get("user_object")
if user and not user.can_access_domain('ai_assistant'):
    st.error("🚫 Access Denied")
    st.warning(f"Your role ({user.get_role_display_name()}) does not have permission to access the AI Assistant.")
    if st.button("Return to Home"):
        st.switch_page("Home.py")
    st.stop()

#Service Initialisation
@st.cache_resource
def get_services():
    """Load database and AI client with secrets"""
    try:
        db_path = st.secrets.get("DB_PATH", "DATA/intelligence_platform.db")
        ai_key = st.secrets.get("GEMINI_API_KEY", "")
    except:
        db_path = "DATA/intelligence_platform.db"
        ai_key = ""
    db = DatabaseManager(db_path)
    db.connect()
    client = GeminiClient(api_key=ai_key) if ai_key else None
    return db, client

db, client = get_services()

# Check if AI is configured
if not client:
    st.error("❌ AI not configured")
    st.warning("Add GEMINI_API_KEY to .streamlit/secrets.toml")
    st.stop()

# --- Header --
col1, col2 = st.columns([3, 1])
with col1:
    st.title("🤖 AI Assistant")
    st.caption("Cross-domain analysis & insights")
with col2:
    st.markdown(f"**{st.session_state.username}**", unsafe_allow_html=True)

st.divider()

#Sidebar Controls
with st.sidebar:
    st.header("⚙️ Settings")
    
    # Domain selection based on user permissions
    domains = ["General"]
    prompts = {"General": "You're a helpful assistant."}
    
    if user.can_access_domain('cybersecurity'):
        domains.append("Cybersecurity")
        prompts["Cybersecurity"] = "You're a cybersecurity analyst."
    if user.can_access_domain('datascience'):
        domains.append("Data Science")
        prompts["Data Science"] = "You're a data scientist."
    if user.can_access_domain('itoperations'):
        domains.append("IT Operations")
        prompts["IT Operations"] = "You're an IT specialist."
    
    domain = st.selectbox("Domain", domains)
    temp = st.slider("Creativity", 0.0, 2.0, 1.0, 0.1)
    
    st.divider()
    st.subheader("⚡ Quick Actions")
    
    # Quick analysis buttons based on user permissions
    analyse_all = st.button("📊 Platform Analysis", use_container_width=True, type="primary")
    
    if user.can_access_domain('cybersecurity'):
        cyber_btn = st.button("🛡️ Cyber Summary", use_container_width=True)
    else:
        cyber_btn = False
    if user.can_access_domain('datascience'):
        data_btn = st.button("📈 Data Summary", use_container_width=True)
    else:
        data_btn = False
    if user.can_access_domain('itoperations'):
        it_btn = st.button("💻 IT Summary", use_container_width=True)
    else:
        it_btn = False
    
    st.divider()
    msg_count = len(st.session_state.get("messages", []))
    st.metric("Messages", msg_count)
    
    if st.button("🗑️ Clear Chat", use_container_width=True):
        st.session_state.messages = []
        st.rerun()

#Platform Statistics 
def get_stats():
    """Fetch statistics from all domain tables"""
    stats = {}
    try:
        cyber = db.fetch_all("SELECT COUNT(*), SUM(CASE WHEN status IN ('Open','Investigating') THEN 1 ELSE 0 END), SUM(CASE WHEN severity='Critical' THEN 1 ELSE 0 END) FROM cyber_incidents")
        stats['cyber'] = {'total': cyber[0][0] or 0, 'active': cyber[0][1] or 0, 'critical': cyber[0][2] or 0}
    except:
        stats['cyber'] = {'total': 0, 'active': 0, 'critical': 0}
    
    try:
        data = db.fetch_all("SELECT COUNT(*), SUM(record_count), SUM(file_size_mb) FROM datasets_metadata")
        stats['data'] = {'total': data[0][0] or 0, 'records': data[0][1] or 0, 'size_mb': data[0][2] or 0}
    except:
        stats['data'] = {'total': 0, 'records': 0, 'size_mb': 0}
    
    try:
        it = db.fetch_all("SELECT COUNT(*), SUM(CASE WHEN status IN ('Open','In Progress') THEN 1 ELSE 0 END), SUM(CASE WHEN priority='Critical' THEN 1 ELSE 0 END) FROM it_tickets")
        stats['it'] = {'total': it[0][0] or 0, 'active': it[0][1] or 0, 'critical': it[0][2] or 0}
    except:
        stats['it'] = {'total': 0, 'active': 0, 'critical': 0}
    
    return stats

#Initialise Chat History
if "messages" not in st.session_state:
    st.session_state.messages = []

#Handle Quick Action Prompts
action_prompt = None

if analyse_all:
    stats = get_stats()
    action_prompt = f"""Platform Overview:
🛡️ Cyber: {stats['cyber']['total']} incidents, {stats['cyber']['active']} active, {stats['cyber']['critical']} critical
📊 Data: {stats['data']['total']} datasets, {stats['data']['records']:,} records, {stats['data']['size_mb']:.1f} MB
💻 IT: {stats['it']['total']} tickets, {stats['it']['active']} active, {stats['it']['critical']} critical

Provide insights and recommendations."""

if cyber_btn:
    stats = get_stats()
    action_prompt = f"Analyse cybersecurity status: {stats['cyber']}"

if data_btn:
    stats = get_stats()
    action_prompt = f"Analyse data infrastructure: {stats['data']}"

if it_btn:
    stats = get_stats()
    action_prompt = f"Analyse IT operations: {stats['it']}"

#Display Chat History
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

#Process Quick Action Prompts
if action_prompt:
    st.session_state.messages.append({"role": "user", "content": action_prompt})
    with st.chat_message("user"):
        st.markdown(action_prompt)
    
    messages = [{"role": "system", "content": prompts[domain]}, {"role": "user", "content": action_prompt}]
    with st.chat_message("assistant"):
        container = st.empty()
        full = ""
        for chunk in client.chat.completions.create(model="gemini-2.0-flash", messages=messages, stream=True):
            if chunk.choices[0].delta.content:
                full += chunk.choices[0].delta.content
                container.markdown(full + "▌")
        container.markdown(full)
    st.session_state.messages.append({"role": "assistant", "content": full})

#Chat Input
prompt = st.chat_input("Ask anything...")

if prompt:
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)
    
    # Check if user is asking about platform stats
    if any(kw in prompt.lower() for kw in ['dashboard', 'platform', 'summary', 'overview', 'stats']):
        stats = get_stats()
        context = f"Platform: Cyber={stats['cyber']}, Data={stats['data']}, IT={stats['it']}\nQuestion: {prompt}"
        messages = [{"role": "system", "content": prompts[domain]}, {"role": "user", "content": context}]
    else:
        messages = [{"role": "system", "content": prompts[domain]}, {"role": "user", "content": prompt}]
    
    # Generate AI response
    with st.chat_message("assistant"):
        container = st.empty()
        full = ""
        for chunk in client.chat.completions.create(model="gemini-2.0-flash", messages=messages, stream=True):
            if chunk.choices[0].delta.content:
                full += chunk.choices[0].delta.content
                container.markdown(full + "▌")
        container.markdown(full)
    st.session_state.messages.append({"role": "assistant", "content": full})

#Welcome Message
if not st.session_state.messages:
    st.markdown("""
    ### 👋 Hi! I'm your AI Assistant
    
    I can help with:
    - 🛡️ **Cybersecurity** - Threat analysis, incident response
    - 📊 **Data Science** - Dataset insights, ML recommendations  
    - 💻 **IT Operations** - Troubleshooting, workload analysis
    - 📈 **Platform Analytics** - Cross-domain insights
    
    Try the **Quick Actions** in the sidebar or just ask me anything!
    """)

# --- Footer ---
st.divider()
st.caption(f"🤖 AI Assistant | {st.session_state.username} | Domain: {domain}")