"""
Data Science Domain Dashboard - Professional Edition
Comprehensive dataset analytics and management
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime

from app.services.database_manager import DatabaseManager
from app.services.ai_assistant import AIAssistant
from app.models.dataset import Dataset

# Page configuration
st.set_page_config(
    page_title="Data Science | Intelligence Platform",
    page_icon="📊",
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
if user and not user.can_access_domain('datascience'):
    st.error(f"🚫 Access Denied: Your role ({user.get_role_display_name()}) does not have permission to access the Data Science domain.")
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
    st.title("📊 Data Science Analytics Center")
    st.caption("Dataset Management & Advanced Analytics")

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
    category_filter = st.multiselect(
        "Dataset Category",
        options=["Threat Intelligence", "Network Logs", "User Behaviour", "System Metrics", "Security Alerts", "Other"],
        default=[]
    )
    
    st.subheader("📏 Size Filters")
    size_range = st.slider(
        "File Size (MB)",
        min_value=0,
        max_value=1000,
        value=(0, 1000),
        step=10
    )
    
    st.subheader("📊 Record Filters")
    record_range = st.slider(
        "Record Count (thousands)",
        min_value=0,
        max_value=5000,
        value=(0, 5000),
        step=100
    )
    
    st.divider()
    
    # Refresh controls
    if st.button("🔄 Refresh Data", use_container_width=True):
        st.cache_data.clear()
        st.rerun()
    
    st.divider()
    
    # Quick actions
    st.subheader("⚡ Quick Actions")
    show_add_dataset = st.button("➕ Register New Dataset", use_container_width=True, type="primary")
    
    if st.button("📈 Export Analytics", use_container_width=True):
        st.info("Export feature coming soon!")

# Fetch datasets from database
@st.cache_data(ttl=60)
def load_datasets():
    """Load all datasets from database as Dataset objects."""
    query = """
    SELECT id, dataset_name, category, source, last_updated, record_count, file_size_mb
    FROM datasets_metadata
    ORDER BY id DESC
    """
    rows = db.fetch_all(query)
    
    datasets = []
    for row in rows:
        dataset = Dataset(
            dataset_id=row[0],
            name=row[1],
            category=row[2],
            source=row[3],
            last_updated=row[4],
            record_count=row[5],
            file_size_mb=row[6]
        )
        datasets.append(dataset)
    
    return datasets

datasets = load_datasets()

# Convert to DataFrame
def datasets_to_dataframe(datasets_list):
    """Convert list of Dataset objects to pandas DataFrame."""
    data = []
    for ds in datasets_list:
        data.append({
            "ID": ds.get_id(),
            "Name": ds.get_name(),
            "Category": ds.get_category(),
            "Source": ds.get_source(),
            "Last Updated": ds.get_last_updated(),
            "Records": ds.get_record_count(),
            "Size (MB)": ds.get_file_size_mb(),
            "Size (GB)": ds.calculate_size_gb(),
            "Density": ds.get_records_per_mb(),
            "Is Large": ds.is_large_dataset()
        })
    return pd.DataFrame(data)

df = datasets_to_dataframe(datasets)

# Apply filters
if not df.empty:
    df_filtered = df.copy()
    
    # Category filter
    if category_filter:
        df_filtered = df_filtered[df_filtered["Category"].isin(category_filter)]
    
    # Size filter
    df_filtered = df_filtered[
        (df_filtered["Size (MB)"] >= size_range[0]) &
        (df_filtered["Size (MB)"] <= size_range[1])
    ]
    
    # Record count filter
    df_filtered = df_filtered[
        (df_filtered["Records"] >= record_range[0] * 1000) &
        (df_filtered["Records"] <= record_range[1] * 1000)
    ]
else:
    df_filtered = df

# ========== KEY METRICS ROW ==========
st.subheader("📊 Dataset Overview")

metric_col1, metric_col2, metric_col3, metric_col4, metric_col5 = st.columns(5)

with metric_col1:
    total_datasets = len(datasets)
    st.metric(
        "Total Datasets",
        total_datasets,
        help="All registered datasets"
    )

with metric_col2:
    if not df.empty:
        total_records = df["Records"].sum()
        st.metric(
            "Total Records",
            f"{total_records / 1_000_000:.2f}M",
            help="Sum of all records across datasets"
        )
    else:
        st.metric("Total Records", "0")

with metric_col3:
    if not df.empty:
        total_size = df["Size (MB)"].sum()
        total_size_gb = total_size / 1024
        st.metric(
            "Total Storage",
            f"{total_size_gb:.2f} GB",
            help="Total storage used by all datasets"
        )
    else:
        st.metric("Total Storage", "0 GB")

with metric_col4:
    large_datasets = len([ds for ds in datasets if ds.is_large_dataset()])
    st.metric(
        "Large Datasets",
        large_datasets,
        help="Datasets over 100 MB"
    )

with metric_col5:
    if not df.empty:
        avg_density = df["Density"].mean()
        st.metric(
            "Avg. Density",
            f"{avg_density:.1f} rec/MB",
            help="Average records per MB"
        )
    else:
        st.metric("Avg. Density", "N/A")

st.divider()

# ========== ADVANCED VISUALIZATIONS ==========
st.subheader("📈 Data Analytics Dashboard")

if not df_filtered.empty:
    
    # Row 1: Distribution Charts
    chart_col1, chart_col2 = st.columns(2)
    
    with chart_col1:
        st.markdown("**📁 Dataset Distribution by Category**")
        category_counts = df_filtered["Category"].value_counts()
        
        fig_categories = px.bar(
            x=category_counts.index,
            y=category_counts.values,
            labels={"x": "Category", "y": "Number of Datasets"},
            color=category_counts.values,
            color_continuous_scale="Blues"
        )
        fig_categories.update_traces(
            hovertemplate='<b>%{x}</b><br>Datasets: %{y}<extra></extra>'
        )
        fig_categories.update_layout(showlegend=False, height=400)
        st.plotly_chart(fig_categories, use_container_width=True)
    
    with chart_col2:
        st.markdown("**💾 Storage Distribution**")
        storage_by_category = df_filtered.groupby("Category")["Size (MB)"].sum().sort_values(ascending=False)
        
        fig_storage = px.pie(
            values=storage_by_category.values,
            names=storage_by_category.index,
            hole=0.4,
            color_discrete_sequence=px.colors.qualitative.Pastel
        )
        fig_storage.update_traces(
            textposition='inside',
            textinfo='percent+label',
            hovertemplate='<b>%{label}</b><br>Storage: %{value:.2f} MB<br>Percentage: %{percent}<extra></extra>'
        )
        fig_storage.update_layout(height=400)
        st.plotly_chart(fig_storage, use_container_width=True)
    
    # Row 2: Scatter and Tree Map
    chart_col3, chart_col4 = st.columns(2)
    
    with chart_col3:
        st.markdown("**🔍 Dataset Size vs Record Count Analysis**")
        
        fig_scatter = px.scatter(
            df_filtered,
            x="Records",
            y="Size (MB)",
            size="Records",
            color="Category",
            hover_name="Name",
            hover_data=["Source", "Last Updated", "Density"],
            size_max=50,
            color_discrete_sequence=px.colors.qualitative.Set2
        )
        fig_scatter.update_traces(
            hovertemplate='<b>%{hovertext}</b><br>Records: %{x:,}<br>Size: %{y:.2f} MB<extra></extra>'
        )
        fig_scatter.update_layout(
            xaxis_title="Number of Records",
            yaxis_title="File Size (MB)",
            height=400
        )
        st.plotly_chart(fig_scatter, use_container_width=True)
    
    with chart_col4:
        st.markdown("**🗂️ Dataset Hierarchy View**")
        
        fig_treemap = px.treemap(
            df_filtered,
            path=['Category', 'Name'],
            values='Size (MB)',
            color='Records',
            color_continuous_scale='Viridis',
            hover_data=['Records', 'Source']
        )
        fig_treemap.update_traces(
            hovertemplate='<b>%{label}</b><br>Size: %{value:.2f} MB<br>Records: %{customdata[0]:,}<extra></extra>'
        )
        fig_treemap.update_layout(height=400)
        st.plotly_chart(fig_treemap, use_container_width=True)
    
    # Row 3: Advanced Analytics
    st.markdown("**🔬 Advanced Dataset Analytics**")
    
    analysis_col1, analysis_col2, analysis_col3 = st.columns(3)
    
    with analysis_col1:
        st.markdown("**Top 5 Largest Datasets**")
        top_datasets = df_filtered.nlargest(5, 'Size (MB)')
        
        fig_top_size = go.Figure(data=[
            go.Bar(
                y=top_datasets['Name'][::-1],
                x=top_datasets['Size (MB)'][::-1],
                orientation='h',
                marker_color='#10B981',
                text=[f"{size:.1f} MB" for size in top_datasets['Size (MB)'][::-1]],
                textposition='auto',
                hovertemplate='<b>%{y}</b><br>Size: %{x:.2f} MB<extra></extra>'
            )
        ])
        fig_top_size.update_layout(
            xaxis_title="Size (MB)",
            yaxis_title="",
            height=300,
            margin=dict(l=150)
        )
        st.plotly_chart(fig_top_size, use_container_width=True)
    
    with analysis_col2:
        st.markdown("**Data Source Distribution**")
        source_counts = df_filtered['Source'].value_counts()
        
        fig_sources = px.pie(
            values=source_counts.values,
            names=source_counts.index,
            color_discrete_sequence=px.colors.qualitative.Safe
        )
        fig_sources.update_traces(
            textposition='inside',
            textinfo='label+percent',
            hovertemplate='<b>%{label}</b><br>Count: %{value}<extra></extra>'
        )
        fig_sources.update_layout(height=300)
        st.plotly_chart(fig_sources, use_container_width=True)
    
    with analysis_col3:
        st.markdown("**Dataset Efficiency (Records/MB)**")
        top_density = df_filtered.nlargest(5, 'Density')
        
        fig_density = px.bar(
            x=top_density['Density'],
            y=top_density['Name'],
            orientation='h',
            color=top_density['Density'],
            color_continuous_scale='Teal'
        )
        fig_density.update_traces(
            hovertemplate='<b>%{y}</b><br>Density: %{x:.2f} rec/MB<extra></extra>'
        )
        fig_density.update_layout(
            xaxis_title="Records per MB",
            yaxis_title="",
            showlegend=False,
            height=300,
            margin=dict(l=150)
        )
        st.plotly_chart(fig_density, use_container_width=True)
    
    # Row 4: Time Series (if applicable)
    st.markdown("**📅 Dataset Updates Timeline**")
    
    df_timeline = df_filtered.copy()
    df_timeline['Last Updated'] = pd.to_datetime(df_timeline['Last Updated'])
    timeline_data = df_timeline.groupby('Last Updated').size().reset_index(name='Count')
    
    fig_timeline = px.line(
        timeline_data,
        x='Last Updated',
        y='Count',
        markers=True,
        line_shape='spline'
    )
    fig_timeline.update_traces(
        line_color='#0EA5E9',
        marker=dict(size=10, color='#0EA5E9'),
        hovertemplate='<b>%{x|%Y-%m-%d}</b><br>Updates: %{y}<extra></extra>'
    )
    fig_timeline.update_layout(
        xaxis_title="Date",
        yaxis_title="Number of Updates",
        hovermode='x unified',
        height=300
    )
    st.plotly_chart(fig_timeline, use_container_width=True)

else:
    st.info("📊 No datasets match the selected filters. Adjust your filters or register a new dataset.")

st.divider()

# ========== DATASETS DATA TABLE ==========
st.subheader("🔍 Dataset Management")

if not df_filtered.empty:
    # Display count and filters summary
    filter_summary = f"Showing **{len(df_filtered)}** of **{len(df)}** datasets"
    if category_filter:
        filter_summary += f" | Categories: {', '.join(category_filter)}"
    
    st.caption(filter_summary)
    
    # Dataset selection
    selected_dataset_id = st.selectbox(
        "Select a dataset to view details:",
        options=df_filtered["ID"].tolist(),
        format_func=lambda x: f"DS-{x:04d} | {df_filtered[df_filtered['ID']==x]['Name'].values[0]} | {df_filtered[df_filtered['ID']==x]['Category'].values[0]}"
    )
    
    # Display full dataset table
    display_df = df_filtered.drop(columns=['Is Large']).copy()
    
    st.dataframe(
        display_df,
        use_container_width=True,
        hide_index=True,
        column_config={
            "ID": st.column_config.NumberColumn("Dataset ID", width="small", format="DS-%04d"),
            "Name": st.column_config.TextColumn("Dataset Name", width="large"),
            "Category": st.column_config.TextColumn("Category", width="medium"),
            "Source": st.column_config.TextColumn("Source", width="medium"),
            "Last Updated": st.column_config.DateColumn("Last Updated", width="small"),
            "Records": st.column_config.NumberColumn("Records", format="%d"),
            "Size (MB)": st.column_config.NumberColumn("Size (MB)", format="%.2f"),
            "Size (GB)": st.column_config.NumberColumn("Size (GB)", format="%.3f"),
            "Density": st.column_config.NumberColumn("Density", format="%.2f", help="Records per MB")
        }
    )
    
    # ========== DATASET DETAILS & AI ANALYSIS ==========
    if selected_dataset_id:
        st.divider()
        
        # Get selected dataset object
        selected_dataset = next(ds for ds in datasets if ds.get_id() == selected_dataset_id)
        
        # Display detailed dataset information
        st.subheader(f"📋 Dataset Profile: DS-{selected_dataset_id:04d}")
        
        detail_col1, detail_col2, detail_col3, detail_col4 = st.columns(4)
        
        with detail_col1:
            st.markdown("**Dataset Name**")
            st.info(selected_dataset.get_name())
        
        with detail_col2:
            st.markdown("**Category**")
            st.info(selected_dataset.get_category())
        
        with detail_col3:
            st.markdown("**Data Source**")
            st.info(selected_dataset.get_source())
        
        with detail_col4:
            size_status = "🔴 Large" if selected_dataset.is_large_dataset() else "🟢 Standard"
            st.markdown("**Size Status**")
            st.warning(size_status)
        
        # Detailed metrics
        metric_detail_col1, metric_detail_col2, metric_detail_col3, metric_detail_col4 = st.columns(4)
        
        with metric_detail_col1:
            st.metric("Total Records", f"{selected_dataset.get_record_count():,}")
        
        with metric_detail_col2:
            st.metric("File Size", f"{selected_dataset.get_file_size_mb():.2f} MB")
        
        with metric_detail_col3:
            st.metric("Size (GB)", f"{selected_dataset.calculate_size_gb()} GB")
        
        with metric_detail_col4:
            st.metric("Density", f"{selected_dataset.get_records_per_mb():.2f} rec/MB")
        
        # Last updated
        st.markdown("**Last Updated:** " + selected_dataset.get_last_updated())
        
        # AI Analysis Section
        if ai:
            st.divider()
            st.subheader("🤖 AI-Powered Dataset Analysis")
            
            col_ai_action, col_ai_button = st.columns([3, 1])
            
            with col_ai_action:
                st.markdown(f"**Generate comprehensive analysis and recommendations for this dataset**")
            
            with col_ai_button:
                analyse_button = st.button(
                    "🔬 Analyse with AI",
                    use_container_width=True,
                    type="primary"
                )
            
            if analyse_button:
                with st.spinner("🤖 AI is analysing the dataset... This may take a moment."):
                    # Get dataset context
                    context = selected_dataset.get_ai_context()
                    
                    # Get AI analysis
                    ai.set_domain("datascience")
                    analysis = ai.analyse_dataset(context)
                    
                    # Display analysis
                    with st.expander("📊 Analysis Report", expanded=True):
                        st.markdown(analysis)
                    
                    # Follow-up questions
                    st.divider()
                    st.markdown("#### 💬 Ask Follow-up Questions")
                    
                    follow_up = st.text_input(
                        "Have questions about this dataset?",
                        placeholder="e.g., What machine learning models would work best? How should I handle missing data?",
                        key=f"followup_ds_{selected_dataset_id}"
                    )
                    
                    if follow_up:
                        with st.spinner("🤖 Generating response..."):
                            follow_up_response = ai.send_message(follow_up, context=context)
                            st.markdown("**AI Response:**")
                            st.info(follow_up_response)
        else:
            st.warning("⚠️ AI Assistant is not configured. Add your Google Gemini API key to enable AI analysis.")

else:
    st.info("📊 No datasets to display. Adjust your filters or register a new dataset.")

# ========== ADD NEW DATASET FORM ==========
if show_add_dataset:
    st.divider()
    st.subheader("➕ Register New Dataset")
    
    with st.form("new_dataset_form"):
        form_col1, form_col2, form_col3 = st.columns(3)
        
        with form_col1:
            dataset_name = st.text_input(
                "Dataset Name",
                placeholder="e.g., Q4 2024 Security Logs"
            )
            category = st.selectbox(
                "Category",
                options=["Threat Intelligence", "Network Logs", "User Behaviour", "System Metrics", "Security Alerts", "Other"]
            )
        
        with form_col2:
            source = st.text_input(
                "Data Source",
                placeholder="e.g., Internal SIEM, External API"
            )
            last_updated = st.date_input("Last Updated", value=datetime.today())
        
        with form_col3:
            record_count = st.number_input(
                "Record Count",
                min_value=0,
                value=100000,
                step=1000,
                help="Total number of records in the dataset"
            )
            file_size_mb = st.number_input(
                "File Size (MB)",
                min_value=0.0,
                value=50.0,
                step=0.1,
                format="%.2f"
            )
        
        submit_col1, submit_col2 = st.columns([3, 1])
        
        with submit_col2:
            submit_button = st.form_submit_button(
                "🚀 Register Dataset",
                use_container_width=True,
                type="primary"
            )
        
        if submit_button:
            if not dataset_name:
                st.error("⚠️ Please provide a dataset name")
            else:
                # Insert into database
                try:
                    query = """
                    INSERT INTO datasets_metadata (dataset_name, category, source, last_updated, record_count, file_size_mb)
                    VALUES (?, ?, ?, ?, ?, ?)
                    """
                    db.execute_query(
                        query,
                        (dataset_name, category, source, str(last_updated), record_count, file_size_mb)
                    )
                    
                    st.success(f"✅ Dataset registered successfully! Reference: DS-{len(datasets)+1:04d}")
                    st.cache_data.clear()
                    st.rerun()
                except Exception as e:
                    st.error(f"❌ Error registering dataset: {e}")

# Footer
st.divider()
st.caption("📊 Data Science Analytics Center | Advanced Dataset Intelligence Platform")
st.caption(f"Session: {st.session_state.username} | {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")