"""AI Assistant Dashboard"""

import streamlit as st
from app.services.ai_assistant import GeminiClient
from app.services.database_manager import DatabaseManager

# Page configuration
st.set_page_config(page_title="AI Assistant | Intelligence Platform", page_icon="🤖", layout="wide")

# Authentication & Authorisation
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

# Service Initialisation
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

# Header
col1, col2 = st.columns([3, 1])
with col1:
    st.title("🤖 AI Assistant")
    st.caption("Cross-domain analysis & insights")
with col2:
    st.markdown(f"**{st.session_state.username}**", unsafe_allow_html=True)

st.divider()

# Sidebar Controls
with st.sidebar:
    st.header("⚙️ Settings")
    
    # Domain selection based on user permissions
    domains = ["General"]
    prompts = {"General": "You're a helpful assistant."}
    
    domain_config = {
        'cybersecurity': ("Cybersecurity", "You're a cybersecurity analyst. Use the provided dashboard data to answer questions accurately."),
        'datascience': ("Data Science", "You're a data scientist. Use the provided dashboard data to answer questions accurately."),
        'itoperations': ("IT Operations", "You're an IT specialist. Use the provided dashboard data to answer questions accurately.")
    }
    
    for key, (name, prompt) in domain_config.items():
        if user.can_access_domain(key):
            domains.append(name)
            prompts[name] = prompt
    
    domain = st.selectbox("Domain", domains)
    
    st.divider()
    st.subheader("⚡ Quick Actions")
    
    # Quick analysis buttons
    quick_actions = {
        "📊 Platform Analysis": ("General", "Perform a comprehensive analysis of the entire platform. Highlight key risks, operational bottlenecks, and data trends."),
        "🛡️ Cyber Summary": ("Cybersecurity", "Analyze cybersecurity incidents. Summarize critical threats and recent trends."),
        "📈 Data Summary": ("Data Science", "Analyze datasets. Provide insights on storage usage, categories, and recent updates."),
        "💻 IT Summary": ("IT Operations", "Analyze IT tickets. Identify high-priority issues and workload distribution.")
    }
    
    action_clicked = None
    action_domain = None
    action_prompt = None
    
    for btn_text, (btn_domain, btn_prompt) in quick_actions.items():
        if btn_domain == "General" or user.can_access_domain(btn_domain.lower().replace(" ", "")):
            if st.button(btn_text, use_container_width=True, type="primary" if btn_domain == "General" else None):
                action_clicked = btn_text
                action_domain = btn_domain
                action_prompt = btn_prompt
                break
    
    st.divider()
    msg_count = len(st.session_state.get("messages", []))
    st.metric("Messages", msg_count)
    
    if st.button("🗑️ Clear Chat", use_container_width=True):
        st.session_state.messages = []
        st.rerun()

# Initialize Chat History
if "messages" not in st.session_state:
    st.session_state.messages = []

# Helper function for AI responses
def display_ai_response(messages, response_domain):
    """Display AI response with streaming"""
    with st.chat_message("assistant"):
        container = st.empty()
        full = ""
        for chunk in client.chat.completions.create(model="gemini-2.0-flash", messages=messages, stream=True, domain=response_domain):
            if chunk.choices[0].delta.content:
                full += chunk.choices[0].delta.content
                container.markdown(full + "▌")
        container.markdown(full)
    return full

# Handle Quick Action Prompts
if action_clicked:
    st.session_state.messages.append({"role": "user", "content": action_prompt})
    with st.chat_message("user"):
        st.markdown(action_prompt)
    
    messages = [
        {"role": "system", "content": prompts.get(action_domain, prompts.get("General"))},
        {"role": "user", "content": action_prompt}
    ]
    
    full = display_ai_response(messages, action_domain)
    st.session_state.messages.append({"role": "assistant", "content": full})

# Display Chat History
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# Chat Input
prompt = st.chat_input("Ask anything...")

if prompt:
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)
    
    # Smart domain detection
    query_domain = domain
    if domain == "General":
        domain_keywords = {
            ('platform', 'all', 'overall', 'entire'): "General",
            ('cyber', 'security', 'incident', 'threat'): "Cybersecurity",
            ('dataset', 'data science', 'ml', 'machine learning'): "Data Science",
            ('ticket', 'it operations', 'support', 'sla'): "IT Operations"
        }
        for keywords, detected_domain in domain_keywords.items():
            if any(kw in prompt.lower() for kw in keywords):
                query_domain = detected_domain
                break
    
    messages = [
        {"role": "system", "content": prompts.get(query_domain, prompts.get("General"))},
        {"role": "user", "content": prompt}
    ]
    
    full = display_ai_response(messages, query_domain)
    st.session_state.messages.append({"role": "assistant", "content": full})

# Welcome Message
if not st.session_state.messages:
    st.markdown("""
    ### 🤖 Hi! I'm your AI Assistant
    
    I can help with:
    - 🛡️ **Cybersecurity** - Threat analysis, incident response
    - 📊 **Data Science** - Dataset insights, ML recommendations  
    - 💻 **IT Operations** - Troubleshooting, workload analysis
    - 📈 **Platform Analytics** - Cross-domain insights
    
    **Note:** I have direct access to live dashboard data from your CSV files!
    Try the **Quick Actions** in the sidebar or just ask me anything!
    """)

# Footer
st.divider()
st.caption(f"🤖 AI Assistant | {st.session_state.username} | Domain: {domain}")
