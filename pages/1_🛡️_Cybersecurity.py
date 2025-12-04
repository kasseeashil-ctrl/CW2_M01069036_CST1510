"""
Cybersecurity Domain Dashboard - Professional Edition
Comprehensive security incident management with advanced analytics
"""

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

# Authentication and permission check
if not st.session_state.get("logged_in", False):
    st.error("🔒 Please login to access this page")
    if st.button("Go to Login"):
        st.switch_page("Home.py")
    st.stop()

# Check if user has permission to access this domain
user = st.session_state.get("user_object")
if user and not user.can_access_domain('cybersecurity'):
    st.error(f"🚫 Access Denied: Your role ({user.get_role_display_name()}) does not have permission to access the Cybersecurity domain.")
    st.info("Please contact your administrator if you need access to this domain.")
    if st.button("Return to Home"):
        st.switch_page("Home.py")
    st.stop()

# Initialise services
@st.cache_resource
def get_services():
    """Initialise database and AI services."""
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

# Header with user info
col_title, col_user = st.columns([3, 1])

with col_title:
    st.title("🛡️ Cybersecurity Operations Center")
    st.caption("Security Incident Management & Threat Analysis")

with col_user:
    st.markdown(f"""
    <div style="text-align: right; padding: 10px;">
        <strong>{st.session_state.username}</strong><br>
        <small>{user.get_role_display_name()}</small>
    </div>
    """, unsafe_allow_html=True)

st.divider()

# Sidebar controls
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
        options=["Phishing", "Malware", "DDoS", "Data Breach", "Ransomware", "Insider Threat", "Vulnerability", "Social Engineering", "Other"],
        default=[]
    )
    
    st.divider()
    
    # Refresh controls
    if st.button("🔄 Refresh Data", use_container_width=True):
        st.cache_data.clear()
        st.rerun()
    
    st.divider()
    
    # Quick actions
    st.subheader("⚡ Quick Actions")
    show_add_incident = st.button("➕ Report New Incident", use_container_width=True, type="primary")
    
    if st.button("📊 Generate Report", use_container_width=True):
        st.info("Report generation feature coming soon!")

# Fetch incidents from database
@st.cache_data(ttl=60)
def load_incidents():
    """Load all incidents from database as SecurityIncident objects."""
    query = """
    SELECT id, date, incident_type, severity, status, description, reported_by
    FROM cyber_incidents
    ORDER BY date DESC, id DESC
    """
    rows = db.fetch_all(query)
    
    incidents = []
    for row in rows:
        incident = SecurityIncident(
            incident_id=row[0],
            date=row[1],
            incident_type=row[2],
            severity=row[3],
            status=row[4],
            description=row[5],
            reported_by=row[6]
        )
        incidents.append(incident)
    
    return incidents

incidents = load_incidents()

# Convert to DataFrame
def incidents_to_dataframe(incidents_list):
    """Convert list of SecurityIncident objects to pandas DataFrame."""
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
    
    # Severity filter
    if severity_filter:
        df_filtered = df_filtered[df_filtered["Severity"].isin(severity_filter)]
    
    # Status filter
    if status_filter:
        df_filtered = df_filtered[df_filtered["Status"].isin(status_filter)]
    
    # Incident type filter
    if incident_type_filter:
        df_filtered = df_filtered[df_filtered["Type"].isin(incident_type_filter)]
else:
    df_filtered = df

# ========== KEY METRICS ROW ==========
st.subheader("📊 Executive Summary")

metric_col1, metric_col2, metric_col3, metric_col4, metric_col5 = st.columns(5)

with metric_col1:
    total_incidents = len(incidents)
    st.metric(
        "Total Incidents",
        total_incidents,
        help="All recorded security incidents"
    )

with metric_col2:
    open_incidents = len([i for i in incidents if i.is_open()])
    delta_open = f"+{open_incidents}" if open_incidents > 0 else "0"
    st.metric(
        "Active Incidents",
        open_incidents,
        delta=delta_open,
        delta_color="inverse",
        help="Currently open or under investigation"
    )

with metric_col3:
    critical_incidents = len([i for i in incidents if i.is_critical()])
    st.metric(
        "Critical Alerts",
        critical_incidents,
        delta="Urgent" if critical_incidents > 0 else "None",
        delta_color="inverse",
        help="Incidents requiring immediate attention"
    )

with metric_col4:
    if total_incidents > 0:
        resolution_rate = ((total_incidents - open_incidents) / total_incidents) * 100
        st.metric(
            "Resolution Rate",
            f"{resolution_rate:.1f}%",
            help="Percentage of closed incidents"
        )
    else:
        st.metric("Resolution Rate", "N/A")

