"""Cybersecurity Dashboard"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import os

from app.services.database_manager import DatabaseManager
from app.services.ai_assistant import GeminiClient

# Page configuration
st.set_page_config(page_title="Cybersecurity | Intelligence Platform", page_icon="🛡️", layout="wide")

#Authentication & Authorisation Check 
if not st.session_state.get("logged_in", False):
    st.error("🔒 Access Denied")
    st.warning("You must be logged in to view this page.")
    if st.button("Go to Login"):
        st.switch_page("Home.py")
    st.stop()

user = st.session_state.get("user_object")
if user and not user.can_access_domain('cybersecurity'):
    st.error("🚫 Access Denied")
    st.warning(f"Your role ({user.get_role_display_name()}) does not have permission to access the Cybersecurity domain.")
    if st.button("Return to Home"):
        st.switch_page("Home.py")
    st.stop()

#Initialise Services
@st.cache_resource
def get_services():
    """Initialize database and AI client with caching"""
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

# --- Header ---
col1, col2 = st.columns([3, 1])
with col1:
    st.title("🛡️ Cybersecurity Operations Center")
with col2:
    st.markdown(f"**{st.session_state.username}**<br><small>{user.get_role_display_name()}</small>", unsafe_allow_html=True)

st.divider()

# --- Sidebar Filters ---
with st.sidebar:
    st.header("🔧 Filters")
    severity_filter = st.multiselect("Severity", ["Low", "Medium", "High", "Critical"])
    status_filter = st.multiselect("Status", ["Open", "In Progress", "Resolved", "Closed"])
    type_filter = st.multiselect("Type", ["Phishing", "Malware", "DDoS", "Misconfiguration", "Unauthorized Access"])
    
    st.divider()
    if st.button("🔄 Refresh", use_container_width=True):
        st.cache_data.clear()
        st.rerun()
    
    show_add = st.button("➕ New Incident", use_container_width=True, type="primary")

# --- Load Incident Data from CSV ---
@st.cache_data(ttl=60)
def load_incidents():
    """Load incidents from CSV file"""
    csv_path = "DATA/cyber_incidents.csv"
    if os.path.exists(csv_path):
        df = pd.read_csv(csv_path)
        # CSV already has correct column names: ID, Date, Type, Severity, Status, Description, Reported By
        # Ensure Reported By column exists (handle space in column name)
        if 'Reported By' not in df.columns and 'Reported_By' not in df.columns:
            df['Reported By'] = 'System'
        elif 'Reported_By' in df.columns:
            df = df.rename(columns={'Reported_By': 'Reported By'})
        return df
    return pd.DataFrame()

df = load_incidents()

# Apply sidebar filters
if not df.empty:
    df_f = df.copy()
    if severity_filter: df_f = df_f[df_f["Severity"].isin(severity_filter)]
    if status_filter: df_f = df_f[df_f["Status"].isin(status_filter)]
    if type_filter: df_f = df_f[df_f["Type"].isin(type_filter)]
else:
    df_f = df

#Metrics Dashboard
st.subheader("📊 Executive Summary")
m1, m2, m3, m4, m5 = st.columns(5)

total = len(df)
active = len(df[df["Status"].isin(["Open", "In Progress"])]) if not df.empty else 0
critical = len(df[df["Severity"] == "Critical"]) if not df.empty else 0
resolved = len(df[df["Status"].isin(["Resolved", "Closed"])]) if not df.empty else 0
rate = (resolved / total * 100) if total > 0 else 0

m1.metric("Total Incidents", total)
m2.metric("Active Threats", active)
m3.metric("Critical", critical)
m4.metric("Resolved", resolved)
m5.metric("Resolution Rate", f"{rate:.0f}%")

st.divider()

# --- Visualization Section ---
st.subheader("📈 Threat Analytics")

if not df_f.empty:
    # Row 1: Pie, Bar, and Gauge charts
    c1, c2, c3 = st.columns(3)
    
    with c1:
        # Donut chart for incident types
        type_counts = df_f["Type"].value_counts()
        fig = go.Figure(data=[go.Pie(
            labels=type_counts.index, values=type_counts.values, hole=0.5,
            marker_colors=px.colors.sequential.Blues_r[:len(type_counts)]
        )])
        fig.update_layout(title="Incidents by Type", height=300, showlegend=True)
        st.plotly_chart(fig, use_container_width=True)
    
    with c2:
        # Bar chart for severity distribution
        sev_counts = df_f["Severity"].value_counts()
        sev_order = ["Low", "Medium", "High", "Critical"]
        sev_sorted = {s: sev_counts.get(s, 0) for s in sev_order}
        colors = ["#93c5fd", "#60a5fa", "#f87171", "#dc2626"]
        fig = go.Figure(data=[go.Bar(
            x=list(sev_sorted.keys()), y=list(sev_sorted.values()),
            marker_color=colors, text=list(sev_sorted.values()), textposition='auto'
        )])
        fig.update_layout(title="Severity Distribution", height=300)
        st.plotly_chart(fig, use_container_width=True)
    
    with c3:
        # Gauge indicator for threat level
        threat_score = min(100, (critical * 25) + (active * 10))
        fig = go.Figure(go.Indicator(
            mode="gauge+number",
            value=threat_score,
            gauge={
                'axis': {'range': [0, 100]},
                'bar': {'color': "#dc2626" if threat_score > 70 else "#f59e0b" if threat_score > 40 else "#3b82f6"},
                'steps': [
                    {'range': [0, 40], 'color': "#dbeafe"},
                    {'range': [40, 70], 'color': "#fef3c7"},
                    {'range': [70, 100], 'color': "#fecaca"}
                ]
            },
            title={'text': "Threat Level"}
        ))
        fig.update_layout(height=300)
        st.plotly_chart(fig, use_container_width=True)
    
    # Row 2: Timeline and status overview
    c4, c5 = st.columns(2)
    
    with c4:
        # Area chart for incident timeline
        df_time = df_f.copy()
        df_time['Date'] = pd.to_datetime(df_time['Date'])
        daily = df_time.groupby('Date').size().reset_index(name='Count')
        fig = px.area(daily, x='Date', y='Count', title="Incident Timeline")
        fig.update_traces(fill='tozeroy', line_color='#3b82f6', fillcolor='rgba(59,130,246,0.3)')
        fig.update_layout(height=300)
        st.plotly_chart(fig, use_container_width=True)
    
    with c5:
        # Horizontal bar chart for status overview
        status_counts = df_f["Status"].value_counts()
        colors_status = {"Open": "#ef4444", "Investigating": "#f59e0b", "Resolved": "#3b82f6", "Closed": "#6b7280"}
        fig = go.Figure(data=[go.Bar(
            y=status_counts.index, x=status_counts.values, orientation='h',
            marker_color=[colors_status.get(s, "#3b82f6") for s in status_counts.index],
            text=status_counts.values, textposition='auto'
        )])
        fig.update_layout(title="Status Overview", height=300)
        st.plotly_chart(fig, use_container_width=True)
    
    # Row 3: Heatmap and treemap
    c6, c7 = st.columns(2)
    
    with c6:
        # Heatmap for type vs severity correlation
        cross = pd.crosstab(df_f['Type'], df_f['Severity'])
        fig = px.imshow(cross, text_auto=True, color_continuous_scale='Blues', title="Type vs Severity")
        fig.update_layout(height=350)
        st.plotly_chart(fig, use_container_width=True)
    
    with c7:
        # Treemap for incident hierarchy
        fig = px.treemap(df_f, path=['Status', 'Type'], title="Incident Hierarchy", 
                        color_discrete_sequence=px.colors.sequential.Blues_r)
        fig.update_layout(height=350)
        st.plotly_chart(fig, use_container_width=True)

else:
    st.info("No incidents match filters")

st.divider()

# Incident Management & AI Analysis
st.subheader("🔍 Incident Management")

if not df_f.empty:
    # Incident selection dropdown
    selected_id = st.selectbox("Select Incident", df_f["ID"].tolist(),
        format_func=lambda x: f"INC-{int(x):04d} | {df_f[df_f['ID']==x]['Type'].values[0]} | {df_f[df_f['ID']==x]['Severity'].values[0]}")
    
    # Data table display
    st.dataframe(df_f[['ID', 'Date', 'Type', 'Severity', 'Status', 'Description']], use_container_width=True, hide_index=True)
    
    # Get selected incident details
    selected_incident = df_f[df_f['ID'] == selected_id].iloc[0]
    
    # AI Assistant Section
    if client:
        st.divider()
        st.subheader("🤖 AI Analysis")
        
        # AI analysis buttons
        b1, b2, b3 = st.columns(3)
        with b1:
            btn1 = st.button("🔬 Analyse Incident", use_container_width=True)
        with b2:
            btn2 = st.button("📊 Dashboard Insights", use_container_width=True, type="primary")
        with b3:
            btn3 = st.button("🎯 Threat Intel", use_container_width=True)
        
        # Individual AI analysis handlers
        if btn1:
            incident_context = f"""
