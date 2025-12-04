"""
AI Assistant Chat Interface - Enhanced Edition
Domain-specific AI assistance for authorized users
"""

import streamlit as st
from app.services.ai_assistant import AIAssistant

# Page configuration
st.set_page_config(
    page_title="AI Assistant | Intelligence Platform",
    page_icon="🤖",
    layout="wide"
)

# Authentication check
if not st.session_state.get("logged_in", False):
    st.error("🔒 Please login to access this page")
    if st.button("Go to Login"):
        st.switch_page("Home.py")
    st.stop()

# Check if user has permission to access AI Assistant
user = st.session_state.get("user_object")
if user and not user.can_access_domain('ai_assistant'):
    st.error(f"🚫 Access Denied: Your role ({user.get_role_display_name()}) does not have permission to access the AI Assistant.")
    st.info("Please contact your administrator if you need access to this feature.")
    if st.button("Return to Home"):
        st.switch_page("Home.py")
    st.stop()

# Initialise AI assistant
@st.cache_resource
def get_ai_assistant():
    """Initialise the AI assistant."""
    try:
        ai_key = st.secrets.get("GEMINI_API_KEY", "")
    except:
        ai_key = ""
    
    if not ai_key:
        return None
    return AIAssistant(ai_key)

ai = get_ai_assistant()

if not ai:
    st.error("❌ AI Assistant is not configured. Please add your Google Gemini API key to `.streamlit/secrets.toml`")
    st.code("""
# Add this to .streamlit/secrets.toml:
GEMINI_API_KEY = "your-gemini-api-key-here"

# Get your free API key from:
# https://makersuite.google.com/app/apikey
    """)
    if st.button("Return to Home"):
        st.switch_page("Home.py")
    st.stop()

# Header with user info
col_title, col_user = st.columns([3, 1])

with col_title:
    st.title("🤖 AI Assistant")
    st.caption("Your intelligent companion for domain-specific guidance")

with col_user:
    st.markdown(f"""
    <div style="text-align: right; padding: 10px;">
        <strong>{st.session_state.username}</strong><br>
        <small>{user.get_role_display_name()}</small>
    </div>
    """, unsafe_allow_html=True)

st.divider()

# Sidebar configuration
with st.sidebar:
    st.header("🔧 AI Configuration")
    
    # Domain selection based on user permissions
    st.subheader("🎯 Domain Context")
    
    # Get available domains for user
    available_domains = []
    domain_mapping = {}
    
    if user.can_access_domain('cybersecurity'):
        available_domains.append("Cybersecurity")
        domain_mapping["Cybersecurity"] = "cybersecurity"
    
    if user.can_access_domain('datascience'):
        available_domains.append("Data Science")
        domain_mapping["Data Science"] = "datascience"
    
    if user.can_access_domain('itoperations'):
        available_domains.append("IT Operations")
        domain_mapping["IT Operations"] = "itoperations"
    
    # Always add General option
    available_domains.insert(0, "General")
    domain_mapping["General"] = "general"
    
    # Domain selection
    domain = st.selectbox(
        "Select AI Domain",
        options=available_domains,
        index=0,
        help="Choose the domain expertise for the AI assistant"
    )
    
    if st.button("🔄 Switch Domain", use_container_width=True):
        ai.set_domain(domain_mapping[domain])
        st.success(f"✅ Switched to {domain} mode")
        st.rerun()
    
    st.divider()
    
    # Chat controls
    st.subheader("💬 Chat Controls")
    
    if st.button("🗑️ Clear Conversation", use_container_width=True):
        ai.clear_conversation()
        if "chat_messages" in st.session_state:
            st.session_state.chat_messages = []
        st.success("✅ Conversation cleared")
        st.rerun()
    
    # Display current domain
    st.divider()
    current_domain = ai.get_current_domain()
    domain_emoji = {
        'general': '🌐',
        'cybersecurity': '🛡️',
        'datascience': '📊',
        'itoperations': '💻'
    }
    st.info(f"{domain_emoji.get(current_domain, '🤖')} **Current Domain:** {current_domain.title()}")
    
    # User's accessible domains
    st.divider()
    st.subheader("🔓 Your Permissions")
    
    for accessible_domain in user.get_allowed_domains():
        if accessible_domain != 'ai_assistant':
            emoji = domain_emoji.get(accessible_domain, '📁')
            st.caption(f"{emoji} {accessible_domain.replace('_', ' ').title()}")
    
    # Quick prompts based on accessible domains
    st.divider()
    st.subheader("💡 Quick Prompts")
    
    quick_prompts = {
        "cybersecurity": [
            "What is a zero-day vulnerability?",
            "How do I respond to a phishing attack?",
            "Explain the MITRE ATT&CK framework",
            "What are common ransomware indicators?"
        ],
        "datascience": [
            "How do I handle missing data?",
            "What's the difference between supervised and unsupervised learning?",
            "Recommend visualisation for time-series data",
            "How do I detect outliers in a dataset?"
        ],
        "itoperations": [
            "How do I troubleshoot network connectivity issues?",
            "What are best practices for backup strategies?",
            "How do I optimise server performance?",
            "Explain the difference between RAID levels"
        ],
        "general": [
            "Help me understand the platform features",
            "What can you help me with?",
            "Explain role-based access control",
            "How do the domains integrate?"
        ]
    }
    
    current_domain_key = domain_mapping[domain]
    for i, prompt in enumerate(quick_prompts.get(current_domain_key, [])):
        if st.button(f"💬 {prompt}", use_container_width=True, key=f"quick_{current_domain_key}_{i}"):
            if "chat_messages" not in st.session_state:
                st.session_state.chat_messages = []
            st.session_state.chat_messages.append({"role": "user", "content": prompt})
            st.rerun()

