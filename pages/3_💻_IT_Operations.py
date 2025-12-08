"""IT Operations Dashboard"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import os

from app.services.database_manager import DatabaseManager
from app.services.ai_assistant import GeminiClient

# Page configuration
st.set_page_config(page_title="IT Operations | Intelligence Platform", page_icon="💻", layout="wide")

#Authentication & Authorisation 
if not st.session_state.get("logged_in", False):
    st.error("🔒 Access Denied")
    st.warning("You must be logged in to view this page.")
    if st.button("Go to Login"):
        st.switch_page("Home.py")
    st.stop()

user = st.session_state.get("user_object")
if user and not user.can_access_domain('itoperations'):
    st.error("🚫 Access Denied")
    st.warning(f"Your role ({user.get_role_display_name()}) does not have permission to access the IT Operations domain.")
    if st.button("Return to Home"):
        st.switch_page("Home.py")
    st.stop()

#Service Initialisation
@st.cache_resource
def get_services():
    """Load database and AI client with caching"""
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

# --- Header--
col1, col2 = st.columns([3, 1])
with col1:
    st.title("💻 IT Operations Command Center")
with col2:
    st.markdown(f"**{st.session_state.username}**<br><small>{user.get_role_display_name()}</small>", unsafe_allow_html=True)

st.divider()

#Sidebar Filters
with st.sidebar:
    st.header("🔧 Filters")
    priority_filter = st.multiselect("Priority", ["Low", "Medium", "High", "Critical"])
    status_filter = st.multiselect("Status", ["Open", "In Progress", "Resolved", "Waiting for User"])
    
    st.divider()
    if st.button("🔄 Refresh", use_container_width=True):
        st.cache_data.clear()
        st.rerun()
    
    show_add = st.button("➕ New Ticket", use_container_width=True, type="primary")

#Load Ticket Data from CSV
@st.cache_data(ttl=60)
def load_tickets():
    """Load tickets from CSV file"""
    csv_path = "DATA/it_tickets.csv"
    if os.path.exists(csv_path):
        df = pd.read_csv(csv_path)
        # Rename columns to match expected format
        df = df.rename(columns={
            'ticket_id': 'ID',
            'priority': 'Priority',
            'description': 'Description',
            'status': 'Status',
            'assigned_to': 'Assigned',
            'created_at': 'Created',
            'resolution_time_hours': 'Resolution Hours'
        })
        return df
    return pd.DataFrame()

df = load_tickets()

# Applying sidebar filters
if not df.empty:
    df_f = df.copy()
    if priority_filter: df_f = df_f[df_f["Priority"].isin(priority_filter)]
    if status_filter: df_f = df_f[df_f["Status"].isin(status_filter)]
else:
    df_f = df

#Metrics Dashboard
st.subheader("📊 Operations Overview")
m1, m2, m3, m4, m5 = st.columns(5)

total = len(df)
active = len(df[df["Status"].isin(["Open", "In Progress"])]) if not df.empty else 0
critical = len(df[df["Priority"] == "Critical"]) if not df.empty else 0
assigned = len(df[df["Assigned"].notna()]) if not df.empty else 0
resolved = len(df[df["Status"] == "Resolved"]) if not df.empty else 0

m1.metric("Total Tickets", total)
m2.metric("Active", active)
m3.metric("Critical", critical)
m4.metric("Assigned", assigned)
m5.metric("Resolved", resolved)

st.divider()

#Visualisation Section
st.subheader("📈 Operations Analytics")

if not df_f.empty:
    # Row 1: Priority, Status, and Workload charts
    c1, c2, c3 = st.columns(3)
    
    with c1:
        # Priority distribution donut chart
        prio_counts = df_f["Priority"].value_counts()
        colors = {"Low": "#93c5fd", "Medium": "#60a5fa", "High": "#f87171", "Critical": "#dc2626"}
        fig = go.Figure(data=[go.Pie(
            labels=prio_counts.index, values=prio_counts.values, hole=0.5,
            marker_colors=[colors.get(p, "#3b82f6") for p in prio_counts.index]
        )])
        fig.update_layout(title="Priority Distribution", height=300)
        st.plotly_chart(fig, use_container_width=True)
    
    with c2:
        # Status overview bar chart
        status_counts = df_f["Status"].value_counts()
        colors_s = {"Open": "#ef4444", "In Progress": "#f59e0b", "Resolved": "#3b82f6", "Closed": "#6b7280"}
        fig = go.Figure(data=[go.Bar(
            x=status_counts.index, y=status_counts.values,
            marker_color=[colors_s.get(s, "#3b82f6") for s in status_counts.index],
            text=status_counts.values, textposition='auto'
        )])
        fig.update_layout(title="Status Overview", height=300)
        st.plotly_chart(fig, use_container_width=True)
    
    with c3:
        # Team workload gauge indicator
        workload = min(100, active * 12)  # Calculated based on active tickets.
        fig = go.Figure(go.Indicator(
            mode="gauge+number",
            value=workload,
            number={'suffix': "%"},
            gauge={
                'axis': {'range': [0, 100]},
                'bar': {'color': "#dc2626" if workload > 70 else "#f59e0b" if workload > 40 else "#3b82f6"},
                'steps': [
                    {'range': [0, 40], 'color': '#dbeafe'},
                    {'range': [40, 70], 'color': '#fef3c7'},
                    {'range': [70, 100], 'color': '#fecaca'}
                ]
            },
            title={'text': "Team Workload"}
        ))
        fig.update_layout(height=300)
        st.plotly_chart(fig, use_container_width=True)
    
    # Row 2: Assigned breakdown and timeline
    c4, c5 = st.columns(2)
    
    with c4:
        # Horizontal bar chart by assigned person
        assigned_counts = df_f["Assigned"].value_counts()
        fig = go.Figure(data=[go.Bar(
            y=assigned_counts.index, x=assigned_counts.values, orientation='h',
            marker_color='#3b82f6', text=assigned_counts.values, textposition='auto'
        )])
        fig.update_layout(title="By Assigned Staff", height=300)
        st.plotly_chart(fig, use_container_width=True)
    
    with c5:
        # Area chart showing ticket creation trend
        df_time = df_f.copy()
        df_time['Created'] = pd.to_datetime(df_time['Created'])
        daily = df_time.groupby(df_time['Created'].dt.date).size().reset_index(name='Count')
        daily.columns = ['Date', 'Count']
        fig = px.area(daily, x='Date', y='Count', title="Ticket Trend")
        fig.update_traces(fill='tozeroy', line_color='#3b82f6', fillcolor='rgba(59,130,246,0.3)')
        fig.update_layout(height=300)
        st.plotly_chart(fig, use_container_width=True)
    
    # Row 3: Cross analysis and pipeline view
    c6, c7 = st.columns(2)
    
    with c6:
        # Heatmap showing assigned vs priority correlation
        cross = pd.crosstab(df_f['Assigned'], df_f['Priority'])
        fig = px.imshow(cross, text_auto=True, color_continuous_scale='Blues', title="Staff vs Priority")
        fig.update_layout(height=300)
        st.plotly_chart(fig, use_container_width=True)
    
    with c7:
        # Funnel chart showing ticket pipeline flow
        funnel_data = df_f["Status"].value_counts()
        order = ["Open", "In Progress", "Waiting for User", "Resolved"]
        funnel_sorted = [funnel_data.get(s, 0) for s in order]
        colors_f = ['#ef4444', '#f59e0b', '#a855f7', '#3b82f6']
        fig = go.Figure(go.Funnel(y=order, x=funnel_sorted, marker_color=colors_f))
        fig.update_layout(title="Ticket Pipeline", height=300)
        st.plotly_chart(fig, use_container_width=True)

else:
    st.info("No tickets match filters")

st.divider()

#Ticket Management & AI implentation
st.subheader("🔍 Ticket Management")

if not df_f.empty:
    # Ticket selection dropdown
    selected_id = st.selectbox("Select Ticket", df_f["ID"].tolist(),
        format_func=lambda x: f"TICK-{int(x):04d} | {df_f[df_f['ID']==x]['Priority'].values[0]} | {df_f[df_f['ID']==x]['Description'].values[0][:30]}")
    
    # Data table display
    st.dataframe(df_f[['ID', 'Priority', 'Status', 'Assigned', 'Created', 'Description']], use_container_width=True, hide_index=True)
    
    # Get selected ticket details
    selected_ticket = df_f[df_f['ID'] == selected_id].iloc[0]
    
    # Ticket detail cards
    st.divider()
    d1, d2, d3, d4 = st.columns(4)
    d1.markdown(f"**Priority:** {selected_ticket['Priority']}")
    d2.markdown(f"**Status:** {selected_ticket['Status']}")
    d3.markdown(f"**Resolution Time:** {selected_ticket['Resolution Hours']}h")
    d4.markdown(f"**Assigned:** {selected_ticket['Assigned']}")
    
    # Ticket action controls
    a1, a2, a3 = st.columns(3)
    with a1:
        new_assign = st.text_input("Assign to:", key=f"assign_{selected_id}")
        if st.button("👤 Assign", key=f"btn_a_{selected_id}"):
            if new_assign:
                # Update CSV
                csv_path = "DATA/it_tickets.csv"
                update_df = pd.read_csv(csv_path)
                update_df.loc[update_df['ticket_id'] == selected_id, 'assigned_to'] = new_assign
                update_df.loc[update_df['ticket_id'] == selected_id, 'status'] = 'In Progress'
                update_df.to_csv(csv_path, index=False)
                st.success("✅ Assigned")
                st.cache_data.clear()
                st.rerun()
    
    with a2:
        new_status = st.selectbox("Status:", ["Open", "In Progress", "Resolved", "Waiting for User"], key=f"status_{selected_id}")
        if st.button("🔄 Update", key=f"btn_s_{selected_id}"):
            csv_path = "DATA/it_tickets.csv"
            update_df = pd.read_csv(csv_path)
            update_df.loc[update_df['ticket_id'] == selected_id, 'status'] = new_status
            update_df.to_csv(csv_path, index=False)
            st.success("✅ Updated")
            st.cache_data.clear()
            st.rerun()
    
    with a3:
        st.write("")
        if st.button("✅ Resolve", key=f"btn_c_{selected_id}", type="primary"):
            csv_path = "DATA/it_tickets.csv"
            update_df = pd.read_csv(csv_path)
            update_df.loc[update_df['ticket_id'] == selected_id, 'status'] = 'Resolved'
            update_df.to_csv(csv_path, index=False)
            st.success("✅ Resolved")
            st.cache_data.clear()
            st.rerun()
    
    # AI Assistant Section
    if client:
        st.divider()
        st.subheader("🤖 AI Troubleshooting")
        
        # AI analysis buttons
        b1, b2, b3 = st.columns(3)
        with b1:
            btn1 = st.button("🔬 Troubleshoot", use_container_width=True)
        with b2:
            btn2 = st.button("📊 Workload Analysis", use_container_width=True, type="primary")
        with b3:
            btn3 = st.button("📈 SLA Insights", use_container_width=True)
        
        # Individual AI analysis handlers
        if btn1:
            ticket_context = f"""
