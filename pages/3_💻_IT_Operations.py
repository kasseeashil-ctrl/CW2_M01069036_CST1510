"""
IT Operations Domain Dashboard - Professional Edition
Comprehensive IT ticket management and infrastructure monitoring
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime

from app.services.database_manager import DatabaseManager
from app.services.ai_assistant import AIAssistant
from app.models.it_tickets import ITTicket

# Page configuration
st.set_page_config(
    page_title="IT Operations | Intelligence Platform",
    page_icon="💻",
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
if user and not user.can_access_domain('itoperations'):
    st.error(f"🚫 Access Denied: Your role ({user.get_role_display_name()}) does not have permission to access the IT Operations domain.")
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
    st.title("💻 IT Operations Command Center")
    st.caption("Ticket Management & Infrastructure Support")

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
    priority_filter = st.multiselect(
        "Priority Level",
        options=["Low", "Medium", "High", "Critical"],
        default=[]
    )
    
    status_filter = st.multiselect(
        "Status",
        options=["Open", "In Progress", "Resolved", "Closed"],
        default=[]
    )
    
    category_filter = st.multiselect(
        "Category",
        options=["Hardware", "Software", "Network", "Security", "Access", "Other"],
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
    show_create_ticket = st.button("➕ Create New Ticket", use_container_width=True, type="primary")
    
    if st.button("📊 SLA Report", use_container_width=True):
        st.info("SLA reporting feature coming soon!")

# Fetch tickets from database
@st.cache_data(ttl=60)
def load_tickets():
    """Load all tickets from database as ITTicket objects."""
    query = """
    SELECT id, ticket_id, priority, status, category, subject, description,
           created_date, resolved_date, assigned_to
    FROM it_tickets
    ORDER BY created_date DESC, id DESC
    """
    rows = db.fetch_all(query)
    
    tickets = []
    for row in rows:
        ticket = ITTicket(
            ticket_id=row[0],
            ticket_number=row[1],
            priority=row[2],
            status=row[3],
            category=row[4],
            subject=row[5],
            description=row[6],
            created_date=row[7],
            resolved_date=row[8],
            assigned_to=row[9]
        )
        tickets.append(ticket)
    
    return tickets

tickets = load_tickets()

# Convert to DataFrame
def tickets_to_dataframe(tickets_list):
    """Convert list of ITTicket objects to pandas DataFrame."""
    data = []
    for ticket in tickets_list:
        data.append({
            "ID": ticket.get_id(),
            "Ticket #": ticket.get_ticket_number(),
            "Priority": ticket.get_priority(),
            "Status": ticket.get_status(),
            "Category": ticket.get_category(),
            "Subject": ticket.get_subject(),
            "Description": ticket.get_description(),
            "Created": ticket.get_created_date(),
            "Resolved": ticket.get_resolved_date(),
            "Assigned To": ticket.get_assigned_to(),
            "Priority_Level": ticket.get_priority_level()
        })
    return pd.DataFrame(data)

df = tickets_to_dataframe(tickets)

# Apply filters
if not df.empty:
    df_filtered = df.copy()
    
    # Priority filter
    if priority_filter:
        df_filtered = df_filtered[df_filtered["Priority"].isin(priority_filter)]
    
    # Status filter
    if status_filter:
        df_filtered = df_filtered[df_filtered["Status"].isin(status_filter)]
    
    # Category filter
    if category_filter:
        df_filtered = df_filtered[df_filtered["Category"].isin(category_filter)]
else:
    df_filtered = df

# ========== KEY METRICS ROW ==========
st.subheader("📊 Operations Overview")

metric_col1, metric_col2, metric_col3, metric_col4, metric_col5 = st.columns(5)

with metric_col1:
    total_tickets = len(tickets)
    st.metric(
        "Total Tickets",
        total_tickets,
        help="All recorded support tickets"
    )

with metric_col2:
    open_tickets = len([t for t in tickets if t.is_open()])
    st.metric(
        "Active Tickets",
        open_tickets,
        delta=f"+{open_tickets}" if open_tickets > 0 else "0",
        delta_color="inverse",
        help="Currently open or in progress"
    )

with metric_col3:
    critical_tickets = len([t for t in tickets if t.is_critical()])
    st.metric(
        "Critical Issues",
        critical_tickets,
        delta="Urgent" if critical_tickets > 0 else "None",
        delta_color="inverse",
        help="High priority tickets requiring immediate attention"
    )

with metric_col4:
    unassigned_tickets = len([t for t in tickets if not t.is_assigned()])
    st.metric(
        "Unassigned",
        unassigned_tickets,
        help="Tickets awaiting assignment"
    )

with metric_col5:
    if total_tickets > 0:
        resolution_rate = ((total_tickets - open_tickets) / total_tickets) * 100
        st.metric(
            "Resolution Rate",
            f"{resolution_rate:.1f}%",
            help="Percentage of resolved tickets"
        )
    else:
        st.metric("Resolution Rate", "N/A")

st.divider()

# ========== ADVANCED VISUALIZATIONS ==========
st.subheader("📈 IT Operations Analytics")

if not df_filtered.empty:
    
    # Row 1: Main Charts
    chart_col1, chart_col2 = st.columns(2)
    
    with chart_col1:
        st.markdown("**🎫 Ticket Distribution by Category**")
        category_counts = df_filtered["Category"].value_counts()
        
        fig_categories = px.pie(
            values=category_counts.values,
            names=category_counts.index,
            hole=0.4,
            color_discrete_sequence=px.colors.qualitative.Set3
        )
        fig_categories.update_traces(
            textposition='inside',
            textinfo='percent+label',
            hovertemplate='<b>%{label}</b><br>Count: %{value}<br>Percentage: %{percent}<extra></extra>'
        )
        fig_categories.update_layout(
            showlegend=True,
            legend=dict(orientation="v", yanchor="middle", y=0.5, xanchor="left", x=1.02),
            height=400
        )
        st.plotly_chart(fig_categories, use_container_width=True)
    
    with chart_col2:
        st.markdown("**⚠️ Priority Level Distribution**")
        priority_counts = df_filtered["Priority"].value_counts()
        
        # Priority color mapping
        color_map = {
            "Low": "#90EE90",
            "Medium": "#FFD700",
            "High": "#FFA500",
            "Critical": "#FF4500"
        }
        colors = [color_map.get(p, "#CCCCCC") for p in priority_counts.index]
        
        fig_priority = go.Figure(data=[
            go.Bar(
                x=priority_counts.index,
                y=priority_counts.values,
                marker_color=colors,
                text=priority_counts.values,
                textposition='auto',
                hovertemplate='<b>%{x}</b><br>Count: %{y}<extra></extra>'
            )
        ])
        fig_priority.update_layout(
            xaxis_title="Priority Level",
            yaxis_title="Number of Tickets",
            showlegend=False,
            height=400
        )
        st.plotly_chart(fig_priority, use_container_width=True)
    
    # Row 2: Status and Timeline
    chart_col3, chart_col4 = st.columns(2)
    
    with chart_col3:
        st.markdown("**🔄 Current Status Overview**")
        status_counts = df_filtered["Status"].value_counts()
        
        # Status color mapping
        status_colors = {
            "Open": "#FF6B6B",
            "In Progress": "#FFA500",
            "Resolved": "#4ECDC4",
            "Closed": "#95E1D3"
        }
        
        fig_status = px.bar(
            x=status_counts.index,
            y=status_counts.values,
            color=status_counts.index,
            color_discrete_map=status_colors
        )
        fig_status.update_traces(
            hovertemplate='<b>%{x}</b><br>Count: %{y}<extra></extra>'
        )
        fig_status.update_layout(
            xaxis_title="Status",
            yaxis_title="Count",
            showlegend=False,
            height=400
        )
        st.plotly_chart(fig_status, use_container_width=True)
    
    with chart_col4:
        st.markdown("**📅 Ticket Creation Timeline**")
        
        if 'Created' not in df_filtered.columns or df_filtered.empty:
            st.info("No timeline data available")
        else:
            df_timeline = df_filtered.copy()
            df_timeline['Created'] = pd.to_datetime(df_timeline['Created'])
            
            # Group by date
            timeline_data = df_timeline.groupby('Created').size().reset_index(name='Count')
            
            fig_timeline = px.line(
                timeline_data,
                x='Created',
                y='Count',
                markers=True,
                line_shape='spline'
            )
            fig_timeline.update_traces(
                line_color='#0EA5E9',
                marker=dict(size=8, color='#0EA5E9'),
                hovertemplate='<b>%{x|%Y-%m-%d}</b><br>Tickets: %{y}<extra></extra>'
            )
            fig_timeline.update_layout(
                xaxis_title="Date",
                yaxis_title="Number of Tickets",
                hovermode='x unified',
                height=400
            )
            st.plotly_chart(fig_timeline, use_container_width=True)
    
    # Row 3: Advanced Analytics
    st.markdown("**🔍 Advanced Operations Analytics**")
    
    analysis_col1, analysis_col2, analysis_col3 = st.columns(3)
    
    with analysis_col1:
        st.markdown("**Top 5 Categories by Volume**")
        top_categories = df_filtered["Category"].value_counts().head(5)
        
        fig_top_cat = go.Figure(data=[
            go.Bar(
                y=top_categories.index[::-1],
                x=top_categories.values[::-1],
                orientation='h',
                marker_color='#10B981',
                text=top_categories.values[::-1],
                textposition='auto',
                hovertemplate='<b>%{y}</b><br>Count: %{x}<extra></extra>'
            )
        ])
        fig_top_cat.update_layout(
            xaxis_title="Count",
            yaxis_title="",
            height=300,
            margin=dict(l=120)
        )
        st.plotly_chart(fig_top_cat, use_container_width=True)
    
    with analysis_col2:
        st.markdown("**Priority vs Status Matrix**")
        
        # Create cross-tabulation
        priority_status = pd.crosstab(df_filtered['Priority'], df_filtered['Status'])
        
        fig_heatmap = go.Figure(data=go.Heatmap(
            z=priority_status.values,
            x=priority_status.columns,
            y=priority_status.index,
            colorscale='Teal',
            text=priority_status.values,
            texttemplate='%{text}',
            textfont={"size": 12},
            hovertemplate='Priority: %{y}<br>Status: %{x}<br>Count: %{z}<extra></extra>'
        ))
        fig_heatmap.update_layout(
            xaxis_title="Status",
            yaxis_title="Priority",
            height=300
        )
        st.plotly_chart(fig_heatmap, use_container_width=True)
    
    with analysis_col3:
        st.markdown("**Assignment Distribution**")
        
        assigned_tickets = df_filtered[df_filtered['Assigned To'] != 'Unassigned']
        if not assigned_tickets.empty:
            assignee_counts = assigned_tickets['Assigned To'].value_counts().head(5)
            
            fig_assignees = px.pie(
                values=assignee_counts.values,
                names=assignee_counts.index,
                color_discrete_sequence=px.colors.qualitative.Pastel
            )
            fig_assignees.update_traces(
                textposition='inside',
                textinfo='label+percent',
                hovertemplate='<b>%{label}</b><br>Tickets: %{value}<extra></extra>'
            )
            fig_assignees.update_layout(height=300)
            st.plotly_chart(fig_assignees, use_container_width=True)
        else:
            st.info("No assigned tickets to display")

else:
    st.info("📊 No tickets match the selected filters. Adjust your filters or create a new ticket.")

st.divider()

# ========== TICKETS DATA TABLE ==========
st.subheader("🔍 Ticket Management")

if not df_filtered.empty:
    # Display count and filters summary
    filter_summary = f"Showing **{len(df_filtered)}** of **{len(df)}** tickets"
    if priority_filter:
        filter_summary += f" | Priority: {', '.join(priority_filter)}"
    if status_filter:
        filter_summary += f" | Status: {', '.join(status_filter)}"
    
    st.caption(filter_summary)
    
    # Ticket selection
    selected_ticket_id = st.selectbox(
        "Select a ticket to view details:",
        options=df_filtered["ID"].tolist(),
        format_func=lambda x: f"{df_filtered[df_filtered['ID']==x]['Ticket #'].values[0]} | {df_filtered[df_filtered['ID']==x]['Subject'].values[0]} | {df_filtered[df_filtered['ID']==x]['Priority'].values[0]}"
    )
    
    # Display full ticket table
    display_df = df_filtered.drop(columns=['Priority_Level']).copy()
    
    st.dataframe(
        display_df,
        use_container_width=True,
        hide_index=True,
        column_config={
            "ID": st.column_config.NumberColumn("ID", width="small"),
            "Ticket #": st.column_config.TextColumn("Ticket #", width="small"),
            "Priority": st.column_config.TextColumn("Priority", width="small"),
            "Status": st.column_config.TextColumn("Status", width="small"),
            "Category": st.column_config.TextColumn("Category", width="medium"),
            "Subject": st.column_config.TextColumn("Subject", width="large"),
            "Created": st.column_config.DateColumn("Created", width="small"),
            "Resolved": st.column_config.TextColumn("Resolved", width="small"),
            "Assigned To": st.column_config.TextColumn("Assigned", width="small")
        }
    )
    
    # ========== TICKET DETAILS & MANAGEMENT ==========
    if selected_ticket_id:
        st.divider()
        
        # Get selected ticket object
        selected_ticket = next(t for t in tickets if t.get_id() == selected_ticket_id)
        
        # Display detailed ticket information
        st.subheader(f"📋 Ticket Details: {selected_ticket.get_ticket_number()}")
        
        detail_col1, detail_col2, detail_col3, detail_col4 = st.columns(4)
        
        with detail_col1:
            priority = selected_ticket.get_priority()
            priority_emoji = {"Low": "🟢", "Medium": "🟡", "High": "🟠", "Critical": "🔴"}
            st.markdown("**Priority**")
            st.warning(f"{priority_emoji.get(priority, '⚪')} {priority}")
        
        with detail_col2:
            st.markdown("**Status**")
            st.info(selected_ticket.get_status())
        
        with detail_col3:
            st.markdown("**Category**")
            st.info(selected_ticket.get_category())
        
        with detail_col4:
            st.markdown("**Assigned To**")
            assigned = selected_ticket.get_assigned_to()
            if assigned == "Unassigned":
                st.error("❌ " + assigned)
            else:
                st.success("✅ " + assigned)
        
        # Dates
        date_col1, date_col2 = st.columns(2)
        with date_col1:
            st.markdown(f"**Created:** {selected_ticket.get_created_date()}")
        with date_col2:
            resolved = selected_ticket.get_resolved_date()
            if resolved == "Not resolved":
                st.markdown(f"**Resolved:** ⏳ {resolved}")
            else:
                st.markdown(f"**Resolved:** ✅ {resolved}")
        
        # Subject and Description
        st.markdown("**Subject:**")
        st.text_input(label="Subject", value=selected_ticket.get_subject(), disabled=True, label_visibility="collapsed")
        
        st.markdown("**Description:**")
        st.text_area(
            label="Description",
            value=selected_ticket.get_description(),
            height=100,
            disabled=True,
            label_visibility="collapsed"
        )
        
        # Ticket Management Actions
        st.divider()
        st.markdown("### 🛠️ Ticket Management")
        
        action_col1, action_col2, action_col3 = st.columns(3)
        
        with action_col1:
            st.markdown("**Assign Ticket**")
            new_assignee = st.text_input("Assignee", placeholder="Enter username", key=f"assign_{selected_ticket_id}")
            if st.button("👤 Assign", use_container_width=True, key=f"btn_assign_{selected_ticket_id}"):
                if new_assignee:
                    try:
                        query = "UPDATE it_tickets SET assigned_to = ?, status = 'In Progress' WHERE id = ?"
                        db.execute_query(query, (new_assignee, selected_ticket_id))
                        st.success(f"✅ Assigned to {new_assignee}")
                        st.cache_data.clear()
                        st.rerun()
                    except Exception as e:
                        st.error(f"❌ Error: {e}")
                else:
                    st.warning("⚠️ Please enter a username")
        
        with action_col2:
            st.markdown("**Update Status**")
            new_status = st.selectbox(
                "New Status",
                ["Open", "In Progress", "Resolved", "Closed"],
                key=f"status_{selected_ticket_id}"
            )
            if st.button("🔄 Update", use_container_width=True, key=f"btn_status_{selected_ticket_id}"):
                try:
                    resolved_date = str(datetime.today().date()) if new_status in ["Resolved", "Closed"] else None
                    query = "UPDATE it_tickets SET status = ?, resolved_date = ? WHERE id = ?"
                    db.execute_query(query, (new_status, resolved_date, selected_ticket_id))
                    st.success(f"✅ Status updated to {new_status}")
                    st.cache_data.clear()
                    st.rerun()
                except Exception as e:
                    st.error(f"❌ Error: {e}")
        
        with action_col3:
            st.markdown("**Quick Actions**")
            if st.button("✅ Resolve & Close", use_container_width=True, type="primary", key=f"btn_close_{selected_ticket_id}"):
                try:
                    query = "UPDATE it_tickets SET status = 'Closed', resolved_date = ? WHERE id = ?"
                    db.execute_query(query, (str(datetime.today().date()), selected_ticket_id))
                    st.success("✅ Ticket closed successfully")
                    st.cache_data.clear()
                    st.rerun()
                except Exception as e:
                    st.error(f"❌ Error: {e}")
        
        # AI Troubleshooting Section
        if ai:
            st.divider()
            st.subheader("🤖 AI-Powered Troubleshooting")
            
            col_ai_action, col_ai_button = st.columns([3, 1])
            
            with col_ai_action:
                st.markdown(f"**Get expert troubleshooting guidance for this {selected_ticket.get_priority()} priority ticket**")
            
            with col_ai_button:
                analyse_button = st.button(
                    "🔬 Get AI Solution",
                    use_container_width=True,
                    type="primary",
                    key=f"ai_{selected_ticket_id}"
                )
            
            if analyse_button:
                with st.spinner("🤖 AI is analysing the ticket... This may take a moment."):
                    # Get ticket context
                    context = selected_ticket.get_ai_context()
                    
                    # Get AI analysis
                    ai.set_domain("itoperations")
                    analysis = ai.analyse_ticket(context)
                    
                    # Display analysis
                    with st.expander("📊 Troubleshooting Guide", expanded=True):
                        st.markdown(analysis)
                    
                    # Follow-up questions
                    st.divider()
                    st.markdown("#### 💬 Ask Follow-up Questions")
                    
                    follow_up = st.text_input(
                        "Need more help with this ticket?",
                        placeholder="e.g., How do I prevent this issue? What are the root causes?",
                        key=f"followup_ticket_{selected_ticket_id}"
                    )
                    
                    if follow_up:
                        with st.spinner("🤖 Generating response..."):
                            follow_up_response = ai.send_message(follow_up, context=context)
                            st.markdown("**AI Response:**")
                            st.info(follow_up_response)
        else:
            st.warning("⚠️ AI Assistant is not configured. Add your Google Gemini API key to enable AI troubleshooting.")

else:
    st.info("📊 No tickets to display. Adjust your filters or create a new ticket.")

# ========== CREATE NEW TICKET FORM ==========
if show_create_ticket:
    st.divider()
    st.subheader("➕ Create New Support Ticket")
    
    with st.form("new_ticket_form"):
        form_col1, form_col2, form_col3 = st.columns(3)
        
        with form_col1:
            ticket_number = st.text_input("Ticket Number", value=f"TICK-{len(tickets)+1:04d}", disabled=True)
            priority = st.selectbox(
                "Priority",
                options=["Low", "Medium", "High", "Critical"],
                index=1
            )
        
        with form_col2:
            category = st.selectbox(
                "Category",
                options=["Hardware", "Software", "Network", "Security", "Access", "Other"]
            )
            status = st.selectbox("Initial Status", ["Open", "In Progress"], index=0)
        
        with form_col3:
            assigned_to = st.text_input("Assign To (optional)", placeholder="Leave empty for unassigned")
            created_date = st.date_input("Created Date", value=datetime.today())
        
        subject = st.text_input("Subject", placeholder="Brief summary of the issue")
        description = st.text_area(
            "Description",
            placeholder="Detailed description of the problem, including steps to reproduce, affected systems, error messages, etc.",
            height=150
        )
        
        submit_col1, submit_col2 = st.columns([3, 1])
        
        with submit_col2:
            submit_button = st.form_submit_button("🚀 Create Ticket", use_container_width=True, type="primary")
        
        if submit_button:
            if not subject or not description:
                st.error("⚠️ Please provide both subject and description")
            elif len(description) < 20:
                st.error("⚠️ Please provide a detailed description (minimum 20 characters)")
            else:
                # Insert into database
                try:
                    query = """
                    INSERT INTO it_tickets (ticket_id, priority, status, category, subject, description, created_date, assigned_to)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                    """
                    db.execute_query(
                        query,
                        (ticket_number, priority, status, category, subject, description, str(created_date), assigned_to or None)
                    )
                    
                    st.success(f"✅ Ticket created successfully! Reference: {ticket_number}")
                    st.cache_data.clear()
                    st.rerun()
                except Exception as e:
                    st.error(f"❌ Error creating ticket: {e}")

# Footer
st.divider()
st.caption("💻 IT Operations Command Center | Infrastructure Support & Management Platform")
st.caption(f"Session: {st.session_state.username} | {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")