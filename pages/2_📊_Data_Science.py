"""Data Science Dashboard"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import random

from app.services.database_manager import DatabaseManager
from app.services.ai_assistant import GeminiClient
from app.models.dataset import Dataset

# Configure page
st.set_page_config(page_title="Data Science | Intelligence Platform", page_icon="📊", layout="wide")

#Authentication & Authorisation
if not st.session_state.get("logged_in", False):
    st.error("🔒 Access Denied")
    st.warning("You must be logged in to view this page.")
    if st.button("Go to Login"):
        st.switch_page("Home.py")
    st.stop()

user = st.session_state.get("user_object")
if user and not user.can_access_domain('datascience'):
    st.error("🚫 Access Denied")
    st.warning(f"Your role ({user.get_role_display_name()}) does not have permission to access the Data Science domain.")
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

#Header
col1, col2 = st.columns([3, 1])
with col1:
    st.title("📊 Data Science Analytics Hub")
with col2:
    st.markdown(f"**{st.session_state.username}**<br><small>{user.get_role_display_name()}</small>", unsafe_allow_html=True)

st.divider()

#Sidebar Filters
with st.sidebar:
    st.header("🔧 Filters")
    cat_filter = st.multiselect("Category", ["Threat Intelligence", "Network Logs", "User Behaviour", "System Metrics", "Security Alerts"])
    size_range = st.slider("Size (MB)", 0, 1000, (0, 1000))
    
    st.divider()
    if st.button("🔄 Refresh", use_container_width=True):
        st.cache_data.clear()
        st.rerun()
    
    show_add = st.button("➕ New Dataset", use_container_width=True, type="primary")

#Load Dataset Data
@st.cache_data(ttl=60)
def load_datasets():
    """Fetch all datasets from database"""
    rows = db.fetch_all("SELECT id, dataset_name, category, source, last_updated, record_count, file_size_mb FROM datasets_metadata ORDER BY id DESC")
    return [Dataset(r[0], r[1], r[2], r[3], r[4], r[5], r[6]) for r in rows]

datasets = load_datasets()

def to_df(data):
    """Convert Dataset objects to DataFrame for analysis"""
    return pd.DataFrame([{
        "ID": d.get_id(), "Name": d.get_name(), "Category": d.get_category(),
        "Source": d.get_source(), "Updated": d.get_last_updated(),
        "Records": d.get_record_count(), "Size (MB)": d.get_file_size_mb(),
        "Density": d.get_records_per_mb()
    } for d in data])

df = to_df(datasets)

# Apply sidebar filters
if not df.empty:
    df_f = df.copy()
    if cat_filter: df_f = df_f[df_f["Category"].isin(cat_filter)]
    df_f = df_f[(df_f["Size (MB)"] >= size_range[0]) & (df_f["Size (MB)"] <= size_range[1])]
else:
    df_f = df

# --- Metrics Dashboard ---
st.subheader("📊 Data Overview")
m1, m2, m3, m4, m5 = st.columns(5)

total_ds = len(datasets)
total_records = df["Records"].sum() if not df.empty else 0
total_size = df["Size (MB)"].sum() if not df.empty else 0
avg_density = df["Density"].mean() if not df.empty else 0
large_ds = len([d for d in datasets if d.is_large_dataset()])

m1.metric("Datasets", total_ds)
m2.metric("Total Records", f"{total_records/1e6:.1f}M")
m3.metric("Storage", f"{total_size/1024:.2f} GB")
m4.metric("Avg Density", f"{avg_density:.0f} rec/MB")
m5.metric("Large Datasets", large_ds)

st.divider()

# Visualisation Section
st.subheader("📈 Data Analytics")

if not df_f.empty:
    # Row 1: Distribution charts
    c1, c2, c3 = st.columns(3)
    
    with c1:
        # Category distribution pie chart
        cat_counts = df_f["Category"].value_counts()
        fig = go.Figure(data=[go.Pie(
            labels=cat_counts.index, values=cat_counts.values, hole=0.4,
            marker_colors=px.colors.sequential.Blues_r[:len(cat_counts)]
        )])
        fig.update_layout(title="By Category", height=300)
        st.plotly_chart(fig, use_container_width=True)
    
    with c2:
        # Storage usage by category (horizontal bar)
        storage = df_f.groupby("Category")["Size (MB)"].sum().sort_values()
        fig = go.Figure(data=[go.Bar(
            y=storage.index, x=storage.values, orientation='h',
            marker_color='#3b82f6', text=[f"{v:.0f}" for v in storage.values], textposition='auto'
        )])
        fig.update_layout(title="Storage by Category", height=300)
        st.plotly_chart(fig, use_container_width=True)
    
    with c3:
        # Storage utilisation gauge
        used = total_size / 1024  # Convert MB to GB
        capacity = 10  # 10 GB assumed capacity
        util = min(100, (used / capacity) * 100)
        fig = go.Figure(go.Indicator(
            mode="gauge+number",
            value=util,
            number={'suffix': "%"},
            gauge={
                'axis': {'range': [0, 100]},
                'bar': {'color': "#3b82f6"},
                'steps': [
                    {'range': [0, 60], 'color': '#dbeafe'},
                    {'range': [60, 85], 'color': '#fef3c7'},
                    {'range': [85, 100], 'color': '#fecaca'}
                ]
            },
            title={'text': "Storage Used"}
        ))
        fig.update_layout(height=300)
        st.plotly_chart(fig, use_container_width=True)
    
    # Row 2: Scatter and hierarchy charts
    c4, c5 = st.columns(2)
    
    with c4:
        # Scatter plot: records vs size
        fig = px.scatter(df_f, x="Records", y="Size (MB)", size="Records", color="Category",
                        hover_name="Name", color_discrete_sequence=px.colors.sequential.Blues_r)
        fig.update_layout(title="Size vs Records", height=350)
        st.plotly_chart(fig, use_container_width=True)
    
    with c5:
        # Treemap showing hierarchy
        fig = px.treemap(df_f, path=['Category', 'Name'], values='Size (MB)', 
                        color='Records', color_continuous_scale='Blues')
        fig.update_layout(title="Dataset Hierarchy", height=350)
        st.plotly_chart(fig, use_container_width=True)
    
    # Row 3: Top 5 comparisons
    c6, c7 = st.columns(2)
    
    with c6:
        # Largest datasets by size
        top5 = df_f.nlargest(5, 'Size (MB)')
        fig = go.Figure(data=[go.Bar(
            y=top5['Name'], x=top5['Size (MB)'], orientation='h',
            marker_color=px.colors.sequential.Blues_r[:5]
        )])
        fig.update_layout(title="Top 5 by Size", height=300)
        st.plotly_chart(fig, use_container_width=True)
    
    with c7:
        # Datasets with most records
        top5r = df_f.nlargest(5, 'Records')
        fig = go.Figure(data=[go.Bar(
            y=top5r['Name'], x=top5r['Records'], orientation='h',
            marker_color=px.colors.sequential.Blues[:5]
        )])
        fig.update_layout(title="Top 5 by Records", height=300)
        st.plotly_chart(fig, use_container_width=True)

else:
    st.info("No datasets match filters")

st.divider()

#Dataset Management & AI
st.subheader("🔍 Dataset Management")

if not df_f.empty:
    # Dataset selection dropdown
    selected_id = st.selectbox("Select Dataset", df_f["ID"].tolist(),
        format_func=lambda x: f"DS-{x:04d} | {df_f[df_f['ID']==x]['Name'].values[0]}")
    
    # Data table display
    st.dataframe(df_f, use_container_width=True, hide_index=True)
    
    # AI Assistant Section
    if client:
        st.divider()
        st.subheader("🤖 AI Analysis")
        
        # AI analysis buttons
        b1, b2, b3 = st.columns(3)
        with b1:
            btn1 = st.button("🔬 Analyse Dataset", use_container_width=True)
        with b2:
            btn2 = st.button("📊 Dashboard Insights", use_container_width=True, type="primary")
        with b3:
            btn3 = st.button("💡 ML Recommendations", use_container_width=True)
        
        # Individual AI analysis handlers
        if btn1:
            selected = next(d for d in datasets if d.get_id() == selected_id)
            messages = [
                {"role": "system", "content": "You're a data scientist. Be concise."},
                {"role": "user", "content": f"Analyse:\n{selected.get_ai_context()}"}
            ]
            with st.chat_message("assistant"):
                container = st.empty()
                full = ""
                for chunk in client.chat.completions.create(model="gemini-2.0-flash", messages=messages, stream=True):
                    if chunk.choices[0].delta.content:
                        full += chunk.choices[0].delta.content
                        container.markdown(full + "▌")
                container.markdown(full)
        
        if btn2:
            summary = f"""Data Summary:
- Datasets: {total_ds}, Records: {total_records:,}, Storage: {total_size:.1f} MB
- Categories: {df_f['Category'].value_counts().to_dict()}
- Avg Density: {avg_density:.0f} rec/MB"""
            messages = [
                {"role": "system", "content": "You're a data analyst."},
                {"role": "user", "content": f"Insights for:\n{summary}"}
            ]
            with st.chat_message("assistant"):
                container = st.empty()
                full = ""
                for chunk in client.chat.completions.create(model="gemini-2.0-flash", messages=messages, stream=True):
                    if chunk.choices[0].delta.content:
                        full += chunk.choices[0].delta.content
                        container.markdown(full + "▌")
                container.markdown(full)
        
        if btn3:
            messages = [
                {"role": "system", "content": "You're an ML engineer."},
                {"role": "user", "content": f"ML recommendations for: {df_f['Category'].value_counts().to_dict()}"}
            ]
            with st.chat_message("assistant"):
                container = st.empty()
                full = ""
                for chunk in client.chat.completions.create(model="gemini-2.0-flash", messages=messages, stream=True):
                    if chunk.choices[0].delta.content:
                        full += chunk.choices[0].delta.content
                        container.markdown(full + "▌")
                container.markdown(full)
        
        # General AI chat input
        st.divider()
        q = st.chat_input("Ask about data...")
        if q:
            messages = [{"role": "system", "content": "You're a data assistant."}, {"role": "user", "content": q}]
            with st.chat_message("user"):
                st.markdown(q)
            with st.chat_message("assistant"):
                container = st.empty()
                full = ""
                for chunk in client.chat.completions.create(model="gemini-2.0-flash", messages=messages, stream=True):
                    if chunk.choices[0].delta.content:
                        full += chunk.choices[0].delta.content
                        container.markdown(full + "▌")
                container.markdown(full)
    else:
        st.warning("⚠️ AI not configured")

#New Dataset Registration Form 
if show_add:
    st.divider()
    st.subheader("➕ Register Dataset")
    
    with st.form("new_ds"):
        c1, c2 = st.columns(2)
        with c1:
            name = st.text_input("Name", placeholder="Dataset name")
            category = st.selectbox("Category", ["Threat Intelligence", "Network Logs", "User Behaviour", "System Metrics", "Security Alerts", "Other"])
            source = st.text_input("Source", placeholder="e.g., Internal SIEM")
        with c2:
            updated = st.date_input("Last Updated", datetime.today())
            records = st.number_input("Records", min_value=0, value=100000)
            size = st.number_input("Size (MB)", min_value=0.0, value=50.0)
        
        if st.form_submit_button("🚀 Register", use_container_width=True, type="primary"):
            if name:
                db.execute_query(
                    "INSERT INTO datasets_metadata (dataset_name, category, source, last_updated, record_count, file_size_mb) VALUES (?, ?, ?, ?, ?, ?)",
                    (name, category, source, str(updated), records, size))
                st.success("✅ Dataset registered!")
                st.cache_data.clear()
                st.rerun()
            else:
                st.error("Name required")

# --- Footer ---
st.divider()
st.caption(f"📊 Data Science Hub | {st.session_state.username} | {datetime.now().strftime('%H:%M:%S')}")