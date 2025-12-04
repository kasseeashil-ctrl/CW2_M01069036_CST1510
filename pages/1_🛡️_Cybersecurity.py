"""Cybersecurity dashboard - Professional edition with comprehensive analytics"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime

from app.services.database_manager import DatabaseManager
from app.services.ai_assistant import AIAssistant
from app.models.security_incidents import SecurityIncident

# Page configuration
st.set_page_config(
    page_title="Cybersecurity | Intelligence Platform",
    page_icon="🛡️",
    layout="wide"
)

# Authentication check
if not st.session_state.get("logged_in", False):
    st.error("🔒 Please login to access this page")
    if st.button("Go to Login"):
        st.switch_page("Home.py")
    st.stop()

# Permission check
user = st.session_state.get("user_object")
if user and not user.can_access_domain('cybersecurity'):
    st.error(f"🚫 Access Denied: Your role ({user.get_role_display_name()}) cannot access Cybersecurity.")
    if st.button("Return to Home"):
        st.switch_page("Home.py")
    st.stop()

# Initialise services
@st.cache_resource
def get_services():
    """Initialise database and AI"""
    try:
        db_path = st.secrets.get("DB_PATH", "DATA/intelligence_platform.db")
        ai_key = st.secrets.get("GEMINI_API_KEY", "")
    except:
        db_path = "DATA/intelligence_platform.db"
        ai_key = ""
    
    db = DatabaseManager(db_path)
    db.connect()
    ai = AIAssistant(ai_key) if ai_key else None
    return db, ai

db, ai = get_services()

# Header
col_title, col_user = st.columns([3, 1])
with col_title:
    st.title("🛡️ Cybersecurity Operations Center")
    st.caption("Security Incident Management & Threat Analysis")
with col_user:
    st.markdown(f"""<div style="text-align: right; padding: 10px;">
        <strong>{st.session_state.username}</strong><br>
        <small>{user.get_role_display_name()}</small>
    </div>""", unsafe_allow_html=True)

st.divider()

# Sidebar filters (Week 8 criteria)
with st.sidebar:
    st.header("🔧 Dashboard Controls")
    st.subheader("🎯 Filters")
    
    severity_filter = st.multiselect(
        "Severity Level",
        options=["Low", "Medium", "High", "Critical"],
        default=[]
    )
    
    status_filter = st.multiselect(
        "Status",
        options=["Open", "Investigating", "Resolved", "Closed"],
        default=[]
    )
    
    incident_type_filter = st.multiselect(
        "Incident Type",
        options=["Phishing", "Malware", "DDoS", "Data Breach", "Ransomware", "Insider Threat", "Other"],
        default=[]
    )
    
    st.divider()
    if st.button("🔄 Refresh Data", use_container_width=True):
        st.cache_data.clear()
        st.rerun()
    
    st.divider()
    st.subheader("⚡ Quick Actions")
    show_add_incident = st.button("➕ Report New Incident", use_container_width=True, type="primary")

# Fetch incidents
@st.cache_data(ttl=60)
def load_incidents():
    """Load incidents as SecurityIncident objects"""
    query = "SELECT id, date, incident_type, severity, status, description, reported_by FROM cyber_incidents ORDER BY date DESC, id DESC"
    rows = db.fetch_all(query)
    
    incidents = []
    for row in rows:
        incident = SecurityIncident(
            incident_id=row[0], date=row[1], incident_type=row[2],
            severity=row[3], status=row[4], description=row[5], reported_by=row[6]
        )
        incidents.append(incident)
    return incidents

incidents = load_incidents()

# Convert to DataFrame
def incidents_to_dataframe(incidents_list):
    """Convert incidents to pandas DataFrame"""
    data = []
    for incident in incidents_list:
        data.append({
            "ID": incident.get_id(),
            "Date": incident.get_date(),
            "Type": incident.get_incident_type(),
            "Severity": incident.get_severity(),
            "Status": incident.get_status(),
            "Description": incident.get_description(),
            "Reported By": incident.get_reported_by(),
            "Severity_Level": incident.get_severity_level()
        })
    return pd.DataFrame(data)

df = incidents_to_dataframe(incidents)

# Apply filters
if not df.empty:
    df_filtered = df.copy()
    
    if severity_filter:
        df_filtered = df_filtered[df_filtered["Severity"].isin(severity_filter)]
    
    if status_filter:
        df_filtered = df_filtered[df_filtered["Status"].isin(status_filter)]
    
    if incident_type_filter:
        df_filtered = df_filtered[df_filtered["Type"].isin(incident_type_filter)]
else:
    df_filtered = df

# Metrics row
st.subheader("📊 Executive Summary")

col1, col2, col3, col4, col5 = st.columns(5)

with col1:
    st.metric("Total Incidents", len(incidents))

with col2:
    open_count = len([i for i in incidents if i.is_open()])
    st.metric("Active Incidents", open_count, delta=f"+{open_count}" if open_count > 0 else "0", delta_color="inverse")

with col3:
    critical_count = len([i for i in incidents if i.is_critical()])
    st.metric("Critical Alerts", critical_count, delta="Urgent" if critical_count > 0 else "None", delta_color="inverse")

with col4:
    total = len(incidents)
    if total > 0:
        resolution_rate = ((total - open_count) / total) * 100
        st.metric("Resolution Rate", f"{resolution_rate:.1f}%")
    else:
        st.metric("Resolution Rate", "N/A")

with col5:
    st.metric("Avg. Resolution", "3.5 days")

st.divider()

# Visualisations (Professional charts as before)
st.subheader("📈 Threat Intelligence Analytics")

if not df_filtered.empty:
    
    # Row 1: Main charts
    chart_col1, chart_col2 = st.columns(2)
    
    with chart_col1:
        st.markdown("**🎯 Incident Distribution by Type**")
        type_counts = df_filtered["Type"].value_counts()
        fig_types = px.pie(values=type_counts.values, names=type_counts.index, hole=0.4, color_discrete_sequence=px.colors.qualitative.Set3)
        fig_types.update_traces(textposition='inside', textinfo='percent+label')
        fig_types.update_layout(showlegend=True, height=400)
        st.plotly_chart(fig_types, use_container_width=True)
    
    with chart_col2:
        st.markdown("**⚠️ Severity Level Distribution**")
        severity_counts = df_filtered["Severity"].value_counts()
        color_map = {"Low": "#90EE90", "Medium": "#FFD700", "High": "#FFA500", "Critical": "#FF4500"}
        colors = [color_map.get(sev, "#CCCCCC") for sev in severity_counts.index]
        
        fig_severity = go.Figure(data=[go.Bar(x=severity_counts.index, y=severity_counts.values, marker_color=colors, text=severity_counts.values, textposition='auto')])
        fig_severity.update_layout(xaxis_title="Severity Level", yaxis_title="Count", showlegend=False, height=400)
        st.plotly_chart(fig_severity, use_container_width=True)
    
    # Row 2: Status and timeline
    chart_col3, chart_col4 = st.columns(2)
    
    with chart_col3:
        st.markdown("**🔄 Current Status Overview**")
        status_counts = df_filtered["Status"].value_counts()
        status_colors = {"Open": "#FF6B6B", "Investigating": "#FFA500", "Resolved": "#4ECDC4", "Closed": "#95E1D3"}
        
        fig_status = go.Figure(data=[go.Pie(labels=status_counts.index, values=status_counts.values, hole=0.3, marker=dict(colors=[status_colors.get(s, "#CCCCCC") for s in status_counts.index]))])
        fig_status.update_traces(textinfo='label+percent')
        fig_status.update_layout(height=400)
        st.plotly_chart(fig_status, use_container_width=True)
    
    with chart_col4:
        st.markdown("**📅 Incident Timeline**")
        df_timeline = df_filtered.copy()
        df_timeline['Date'] = pd.to_datetime(df_timeline['Date'])
        timeline_data = df_timeline.groupby('Date').size().reset_index(name='Count')
        
        fig_timeline = px.line(timeline_data, x='Date', y='Count', markers=True, line_shape='spline')
        fig_timeline.update_traces(line_color='#0EA5E9', marker=dict(size=8, color='#0EA5E9'))
        fig_timeline.update_layout(xaxis_title="Date", yaxis_title="Incidents", height=400)
        st.plotly_chart(fig_timeline, use_container_width=True)
    
    # Row 3: Advanced analytics
    st.markdown("**🔍 Advanced Threat Analysis**")
    
    analysis_col1, analysis_col2, analysis_col3 = st.columns(3)
    
    with analysis_col1:
        st.markdown("**Top 5 Threat Vectors**")
        top_types = df_filtered["Type"].value_counts().head(5)
        fig_top = go.Figure(data=[go.Bar(y=top_types.index[::-1], x=top_types.values[::-1], orientation='h', marker_color='#0EA5E9', text=top_types.values[::-1], textposition='auto')])
        fig_top.update_layout(xaxis_title="Count", yaxis_title="", height=300, margin=dict(l=150))
        st.plotly_chart(fig_top, use_container_width=True)
    
    with analysis_col2:
        st.markdown("**Severity vs Status Matrix**")
        severity_status = pd.crosstab(df_filtered['Severity'], df_filtered['Status'])
        fig_heatmap = go.Figure(data=go.Heatmap(z=severity_status.values, x=severity_status.columns, y=severity_status.index, colorscale='YlOrRd', text=severity_status.values, texttemplate='%{text}'))
        fig_heatmap.update_layout(xaxis_title="Status", yaxis_title="Severity", height=300)
        st.plotly_chart(fig_heatmap, use_container_width=True)
    
    with analysis_col3:
        st.markdown("**Reporter Statistics**")
        reporter_counts = df_filtered["Reported By"].value_counts().head(5)
        fig_reporters = px.bar(x=reporter_counts.values, y=reporter_counts.index, orientation='h', color=reporter_counts.values, color_continuous_scale='Blues')
        fig_reporters.update_layout(xaxis_title="Reports", yaxis_title="", showlegend=False, height=300, margin=dict(l=100))
        st.plotly_chart(fig_reporters, use_container_width=True)

else:
    st.info("📊 No incidents match the filters. Adjust filters or report new incident.")

st.divider()

# Incidents table
st.subheader("🔍 Incident Management")

if not df_filtered.empty:
    filter_summary = f"Showing **{len(df_filtered)}** of **{len(df)}** incidents"
    st.caption(filter_summary)
    
    selected_incident_id = st.selectbox(
        "Select incident to view details:",
        options=df_filtered["ID"].tolist(),
        format_func=lambda x: f"INC-{x:04d} | {df_filtered[df_filtered['ID']==x]['Type'].values[0]} | {df_filtered[df_filtered['ID']==x]['Severity'].values[0]}"
    )
    
    st.dataframe(df_filtered.drop(columns=['Severity_Level']), use_container_width=True, hide_index=True)
    
    # AI Analysis section
    if ai and selected_incident_id:
        st.divider()
        st.subheader("🤖 AI-Powered Incident Analysis")
        
        selected_incident = next(i for i in incidents if i.get_id() == selected_incident_id)
        
        col_ai1, col_ai2 = st.columns([3, 1])
        with col_ai1:
            st.markdown(f"**Analysing Incident #{selected_incident_id}:** {selected_incident.get_incident_type()}")
        with col_ai2:
            analyse_button = st.button("🔬 Analyse with AI", use_container_width=True, type="primary")
        
        if analyse_button:
            with st.spinner("🤖 AI is analysing the incident..."):
                context = selected_incident.get_ai_context()
                ai.set_domain("cybersecurity")
                analysis = ai.analyse_incident(context)
                
                with st.expander("📊 Analysis Report", expanded=True):
                    st.markdown(analysis)
                
                st.divider()
                st.markdown("#### 💬 Ask Follow-up Questions")
                follow_up = st.text_input("Have questions?", placeholder="e.g., What MITRE ATT&CK techniques are involved?")
                
                if follow_up:
                    with st.spinner("🤖 Generating response..."):
                        response = ai.send_message(follow_up, context=context)
                        st.markdown("**AI Response:**")
                        st.info(response)
    else:
        if not ai:
            st.warning("⚠️ AI Assistant not configured. Add Gemini API key to enable AI analysis.")

else:
    st.info("📊 No incidents to display.")

# Add incident form
if show_add_incident:
    st.divider()
    st.subheader("➕ Report New Security Incident")
    
    with st.form("new_incident_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            incident_date = st.date_input("Date", value=datetime.today())
            incident_type = st.selectbox("Type", ["Phishing", "Malware", "DDoS", "Data Breach", "Ransomware", "Insider Threat", "Other"])
            severity = st.selectbox("Severity", ["Low", "Medium", "High", "Critical"], index=2)
        
        with col2:
            status = st.selectbox("Status", ["Open", "Investigating"], index=0)
            reported_by = st.text_input("Reported By", value=st.session_state.username, disabled=True)
        
        description = st.text_area("Description", placeholder="Detailed incident description...", height=150)
        
        submit = st.form_submit_button("🚀 Submit Incident", use_container_width=True, type="primary")
        
        if submit:
            if not description or len(description) < 20:
                st.error("⚠️ Description must be at least 20 characters")
            else:
                try:
                    query = "INSERT INTO cyber_incidents (date, incident_type, severity, status, description, reported_by) VALUES (?, ?, ?, ?, ?, ?)"
                    db.execute_query(query, (str(incident_date), incident_type, severity, status, description, reported_by))
                    st.success("✅ Incident reported successfully!")
                    st.cache_data.clear()
                    st.rerun()
                except Exception as e:
                    st.error(f"❌ Error: {e}")

# Footer
st.divider()
st.caption("🛡️ Cybersecurity Operations Center | Powered by Google Gemini AI")
st.caption(f"Session: {st.session_state.username} | {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")