with metric_col5:
    # Calculate average resolution time (mock data for demo)
    avg_resolution_days = 3.5
    st.metric(
        "Avg. Resolution",
        f"{avg_resolution_days:.1f} days",
        help="Average time to resolve incidents"
    )

st.divider()

# ========== ADVANCED VISUALIZATIONS ==========
st.subheader("📈 Threat Intelligence Analytics")

if not df_filtered.empty:
    
    # Row 1: Main Charts
    chart_col1, chart_col2 = st.columns(2)
    
    with chart_col1:
        st.markdown("**🎯 Incident Distribution by Type**")
        type_counts = df_filtered["Type"].value_counts()
        
        fig_types = px.pie(
            values=type_counts.values,
            names=type_counts.index,
            hole=0.4,
            color_discrete_sequence=px.colors.qualitative.Set3
        )
        fig_types.update_traces(
            textposition='inside',
            textinfo='percent+label',
            hovertemplate='<b>%{label}</b><br>Count: %{value}<br>Percentage: %{percent}<extra></extra>'
        )
        fig_types.update_layout(
            showlegend=True,
            legend=dict(orientation="v", yanchor="middle", y=0.5, xanchor="left", x=1.02),
            height=400
        )
        st.plotly_chart(fig_types, use_container_width=True)
    
    with chart_col2:
        st.markdown("**⚠️ Severity Level Distribution**")
        severity_counts = df_filtered["Severity"].value_counts()
        
        # Define color mapping
        color_map = {
            "Low": "#90EE90",
            "Medium": "#FFD700",
            "High": "#FFA500",
            "Critical": "#FF4500"
        }
        colors = [color_map.get(sev, "#CCCCCC") for sev in severity_counts.index]
        
        fig_severity = go.Figure(data=[
            go.Bar(
                x=severity_counts.index,
                y=severity_counts.values,
                marker_color=colors,
                text=severity_counts.values,
                textposition='auto',
                hovertemplate='<b>%{x}</b><br>Count: %{y}<extra></extra>'
            )
        ])
        fig_severity.update_layout(
            xaxis_title="Severity Level",
            yaxis_title="Number of Incidents",
            showlegend=False,
            height=400
        )
        st.plotly_chart(fig_severity, use_container_width=True)
    
    # Row 2: Status and Timeline
    chart_col3, chart_col4 = st.columns(2)
    
    with chart_col3:
        st.markdown("**🔄 Current Status Overview**")
        status_counts = df_filtered["Status"].value_counts()
        
        # Status color mapping
        status_colors = {
            "Open": "#FF6B6B",
            "Investigating": "#FFA500",
            "Resolved": "#4ECDC4",
            "Closed": "#95E1D3"
        }
        
        fig_status = go.Figure(data=[
            go.Pie(
                labels=status_counts.index,
                values=status_counts.values,
                hole=0.3,
                marker=dict(colors=[status_colors.get(s, "#CCCCCC") for s in status_counts.index]),
                textinfo='label+percent',
                hovertemplate='<b>%{label}</b><br>Count: %{value}<br>Percentage: %{percent}<extra></extra>'
            )
        ])
        fig_status.update_layout(height=400)
        st.plotly_chart(fig_status, use_container_width=True)
    
    with chart_col4:
        st.markdown("**📅 Incident Timeline (Last 30 Days)**")
        
        # Prepare timeline data
        if 'Date' not in df_filtered.columns or df_filtered.empty:
            st.info("No timeline data available")
        else:
            df_timeline = df_filtered.copy()
            df_timeline['Date'] = pd.to_datetime(df_timeline['Date'])
            
            # Group by date
            timeline_data = df_timeline.groupby('Date').size().reset_index(name='Count')
            
            fig_timeline = px.line(
                timeline_data,
                x='Date',
                y='Count',
                markers=True,
                line_shape='spline'
            )
            fig_timeline.update_traces(
                line_color='#0EA5E9',
                marker=dict(size=8, color='#0EA5E9'),
                hovertemplate='<b>%{x|%Y-%m-%d}</b><br>Incidents: %{y}<extra></extra>'
            )
            fig_timeline.update_layout(
                xaxis_title="Date",
                yaxis_title="Number of Incidents",
                hovermode='x unified',
                height=400
            )
            st.plotly_chart(fig_timeline, use_container_width=True)
    
    # Row 3: Advanced Analytics
    st.markdown("**🔍 Advanced Threat Analysis**")
    
    analysis_col1, analysis_col2, analysis_col3 = st.columns(3)
    
    with analysis_col1:
        st.markdown("**Top 5 Threat Vectors**")
        top_types = df_filtered["Type"].value_counts().head(5)
        
        fig_top_types = go.Figure(data=[
            go.Bar(
                y=top_types.index[::-1],
                x=top_types.values[::-1],
                orientation='h',
                marker_color='#0EA5E9',
                text=top_types.values[::-1],
                textposition='auto',
                hovertemplate='<b>%{y}</b><br>Count: %{x}<extra></extra>'
            )
        ])
        fig_top_types.update_layout(
            xaxis_title="Count",
            yaxis_title="",
            height=300,
            margin=dict(l=150)
        )
        st.plotly_chart(fig_top_types, use_container_width=True)
    
    with analysis_col2:
        st.markdown("**Severity vs Status Matrix**")
        
        # Create cross-tabulation
        severity_status = pd.crosstab(df_filtered['Severity'], df_filtered['Status'])
        
        fig_heatmap = go.Figure(data=go.Heatmap(
            z=severity_status.values,
            x=severity_status.columns,
            y=severity_status.index,
            colorscale='YlOrRd',
            text=severity_status.values,
            texttemplate='%{text}',
            textfont={"size": 12},
            hovertemplate='Severity: %{y}<br>Status: %{x}<br>Count: %{z}<extra></extra>'
        ))
        fig_heatmap.update_layout(
            xaxis_title="Status",
            yaxis_title="Severity",
            height=300
        )
        st.plotly_chart(fig_heatmap, use_container_width=True)
    
    with analysis_col3:
        st.markdown("**Incident Reporter Statistics**")
        reporter_counts = df_filtered["Reported By"].value_counts().head(5)
        
        fig_reporters = px.bar(
            x=reporter_counts.values,
            y=reporter_counts.index,
            orientation='h',
            color=reporter_counts.values,
            color_continuous_scale='Blues'
        )
        fig_reporters.update_traces(
            hovertemplate='<b>%{y}</b><br>Reports: %{x}<extra></extra>'
        )
        fig_reporters.update_layout(
            xaxis_title="Number of Reports",
            yaxis_title="",
            showlegend=False,
            height=300,
            margin=dict(l=100)
        )
        st.plotly_chart(fig_reporters, use_container_width=True)

