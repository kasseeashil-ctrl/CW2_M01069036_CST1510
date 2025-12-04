"""Data Science dashboard - Professional edition with comprehensive analytics"""

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

# Authentication check
if not st.session_state.get("logged_in", False):
    st.error("🔒 Please login to access this page")
    if st.button("Go to Login"):
        st.switch_page("Home.py")
    st.stop()

# Permission check
user = st.session_state.get("user_object")
if user and not user.can_access_domain('datascience'):
    st.error(f"🚫 Access Denied: Your role ({user.get_role_display_name()}) cannot access Data Science.")
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
    st.title("📊 Data Science Analytics Center")
    st.caption("Dataset Management & Advanced Analytics")
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
    
    category_filter = st.multiselect(
        "Dataset Category",
        options=["Threat Intelligence", "Network Logs", "User Behaviour", "System Metrics", "Security Alerts", "Other"],
        default=[]
    )
    
    st.subheader("📏 Size Filters")
    size_range = st.slider("File Size (MB)", min_value=0, max_value=1000, value=(0, 1000), step=10)
    
    st.subheader("📊 Record Filters")
    record_range = st.slider("Record Count (thousands)", min_value=0, max_value=5000, value=(0, 5000), step=100)
    
    st.divider()
    if st.button("🔄 Refresh Data", use_container_width=True):
        st.cache_data.clear()
        st.rerun()
    
    st.divider()
    st.subheader("⚡ Quick Actions")
    show_add_dataset = st.button("➕ Register New Dataset", use_container_width=True, type="primary")

# Fetch datasets
@st.cache_data(ttl=60)
def load_datasets():
    """Load datasets as Dataset objects"""
    query = "SELECT id, dataset_name, category, source, last_updated, record_count, file_size_mb FROM datasets_metadata ORDER BY id DESC"
    rows = db.fetch_all(query)
    
    datasets = []
    for row in rows:
        dataset = Dataset(
            dataset_id=row[0], name=row[1], category=row[2], source=row[3],
            last_updated=row[4], record_count=row[5], file_size_mb=row[6]
        )
        datasets.append(dataset)
    return datasets

datasets = load_datasets()

# Convert to DataFrame
def datasets_to_dataframe(datasets_list):
    """Convert datasets to pandas DataFrame"""
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
    
    if category_filter:
        df_filtered = df_filtered[df_filtered["Category"].isin(category_filter)]
    
    df_filtered = df_filtered[
        (df_filtered["Size (MB)"] >= size_range[0]) &
        (df_filtered["Size (MB)"] <= size_range[1])
    ]
    
    df_filtered = df_filtered[
        (df_filtered["Records"] >= record_range[0] * 1000) &
        (df_filtered["Records"] <= record_range[1] * 1000)
    ]
else:
    df_filtered = df

# Metrics row
st.subheader("📊 Dataset Overview")

col1, col2, col3, col4, col5 = st.columns(5)

with col1:
    st.metric("Total Datasets", len(datasets))

with col2:
    if not df.empty:
        total_records = df["Records"].sum()
        st.metric("Total Records", f"{total_records / 1_000_000:.2f}M")
    else:
        st.metric("Total Records", "0")

with col3:
    if not df.empty:
        total_size_gb = df["Size (MB)"].sum() / 1024
        st.metric("Total Storage", f"{total_size_gb:.2f} GB")
    else:
        st.metric("Total Storage", "0 GB")

with col4:
    large_count = len([ds for ds in datasets if ds.is_large_dataset()])
    st.metric("Large Datasets", large_count)

with col5:
    if not df.empty:
        avg_density = df["Density"].mean()
        st.metric("Avg. Density", f"{avg_density:.1f} rec/MB")
    else:
        st.metric("Avg. Density", "N/A")

st.divider()

# Visualisations (Professional charts)
st.subheader("📈 Data Analytics Dashboard")

