"""Data Science Dashboard"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import os

from app.services.database_manager import DatabaseManager
from app.services.ai_assistant import GeminiClient

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
    # Get unique uploaded_by values for filter
    uploaded_by_filter = st.multiselect("Uploaded By", ["data_scientist", "cyber_admin", "it_admin"])
    
    st.divider()
    if st.button("🔄 Refresh", use_container_width=True):
        st.cache_data.clear()
        st.rerun()
    
    show_add = st.button("➕ New Dataset", use_container_width=True, type="primary")

#Load Dataset Data from CSV
@st.cache_data(ttl=60)
def load_datasets():
    """Load datasets from CSV file"""
    csv_path = "DATA/datasets_metadata.csv"
    if os.path.exists(csv_path):
        df = pd.read_csv(csv_path)
        # Rename columns to match expected format
        df = df.rename(columns={
            'dataset_id': 'ID',
            'name': 'Name',
            'rows': 'Rows',
            'columns': 'Columns',
            'uploaded_by': 'Uploaded By',
            'upload_date': 'Upload Date'
        })
        return df
    return pd.DataFrame()

df = load_datasets()

# Apply sidebar filters
if not df.empty:
    df_f = df.copy()
    if uploaded_by_filter: df_f = df_f[df_f["Uploaded By"].isin(uploaded_by_filter)]
else:
    df_f = df

# --- Metrics Dashboard ---
st.subheader("📊 Data Overview")
m1, m2, m3, m4, m5 = st.columns(5)

total_ds = len(df)
total_rows = df["Rows"].sum() if not df.empty else 0
total_columns = df["Columns"].sum() if not df.empty else 0
avg_rows = df["Rows"].mean() if not df.empty else 0
max_rows = df["Rows"].max() if not df.empty else 0

m1.metric("Datasets", total_ds)
m2.metric("Total Rows", f"{total_rows/1e3:.1f}K" if total_rows >= 1000 else str(total_rows))
m3.metric("Total Columns", total_columns)
m4.metric("Avg Rows/Dataset", f"{avg_rows/1e3:.1f}K" if avg_rows >= 1000 else f"{avg_rows:.0f}")
m5.metric("Largest Dataset", f"{max_rows/1e3:.0f}K rows" if max_rows >= 1000 else f"{max_rows} rows")

st.divider()

# Visualisation Section
st.subheader("📈 Data Analytics")

if not df_f.empty:
    # Row 1: Distribution charts
    c1, c2, c3 = st.columns(3)
    
    with c1:
        # Uploaded By distribution pie chart
        uploader_counts = df_f["Uploaded By"].value_counts()
        fig = go.Figure(data=[go.Pie(
            labels=uploader_counts.index, values=uploader_counts.values, hole=0.4,
            marker_colors=px.colors.sequential.Blues_r[:len(uploader_counts)]
        )])
        fig.update_layout(title="By Uploader", height=300)
        st.plotly_chart(fig, use_container_width=True)
    
    with c2:
        # Rows by dataset (horizontal bar)
        rows_by_dataset = df_f.set_index('Name')['Rows'].sort_values()
        fig = go.Figure(data=[go.Bar(
            y=rows_by_dataset.index, x=rows_by_dataset.values, orientation='h',
            marker_color='#3b82f6', text=[f"{v/1000:.0f}K" if v >= 1000 else str(v) for v in rows_by_dataset.values], textposition='auto'
        )])
        fig.update_layout(title="Rows by Dataset", height=300)
        st.plotly_chart(fig, use_container_width=True)
    
    with c3:
        # Data coverage gauge (based on total rows)
        target_rows = 1000000  # 1M rows target
        coverage = min(100, (total_rows / target_rows) * 100)
        fig = go.Figure(go.Indicator(
            mode="gauge+number",
            value=coverage,
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
            title={'text': "Data Coverage"}
        ))
        fig.update_layout(height=300)
        st.plotly_chart(fig, use_container_width=True)
    
    # Row 2: Scatter and bar charts
    c4, c5 = st.columns(2)
    
    with c4:
        # Scatter plot: rows vs columns
        fig = px.scatter(df_f, x="Rows", y="Columns", size="Rows", color="Uploaded By",
                        hover_name="Name", color_discrete_sequence=px.colors.sequential.Blues_r)
        fig.update_layout(title="Dataset Dimensions", height=350)
        st.plotly_chart(fig, use_container_width=True)
    
    with c5:
        # Bar chart showing columns per dataset
        fig = go.Figure(data=[go.Bar(
            x=df_f['Name'], y=df_f['Columns'],
            marker_color='#3b82f6', text=df_f['Columns'], textposition='auto'
        )])
        fig.update_layout(title="Columns per Dataset", height=350)
        st.plotly_chart(fig, use_container_width=True)
    
    # Row 3: Top datasets
    c6, c7 = st.columns(2)
    
    with c6:
        # Largest datasets by rows
        top5 = df_f.nlargest(5, 'Rows')
        fig = go.Figure(data=[go.Bar(
            y=top5['Name'], x=top5['Rows'], orientation='h',
            marker_color=px.colors.sequential.Blues_r[:5]
        )])
        fig.update_layout(title="Top 5 by Rows", height=300)
        st.plotly_chart(fig, use_container_width=True)
    
    with c7:
        # Datasets by columns
        top5c = df_f.nlargest(5, 'Columns')
        fig = go.Figure(data=[go.Bar(
            y=top5c['Name'], x=top5c['Columns'], orientation='h',
            marker_color=px.colors.sequential.Blues[:5]
        )])
        fig.update_layout(title="Top 5 by Columns", height=300)
        st.plotly_chart(fig, use_container_width=True)

else:
    st.info("No datasets match filters")

st.divider()

#Dataset Management & AI
st.subheader("🔍 Dataset Management")

if not df_f.empty:
    # Dataset selection dropdown
    selected_id = st.selectbox("Select Dataset", df_f["ID"].tolist(),
        format_func=lambda x: f"DS-{int(x):04d} | {df_f[df_f['ID']==x]['Name'].values[0]}")
    
    # Data table display
    st.dataframe(df_f, use_container_width=True, hide_index=True)
    
    # Get selected dataset details
    selected_dataset = df_f[df_f['ID'] == selected_id].iloc[0]
    
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
            dataset_context = f"""