else:
    st.info("📊 No incidents match the selected filters. Adjust your filters or report a new incident.")

st.divider()

# ========== INCIDENTS DATA TABLE ==========
st.subheader("🔍 Incident Management")

if not df_filtered.empty:
    # Display count and filters summary
    filter_summary = f"Showing **{len(df_filtered)}** of **{len(df)}** incidents"
    if severity_filter:
        filter_summary += f" | Severity: {', '.join(severity_filter)}"
    if status_filter:
        filter_summary += f" | Status: {', '.join(status_filter)}"
    
    st.caption(filter_summary)
    
    # Incident selection
    selected_incident_id = st.selectbox(
        "Select an incident to view details:",
        options=df_filtered["ID"].tolist(),
        format_func=lambda x: f"INC-{x:04d} | {df_filtered[df_filtered['ID']==x]['Type'].values[0]} | {df_filtered[df_filtered['ID']==x]['Severity'].values[0]} | {df_filtered[df_filtered['ID']==x]['Status'].values[0]}"
    )
    
    # Display full incident table
    st.dataframe(
        df_filtered.drop(columns=['Severity_Level']),
        use_container_width=True,
        hide_index=True,
        column_config={
            "ID": st.column_config.NumberColumn("Incident ID", width="small", format="INC-%04d"),
            "Date": st.column_config.DateColumn("Date", width="small"),
            "Type": st.column_config.TextColumn("Threat Type", width="medium"),
            "Severity": st.column_config.TextColumn("Severity", width="small"),
            "Status": st.column_config.TextColumn("Status", width="small"),
            "Description": st.column_config.TextColumn("Description", width="large"),
            "Reported By": st.column_config.TextColumn("Reporter", width="small")
        }
    )
    
    # ========== INCIDENT DETAILS & AI ANALYSIS ==========
    if selected_incident_id:
        st.divider()
        
        # Get selected incident object
        selected_incident = next(i for i in incidents if i.get_id() == selected_incident_id)
        
        # Display detailed incident information
        st.subheader(f"📋 Incident Details: INC-{selected_incident_id:04d}")
        
        detail_col1, detail_col2, detail_col3, detail_col4 = st.columns(4)
        
        with detail_col1:
            st.markdown("**Incident Type**")
            st.info(selected_incident.get_incident_type())
        
        with detail_col2:
            severity = selected_incident.get_severity()
            severity_emoji = {"Low": "🟢", "Medium": "🟡", "High": "🟠", "Critical": "🔴"}
            st.markdown("**Severity Level**")
            st.warning(f"{severity_emoji.get(severity, '⚪')} {severity}")
        
        with detail_col3:
            st.markdown("**Current Status**")
            st.success(selected_incident.get_status())
        
        with detail_col4:
            st.markdown("**Reported By**")
            st.info(selected_incident.get_reported_by())
        
        # Full description
        st.markdown("**Incident Description:**")
        st.text_area(
            label="Description",
            value=selected_incident.get_description(),
            height=100,
            disabled=True,
            label_visibility="collapsed"
        )
        
        # AI Analysis Section
        if ai:
            st.divider()
            st.subheader("🤖 AI-Powered Incident Analysis")
            
            col_ai_action, col_ai_button = st.columns([3, 1])
            
            with col_ai_action:
                st.markdown(f"**Generate expert analysis and recommendations for this {selected_incident.get_severity()} severity incident**")
            
            with col_ai_button:
                analyse_button = st.button(
                    "🔬 Analyse with AI",
                    use_container_width=True,
                    type="primary"
                )
            
            if analyse_button:
                with st.spinner("🤖 AI is analysing the incident... This may take a moment."):
                    # Get incident context
                    context = selected_incident.get_ai_context()
                    
                    # Get AI analysis
                    ai.set_domain("cybersecurity")
                    analysis = ai.analyse_incident(context)
                    
                    # Display analysis in expandable section
                    with st.expander("📊 Analysis Report", expanded=True):
                        st.markdown(analysis)
                    
                    # Follow-up questions section
                    st.divider()
                    st.markdown("#### 💬 Ask Follow-up Questions")
                    
                    follow_up = st.text_input(
                        "Have questions about this incident?",
                        placeholder="e.g., What MITRE ATT&CK techniques are involved? How can we prevent this in the future?",
                        key=f"followup_{selected_incident_id}"
                    )
                    
                    if follow_up:
                        with st.spinner("🤖 Generating response..."):
                            follow_up_response = ai.send_message(follow_up, context=context)
                            st.markdown("**AI Response:**")
                            st.info(follow_up_response)
        else:
            st.warning("⚠️ AI Assistant is not configured. Add your Google Gemini API key to enable AI analysis.")