# Initialise chat messages in session state
if "chat_messages" not in st.session_state:
    st.session_state.chat_messages = []

# Welcome message
if len(st.session_state.chat_messages) == 0:
    st.markdown("""
    ### 👋 Hello! I'm your AI Assistant
    
    I can help you with the domains you have access to:
    """)
    
    # Show user's accessible domains with descriptions
    for accessible_domain in user.get_allowed_domains():
        if accessible_domain == 'cybersecurity':
            st.markdown("""
            🛡️ **Cybersecurity**
            - Analyse security incidents and threats
            - Provide mitigation recommendations
            - Explain attack vectors and vulnerabilities
            """)
        elif accessible_domain == 'datascience':
            st.markdown("""
            📊 **Data Science**
            - Analyse datasets and suggest techniques
            - Recommend visualisation strategies
            - Explain statistical methods
            """)
        elif accessible_domain == 'itoperations':
            st.markdown("""
            💻 **IT Operations**
            - Troubleshoot technical issues
            - Provide step-by-step solutions
            - Recommend best practices
            """)
    
    st.markdown("""
    **How to use:**
    1. Select a domain from the sidebar (or use General for cross-domain questions)
    2. Type your question in the chat box below
    3. I'll provide expert guidance with actionable recommendations
    
    💡 **Tip:** Use the Quick Prompts in the sidebar for common questions!
    """)
    st.divider()

# Display chat history
for message in st.session_state.chat_messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Chat input
prompt = st.chat_input("Ask me anything about your accessible domains...")

if prompt:
    # Add user message to session state
    st.session_state.chat_messages.append({"role": "user", "content": prompt})
    
    # Display user message
    with st.chat_message("user"):
        st.markdown(prompt)
    
    # Get AI response with streaming
    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        full_response = ""
        
        # Set domain before sending message
        ai.set_domain(domain_mapping[domain])
        
        # Stream the response
        with st.spinner("🤖 Thinking..."):
            stream = ai.send_message(prompt, stream=True)
            
            # Process streaming chunks
            for chunk in stream:
                if chunk.choices[0].delta.content:
                    full_response += chunk.choices[0].delta.content
                    message_placeholder.markdown(full_response + "▌")
            
            # Display final response
            message_placeholder.markdown(full_response)
        
        # Add assistant response to session state
        st.session_state.chat_messages.append({"role": "assistant", "content": full_response})
        
        # Update AI's internal history
        ai._conversation_history.append({"role": "user", "content": prompt})
        ai._conversation_history.append({"role": "assistant", "content": full_response})

# Display conversation statistics
if st.session_state.chat_messages:
    st.divider()
    message_count = len(st.session_state.chat_messages)
    user_messages = len([m for m in st.session_state.chat_messages if m["role"] == "user"])
    st.caption(f"💬 Conversation: {user_messages} questions | {message_count} total messages | Domain: {ai.get_current_domain().title()}")

# Footer
st.divider()
st.caption("🤖 AI Assistant powered by Google Gemini | Multi-Domain Intelligence Platform")
st.caption(f"Session: {st.session_state.username} | Role: {user.get_role_display_name()}") 