if not df_filtered.empty:
    
    # Row 1: Distribution charts
    chart_col1, chart_col2 = st.columns(2)
    
    with chart_col1:
        st.markdown("**📁 Dataset Distribution by Category**")
        category_counts = df_filtered["Category"].value_counts()
        fig_categories = px.bar(x=category_counts.index, y=category_counts.values, color=category_counts.values, color_continuous_scale="Blues")
        fig_categories.update_layout(xaxis_title="Category", yaxis_title="Count", showlegend=False, height=400)
        st.plotly_chart(fig_categories, use_container_width=True)
    
    with chart_col2:
        st.markdown("**💾 Storage Distribution**")
        storage_by_category = df_filtered.groupby("Category")["Size (MB)"].sum().sort_values(ascending=False)
        fig_storage = px.pie(values=storage_by_category.values, names=storage_by_category.index, hole=0.4, color_discrete_sequence=px.colors.qualitative.Pastel)
        fig_storage.update_traces(textposition='inside', textinfo='percent+label')
        fig_storage.update_layout(height=400)
        st.plotly_chart(fig_storage, use_container_width=True)
    
    # Row 2: Scatter and tree map
    chart_col3, chart_col4 = st.columns(2)
    
    with chart_col3:
        st.markdown("**🔍 Dataset Size vs Record Count Analysis**")
        fig_scatter = px.scatter(df_filtered, x="Records", y="Size (MB)", size="Records", color="Category", hover_name="Name", size_max=50, color_discrete_sequence=px.colors.qualitative.Set2)
        fig_scatter.update_layout(xaxis_title="Records", yaxis_title="Size (MB)", height=400)
        st.plotly_chart(fig_scatter, use_container_width=True)
    
    with chart_col4:
        st.markdown("**🗂️ Dataset Hierarchy View**")
        fig_treemap = px.treemap(df_filtered, path=['Category', 'Name'], values='Size (MB)', color='Records', color_continuous_scale='Viridis')
        fig_treemap.update_layout(height=400)
        st.plotly_chart(fig_treemap, use_container_width=True)
    
    # Row 3: Advanced analytics
    st.markdown("**🔬 Advanced Dataset Analytics**")
    
    analysis_col1, analysis_col2, analysis_col3 = st.columns(3)
    
    with analysis_col1:
        st.markdown("**Top 5 Largest Datasets**")
        top_datasets = df_filtered.nlargest(5, 'Size (MB)')
        fig_top = go.Figure(data=[go.Bar(y=top_datasets['Name'][::-1], x=top_datasets['Size (MB)'][::-1], orientation='h', marker_color='#10B981', text=[f"{s:.1f} MB" for s in top_datasets['Size (MB)'][::-1]], textposition='auto')])
        fig_top.update_layout(xaxis_title="Size (MB)", yaxis_title="", height=300, margin=dict(l=150))
        st.plotly_chart(fig_top, use_container_width=True)
    
    with analysis_col2:
        st.markdown("**Data Source Distribution**")
        source_counts = df_filtered['Source'].value_counts()
        fig_sources = px.pie(values=source_counts.values, names=source_counts.index, color_discrete_sequence=px.colors.qualitative.Safe)
        fig_sources.update_traces(textposition='inside', textinfo='label+percent')
        fig_sources.update_layout(height=300)
        st.plotly_chart(fig_sources, use_container_width=True)
    
    with analysis_col3:
        st.markdown("**Dataset Efficiency (Records/MB)**")
        top_density = df_filtered.nlargest(5, 'Density')
        fig_density = px.bar(x=top_density['Density'], y=top_density['Name'], orientation='h', color=top_density['Density'], color_continuous_scale='Teal')
        fig_density.update_layout(xaxis_title="Records per MB", yaxis_title="", showlegend=False, height=300, margin=dict(l=150))
        st.plotly_chart(fig_density, use_container_width=True)
    
    # Row 4: Timeline
    st.markdown("**📅 Dataset Updates Timeline**")
    df_timeline = df_filtered.copy()
    df_timeline['Last Updated'] = pd.to_datetime(df_timeline['Last Updated'])
    timeline_data = df_timeline.groupby('Last Updated').size().reset_index(name='Count')
    
    fig_timeline = px.line(timeline_data, x='Last Updated', y='Count', markers=True, line_shape='spline')
    fig_timeline.update_traces(line_color='#0EA5E9', marker=dict(size=10, color='#0EA5E9'))
    fig_timeline.update_layout(xaxis_title="Date", yaxis_title="Updates", height=300)
    st.plotly_chart(fig_timeline, use_container_width=True)