Ticket ID: {selected_ticket['ID']}
Priority: {selected_ticket['Priority']}
Status: {selected_ticket['Status']}
Assigned To: {selected_ticket['Assigned']}
Created: {selected_ticket['Created']}
Resolution Time: {selected_ticket['Resolution Hours']} hours
Description: {selected_ticket['Description']}
"""
            messages = [
                {"role": "system", "content": "You're an IT support specialist. Be concise."},
                {"role": "user", "content": f"Troubleshoot:\n{ticket_context}"}
            ]
            with st.chat_message("assistant"):
                container = st.empty()
                full = ""
                for chunk in client.chat.completions.create(model="gemini-2.0-flash", messages=messages, stream=True, domain="IT Operations"):
                    if chunk.choices[0].delta.content:
                        full += chunk.choices[0].delta.content
                        container.markdown(full + "▌")
                container.markdown(full)
        
        if btn2:
            summary = f"""IT Summary:
- Total: {total}, Active: {active}, Critical: {critical}, Assigned: {assigned}
- Staff Workload: {df_f['Assigned'].value_counts().to_dict()}
- Priorities: {df_f['Priority'].value_counts().to_dict()}
- Status: {df_f['Status'].value_counts().to_dict()}"""
            messages = [
                {"role": "system", "content": "You're an IT operations analyst."},
                {"role": "user", "content": f"Workload analysis:\n{summary}"}
            ]
            with st.chat_message("assistant"):
                container = st.empty()
                full = ""
                for chunk in client.chat.completions.create(model="gemini-2.0-flash", messages=messages, stream=True, domain="IT Operations"):
                    if chunk.choices[0].delta.content:
                        full += chunk.choices[0].delta.content
                        container.markdown(full + "▌")
                container.markdown(full)
        
        if btn3:
            avg_resolution = df_f['Resolution Hours'].mean() if not df_f.empty else 0
            messages = [
                {"role": "system", "content": "You're an IT service manager."},
                {"role": "user", "content": f"SLA recommendations for {active} active, {critical} critical tickets. Average resolution time: {avg_resolution:.1f} hours."}
            ]
            with st.chat_message("assistant"):
                container = st.empty()
                full = ""
                for chunk in client.chat.completions.create(model="gemini-2.0-flash", messages=messages, stream=True, domain="IT Operations"):
                    if chunk.choices[0].delta.content:
                        full += chunk.choices[0].delta.content
                        container.markdown(full + "▌")
                container.markdown(full)
        
        # General AI chat input
        st.divider()
        q = st.chat_input("Ask about IT...")
        if q:
            messages = [{"role": "system", "content": "You're an IT assistant. Only use IT operations ticket data from this dashboard."}, {"role": "user", "content": q}]
            with st.chat_message("user"):
                st.markdown(q)
            with st.chat_message("assistant"):
                container = st.empty()
                full = ""
                for chunk in client.chat.completions.create(model="gemini-2.0-flash", messages=messages, stream=True, domain="IT Operations"):
                    if chunk.choices[0].delta.content:
                        full += chunk.choices[0].delta.content
                        container.markdown(full + "▌")
                container.markdown(full)
    else:
        st.warning("⚠️ AI not configured")

#New Ticket Creation Form
if show_add:
    st.divider()
    st.subheader("➕ Create Ticket")
    
    with st.form("new_ticket"):
        c1, c2 = st.columns(2)
        with c1:
            new_ticket_id = df['ID'].max() + 1 if not df.empty else 2000
            ticket_num = st.text_input("Ticket #", f"TICK-{int(new_ticket_id):04d}", disabled=True)
            priority = st.selectbox("Priority", ["Low", "Medium", "High", "Critical"], index=1)
        with c2:
            status = st.selectbox("Status", ["Open", "In Progress"])
            assigned_to = st.text_input("Assign To (optional)")
        
        desc = st.text_area("Description", placeholder="Describe the issue...", height=100)
        
        if st.form_submit_button("🚀 Create", use_container_width=True, type="primary"):
            if desc and len(desc) >= 20:
                # Load existing CSV, add new row, save back
                csv_path = "DATA/it_tickets.csv"
                if os.path.exists(csv_path):
                    existing_df = pd.read_csv(csv_path)
                    new_id = existing_df['ticket_id'].max() + 1
                else:
                    existing_df = pd.DataFrame(columns=['ticket_id', 'priority', 'description', 'status', 'assigned_to', 'created_at', 'resolution_time_hours'])
                    new_id = 2000
                
                new_row = pd.DataFrame([{
                    'ticket_id': new_id,
                    'priority': priority,
                    'description': desc,
                    'status': status,
                    'assigned_to': assigned_to if assigned_to else None,
                    'created_at': f"{datetime.today().date()} 00:00:00",
                    'resolution_time_hours': 0
                }])
                updated_df = pd.concat([existing_df, new_row], ignore_index=True)
                os.makedirs("DATA", exist_ok=True)
                updated_df.to_csv(csv_path, index=False)
                st.success(f"✅ Created TICK-{int(new_id):04d}")
                st.cache_data.clear()
                st.rerun()
            else:
                st.error("Description (20+ chars) required")

# --- Footer --
st.divider()
st.caption(f"💻 IT Operations | {st.session_state.username} | {datetime.now().strftime('%H:%M:%S')}")