Incident ID: {selected_incident['ID']}
Date: {selected_incident['Date']}
Type: {selected_incident['Type']}
Severity: {selected_incident['Severity']}
Status: {selected_incident['Status']}
Description: {selected_incident['Description']}
"""
            messages = [
                {"role": "system", "content": "You're a cybersecurity analyst. Be concise."},
                {"role": "user", "content": f"Analyse this incident:\n{incident_context}"}
            ]
            with st.chat_message("assistant"):
                container = st.empty()
                full = ""
                for chunk in client.chat.completions.create(model="gemini-2.0-flash", messages=messages, stream=True, domain="Cybersecurity"):
                    if chunk.choices[0].delta.content:
                        full += chunk.choices[0].delta.content
                        container.markdown(full + "▌")
                container.markdown(full)
        
        if btn2:
            summary = f"""Dashboard Summary:
- Total: {total}, Active: {active}, Critical: {critical}
- Resolution Rate: {rate:.0f}%
- Types: {df_f['Type'].value_counts().to_dict()}
- Severity: {df_f['Severity'].value_counts().to_dict()}
- Status: {df_f['Status'].value_counts().to_dict()}"""
            messages = [
                {"role": "system", "content": "You're a security analyst. Provide insights."},
                {"role": "user", "content": f"Analyse:\n{summary}"}
            ]
            with st.chat_message("assistant"):
                container = st.empty()
                full = ""
                for chunk in client.chat.completions.create(model="gemini-2.0-flash", messages=messages, stream=True, domain="Cybersecurity"):
                    if chunk.choices[0].delta.content:
                        full += chunk.choices[0].delta.content
                        container.markdown(full + "▌")
                container.markdown(full)
        
        if btn3:
            messages = [
                {"role": "system", "content": "You're a threat intelligence analyst."},
                {"role": "user", "content": f"Threat landscape insights for: {df_f['Type'].value_counts().to_dict()}"}
            ]
            with st.chat_message("assistant"):
                container = st.empty()
                full = ""
                for chunk in client.chat.completions.create(model="gemini-2.0-flash", messages=messages, stream=True, domain="Cybersecurity"):
                    if chunk.choices[0].delta.content:
                        full += chunk.choices[0].delta.content
                        container.markdown(full + "▌")
                container.markdown(full)
        
        # General AI chat input
        st.divider()
        q = st.chat_input("Ask about security...")
        if q:
            messages = [{"role": "system", "content": "You're a security assistant. Only use cybersecurity incident data from this dashboard."}, {"role": "user", "content": q}]
            with st.chat_message("user"):
                st.markdown(q)
            with st.chat_message("assistant"):
                container = st.empty()
                full = ""
                for chunk in client.chat.completions.create(model="gemini-2.0-flash", messages=messages, stream=True, domain="Cybersecurity"):
                    if chunk.choices[0].delta.content:
                        full += chunk.choices[0].delta.content
                        container.markdown(full + "▌")
                container.markdown(full)
    else:
        st.warning("⚠️ AI not configured")

#New Incident Form
if show_add:
    st.divider()
    st.subheader("➕ Report Incident")
    
    with st.form("new_incident"):
        c1, c2 = st.columns(2)
        with c1:
            date = st.date_input("Date", datetime.today())
            inc_type = st.selectbox("Type", ["Phishing", "Malware", "DDoS", "Misconfiguration", "Unauthorized Access", "Other"])
            severity = st.selectbox("Severity", ["Low", "Medium", "High", "Critical"], index=2)
        with c2:
            status = st.selectbox("Status", ["Open", "In Progress"])
            reported = st.text_input("Reported By", st.session_state.username, disabled=True)
        
        desc = st.text_area("Description", placeholder="Describe the incident...", height=100)
        
        if st.form_submit_button("🚀 Submit", use_container_width=True, type="primary"):
            if desc and len(desc) >= 20:
                # Load existing CSV, add new row, save back
                csv_path = "DATA/cyber_incidents.csv"
                if os.path.exists(csv_path):
                    existing_df = pd.read_csv(csv_path)
                    new_id = existing_df['incident_id'].max() + 1
                else:
                    existing_df = pd.DataFrame(columns=['incident_id', 'timestamp', 'severity', 'category', 'status', 'description'])
                    new_id = 1000
                
                new_row = pd.DataFrame([{
                    'incident_id': new_id,
                    'timestamp': f"{date} 00:00:00.000000",
                    'severity': severity,
                    'category': inc_type,
                    'status': status,
                    'description': desc
                }])
                updated_df = pd.concat([existing_df, new_row], ignore_index=True)
                os.makedirs("DATA", exist_ok=True)
                updated_df.to_csv(csv_path, index=False)
                st.success("✅ Incident reported!")
                st.cache_data.clear()
                st.rerun()
            else:
                st.error("Description must be at least 20 characters")

# --- Footer ---
st.divider()
st.caption(f"🛡️ Cybersecurity Operations | {st.session_state.username} | {datetime.now().strftime('%H:%M:%S')}")