else:
    st.info("📊 No incidents to display. Adjust your filters or report a new incident.")

# ========== ADD NEW INCIDENT FORM ==========
if show_add_incident:
    st.divider()
    st.subheader("➕ Report New Security Incident")
    
    with st.form("new_incident_form"):
        form_col1, form_col2, form_col3 = st.columns(3)
        
        with form_col1:
            incident_date = st.date_input("Incident Date", value=datetime.today())
            incident_type = st.selectbox(
                "Incident Type",
                options=["Phishing", "Malware", "DDoS", "Data Breach", "Ransomware", "Insider Threat", "Other"]
            )
        
        with form_col2:
            severity = st.selectbox(
                "Severity Level",
                options=["Low", "Medium", "High", "Critical"],
                index=2
            )
            status = st.selectbox(
                "Initial Status",
                options=["Open", "Investigating"],
                index=0
            )
        
        with form_col3:
            reported_by = st.text_input("Reported By", value=st.session_state.username, disabled=True)
            incident_source = st.selectbox(
                "Detection Source",
                options=["SIEM Alert", "User Report", "Security Tool", "Manual Detection", "Third Party"]
            )
        
        description = st.text_area(
            "Incident Description",
            placeholder="Provide comprehensive details about the incident including: what happened, when it was detected, affected systems, potential impact, and any immediate actions taken...",
            height=150,
            help="The more detail you provide, the better the AI analysis will be"
        )
        
        submit_col1, submit_col2 = st.columns([3, 1])
        
        with submit_col2:
            submit_button = st.form_submit_button(
                "🚀 Submit Incident",
                use_container_width=True,
                type="primary"
            )
        
        if submit_button:
            if not description or len(description) < 20:
                st.error("⚠️ Please provide a detailed description (minimum 20 characters)")
            else:
                # Insert into database
                try:
                    query = """
                    INSERT INTO cyber_incidents (date, incident_type, severity, status, description, reported_by)
                    VALUES (?, ?, ?, ?, ?, ?)
                    """
                    db.execute_query(
                        query,
                        (str(incident_date), incident_type, severity, status, description, reported_by)
                    )
                    
                    st.success(f"✅ Incident reported successfully! Reference: INC-{len(incidents)+1:04d}")
                    st.cache_data.clear()
                    st.rerun()
                except Exception as e:
                    st.error(f"❌ Error reporting incident: {e}")

# Footer
st.divider()
st.caption("🛡️ Cybersecurity Operations Center | Powered by AI-Enhanced Threat Intelligence")
st.caption(f"Session: {st.session_state.username} | {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")