Dataset ID: {selected_dataset['ID']}
Name: {selected_dataset['Name']}
Rows: {selected_dataset['Rows']}
Columns: {selected_dataset['Columns']}
Uploaded By: {selected_dataset['Uploaded By']}
Upload Date: {selected_dataset['Upload Date']}
"""
            messages = [
                {"role": "system", "content": "You're a data scientist. Be concise."},
                {"role": "user", "content": f"Analyse:\n{dataset_context}"}
            ]
            with st.chat_message("assistant"):
                container = st.empty()
                full = ""
                for chunk in client.chat.completions.create(model="gemini-2.0-flash", messages=messages, stream=True, domain="Data Science"):
                    if chunk.choices[0].delta.content:
                        full += chunk.choices[0].delta.content
                        container.markdown(full + "▌")
                container.markdown(full)
        
        if btn2:
            summary = f"""Data Summary:
- Datasets: {total_ds}, Total Rows: {total_rows:,}, Total Columns: {total_columns}
- Uploaders: {df_f['Uploaded By'].value_counts().to_dict()}
- Avg Rows per Dataset: {avg_rows:.0f}"""
            messages = [
                {"role": "system", "content": "You're a data analyst."},
                {"role": "user", "content": f"Insights for:\n{summary}"}
            ]
            with st.chat_message("assistant"):
                container = st.empty()
                full = ""
                for chunk in client.chat.completions.create(model="gemini-2.0-flash", messages=messages, stream=True, domain="Data Science"):
                    if chunk.choices[0].delta.content:
                        full += chunk.choices[0].delta.content
                        container.markdown(full + "▌")
                container.markdown(full)
        
        if btn3:
            dataset_names = df_f['Name'].tolist()
            messages = [
                {"role": "system", "content": "You're an ML engineer."},
                {"role": "user", "content": f"ML recommendations for datasets: {dataset_names}. Total rows: {total_rows}, Total columns: {total_columns}"}
            ]
            with st.chat_message("assistant"):
                container = st.empty()
                full = ""
                for chunk in client.chat.completions.create(model="gemini-2.0-flash", messages=messages, stream=True, domain="Data Science"):
                    if chunk.choices[0].delta.content:
                        full += chunk.choices[0].delta.content
                        container.markdown(full + "▌")
                container.markdown(full)
        
        # General AI chat input
        st.divider()
        q = st.chat_input("Ask about data...")
        if q:
            messages = [{"role": "system", "content": "You're a data assistant. Only use data science dataset metadata from this dashboard."}, {"role": "user", "content": q}]
            with st.chat_message("user"):
                st.markdown(q)
            with st.chat_message("assistant"):
                container = st.empty()
                full = ""
                for chunk in client.chat.completions.create(model="gemini-2.0-flash", messages=messages, stream=True, domain="Data Science"):
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
            rows = st.number_input("Rows", min_value=0, value=1000)
            columns = st.number_input("Columns", min_value=1, value=10)
        with c2:
            uploaded_by = st.text_input("Uploaded By", st.session_state.username, disabled=True)
            upload_date = st.date_input("Upload Date", datetime.today())
        
        if st.form_submit_button("🚀 Register", use_container_width=True, type="primary"):
            if name:
                # Load existing CSV, add new row, save back
                csv_path = "DATA/datasets_metadata.csv"
                if os.path.exists(csv_path):
                    existing_df = pd.read_csv(csv_path)
                    new_id = existing_df['dataset_id'].max() + 1
                else:
                    existing_df = pd.DataFrame(columns=['dataset_id', 'name', 'rows', 'columns', 'uploaded_by', 'upload_date'])
                    new_id = 1
                
                new_row = pd.DataFrame([{
                    'dataset_id': new_id,
                    'name': name,
                    'rows': rows,
                    'columns': columns,
                    'uploaded_by': st.session_state.username,
                    'upload_date': str(upload_date)
                }])
                updated_df = pd.concat([existing_df, new_row], ignore_index=True)
                os.makedirs("DATA", exist_ok=True)
                updated_df.to_csv(csv_path, index=False)
                st.success("✅ Dataset registered!")
                st.cache_data.clear()
                st.rerun()
            else:
                st.error("Name required")

# --- Footer ---
st.divider()
st.caption(f"📊 Data Science Hub | {st.session_state.username} | {datetime.now().strftime('%H:%M:%S')}")