else:
    st.info("📊 No datasets match the filters.")

st.divider()

# Datasets table
st.subheader("🔍 Dataset Management")

if not df_filtered.empty:
    st.caption(f"Showing **{len(df_filtered)}** of **{len(df)}** datasets")
    
    selected_dataset_id = st.selectbox(
        "Select dataset to view details:",
        options=df_filtered["ID"].tolist(),
        format_func=lambda x: f"DS-{x:04d} | {df_filtered[df_filtered['ID']==x]['Name'].values[0]}"
    )
    
    display_df = df_filtered.drop(columns=['Is Large'])
    st.dataframe(display_df, use_container_width=True, hide_index=True)
    
    # AI Analysis section
    if ai and selected_dataset_id:
        st.divider()
        st.subheader("🤖 AI-Powered Dataset Analysis")
        
        selected_dataset = next(ds for ds in datasets if ds.get_id() == selected_dataset_id)
        
        col_ai1, col_ai2 = st.columns([3, 1])
        with col_ai1:
            st.markdown(f"**Analysing Dataset #{selected_dataset_id}:** {selected_dataset.get_name()}")
        with col_ai2:
            analyse_button = st.button("🔬 Analyse with AI", use_container_width=True, type="primary")
        
        if analyse_button:
            with st.spinner("🤖 AI is analysing the dataset..."):
                context = selected_dataset.get_ai_context()
                ai.set_domain("datascience")
                analysis = ai.analyse_dataset(context)
                
                with st.expander("📊 Analysis Report", expanded=True):
                    st.markdown(analysis)
                
                st.divider()
                st.markdown("#### 💬 Ask Follow-up Questions")
                follow_up = st.text_input("Have questions?", placeholder="e.g., What ML models would work best?")
                
                if follow_up:
                    with st.spinner("🤖 Generating response..."):
                        response = ai.send_message(follow_up, context=context)
                        st.markdown("**AI Response:**")
                        st.info(response)
    else:
        if not ai:
            st.warning("⚠️ AI Assistant not configured. Add Gemini API key.")

else:
    st.info("📊 No datasets to display.")

# Add dataset form
if show_add_dataset:
    st.divider()
    st.subheader("➕ Register New Dataset")
    
    with st.form("new_dataset_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            dataset_name = st.text_input("Dataset Name", placeholder="e.g., Q4 2024 Security Logs")
            category = st.selectbox("Category", ["Threat Intelligence", "Network Logs", "User Behaviour", "System Metrics", "Security Alerts", "Other"])
            source = st.text_input("Source", placeholder="e.g., Internal SIEM")
        
        with col2:
            last_updated = st.date_input("Last Updated", value=datetime.today())
            record_count = st.number_input("Record Count", min_value=0, value=100000, step=1000)
            file_size_mb = st.number_input("File Size (MB)", min_value=0.0, value=50.0, step=0.1, format="%.2f")
        
        submit = st.form_submit_button("🚀 Register Dataset", use_container_width=True, type="primary")
        
        if submit:
            if not dataset_name:
                st.error("⚠️ Please provide a dataset name")
            else:
                try:
                    query = "INSERT INTO datasets_metadata (dataset_name, category, source, last_updated, record_count, file_size_mb) VALUES (?, ?, ?, ?, ?, ?)"
                    db.execute_query(query, (dataset_name, category, source, str(last_updated), record_count, file_size_mb))
                    st.success("✅ Dataset registered successfully!")
                    st.cache_data.clear()
                    st.rerun()
                except Exception as e:
                    st.error(f"❌ Error: {e}")

# Footer
st.divider()
st.caption("📊 Data Science Analytics Center | Powered by Google Gemini AI")
st.caption(f"Session: {st.session_state.username} | {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")