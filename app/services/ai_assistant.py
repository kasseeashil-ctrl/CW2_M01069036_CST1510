"""AI assistant service using Google Gemini - Dashboard Data Reader"""

import os
import streamlit as st
import pandas as pd
import google.generativeai as genai
from typing import Dict, Any


# ----------------------------------------------------------------------
# Dashboard Data Reader
# ----------------------------------------------------------------------

class DashboardDataReader:
    """Reads and aggregates data from all dashboard CSV files"""
    
    def __init__(self, db_manager=None):
        self.db = db_manager
        self.csv_base_path = "DATA"
        self._configs = {
            'cybersecurity': {
                'file': 'cyber_incidents.csv',
                'columns': {'Reported_By': 'Reported By'},
                'defaults': {'Reported By': 'System'},
                'stats_cols': {'status': 'Status', 'severity': 'Severity', 'type': 'Type'}
            },
            'datascience': {
                'file': 'datasets_metadata.csv',
                'columns': {
                    'dataset_id': 'ID', 'name': 'Name', 'rows': 'Record Count',
                    'columns': 'Columns', 'uploaded_by': 'Uploaded By', 'upload_date': 'Last Updated'
                },
                'defaults': {'Category': 'General', 'Source': 'Internal', 'Size (MB)': 0},
                'stats_cols': {}
            },
            'itoperations': {
                'file': 'it_tickets.csv',
                'columns': {
                    'ticket_id': 'ID', 'priority': 'Priority', 'status': 'Status',
                    'assigned_to': 'Assigned To', 'created_at': 'Created', 'description': 'Description'
                },
                'defaults': {
                    'Ticket ID': lambda df: df['ID'],
                    'Category': 'General',
                    'Subject': lambda df: df['Description'].str[:50] if 'Description' in df.columns else '',
                    'Resolved': None
                },
                'stats_cols': {'status': 'Status', 'priority': 'Priority', 'assigned': 'Assigned To'}
            }
        }
    
    def _read_csv(self, domain: str) -> pd.DataFrame:
        """Generic CSV reader with column mapping"""
        config = self._configs.get(domain)
        if not config or not os.path.exists(os.path.join(self.csv_base_path, config['file'])):
            return pd.DataFrame()
        
        try:
            df = pd.read_csv(os.path.join(self.csv_base_path, config['file']))
            if config['columns']:
                df = df.rename(columns=config['columns'])
            for col, default in config['defaults'].items():
                if col not in df.columns:
                    df[col] = default(df) if callable(default) else default
            return df
        except Exception:
            return pd.DataFrame()
    
    def get_cybersecurity_df(self) -> pd.DataFrame:
        return self._read_csv('cybersecurity')
    
    def get_datascience_df(self) -> pd.DataFrame:
        return self._read_csv('datascience')
    
    def get_itoperations_df(self) -> pd.DataFrame:
        return self._read_csv('itoperations')
    
    def get_cybersecurity_stats(self) -> Dict[str, Any]:
        """Get cybersecurity statistics"""
        df = self.get_cybersecurity_df()
        if df.empty:
            return {'total': 0, 'active': 0, 'critical': 0, 'resolved': 0, 'resolution_rate': 0}
        
        total = len(df)
        status_col = 'Status'
        severity_col = 'Severity'
        type_col = 'Type'
        
        active = len(df[df[status_col].isin(['Open', 'Investigating', 'In Progress'])])
        resolved = len(df[df[status_col].isin(['Resolved', 'Closed'])])
        
        return {
            'total': total,
            'active': active,
            'critical': len(df[df[severity_col] == 'Critical']),
            'resolved': resolved,
            'resolution_rate': (resolved / total * 100) if total > 0 else 0,
            'type_distribution': df[type_col].value_counts().to_dict(),
            'severity_distribution': df[severity_col].value_counts().to_dict(),
            'status_distribution': df[status_col].value_counts().to_dict()
        }
    
    def get_datascience_stats(self) -> Dict[str, Any]:
        """Get data science statistics"""
        df = self.get_datascience_df()
        if df.empty:
            return {'total_datasets': 0, 'total_records': 0, 'total_size_mb': 0}
        
        total_size = df['Size (MB)'].sum() if 'Size (MB)' in df.columns else 0
        total_records = df['Record Count'].sum() if 'Record Count' in df.columns else 0
        return {
            'total_datasets': len(df),
            'total_records': total_records,
            'total_size_mb': total_size,
            'total_size_gb': total_size / 1024 if total_size > 0 else 0,
            'large_datasets': len(df[df['Size (MB)'] > 100]) if 'Size (MB)' in df.columns else 0,
            'category_distribution': df['Category'].value_counts().to_dict() if 'Category' in df.columns else {},
            'uploader_distribution': df['Uploaded By'].value_counts().to_dict() if 'Uploaded By' in df.columns else {}
        }
    
    def get_itoperations_stats(self) -> Dict[str, Any]:
        """Get IT operations statistics"""
        df = self.get_itoperations_df()
        if df.empty:
            return {'total': 0, 'active': 0, 'critical': 0, 'assigned': 0}
        
        total = len(df)
        status_col, priority_col, assigned_col = 'Status', 'Priority', 'Assigned To'
        active = len(df[df[status_col].isin(['Open', 'In Progress'])])
        resolved = len(df[df[status_col] == 'Resolved'])
        
        return {
            'total': total,
            'active': active,
            'critical': len(df[df[priority_col] == 'Critical']),
            'assigned': len(df[df[assigned_col].notna() & (df[assigned_col] != '')]),
            'resolved': resolved,
            'resolution_rate': (resolved / total * 100) if total > 0 else 0,
            'priority_distribution': df[priority_col].value_counts().to_dict(),
            'category_distribution': df['Category'].value_counts().to_dict() if 'Category' in df.columns else {},
            'status_distribution': df[status_col].value_counts().to_dict(),
            'assigned_distribution': df[assigned_col].value_counts().to_dict()
        }
    
    def get_all_stats(self) -> Dict[str, Any]:
        return {
            'cybersecurity': self.get_cybersecurity_stats(),
            'datascience': self.get_datascience_stats(),
            'itoperations': self.get_itoperations_stats()
        }


# ----------------------------------------------------------------------
# Gemini Client & AI Functions
# ----------------------------------------------------------------------

def initialize_gemini_client():
    """Initialize Gemini API"""
    try:
        api_key = (st.secrets.get('gemini', {}).get('api_key') or 
                  os.environ.get('GEMINI_API_KEY') or 
                  st.secrets.get("GEMINI_API_KEY", ""))
        if not api_key:
            st.error("Gemini API key not found.")
            return None
        genai.configure(api_key=api_key)
        return True
    except Exception as e:
        st.error(f"Error initializing Gemini: {e}")
        return None

def _generate_response(prompt: str) -> str:
    """Generate AI response with error handling"""
    try:
        model = genai.GenerativeModel('gemini-2.0-flash')
        return model.generate_content(prompt).text
    except Exception as e:
        error_msg = str(e)
        if "429" in error_msg or "Resource exhausted" in error_msg:
            return "⚠️ **API Rate Limit Reached**\n\nThe Gemini API has reached its rate limit. Please wait a few minutes and try again.\nYou can still use dashboard features (tables, charts) without AI."
        return f"⚠️ **Gemini API Error**: {error_msg}"

def get_custom_dashboard_query(data_reader: DashboardDataReader, user_query: str, 
                                domain: str = "General", client: Any = None) -> str:
    """Answer user query using dashboard data"""
    domain_configs = {
        "Cybersecurity": {
            'df_method': 'get_cybersecurity_df',
            'stats_method': 'get_cybersecurity_stats',
            'title': 'CYBERSECURITY DASHBOARD DATA ONLY',
            'instruction': 'You are analyzing ONLY the Cybersecurity dashboard. Use ONLY cybersecurity incident data provided above.'
        },
        "Data Science": {
            'df_method': 'get_datascience_df',
            'stats_method': 'get_datascience_stats',
            'title': 'DATA SCIENCE DASHBOARD DATA ONLY',
            'instruction': 'You are analyzing ONLY the Data Science dashboard. Use ONLY dataset metadata provided above.'
        },
        "IT Operations": {
            'df_method': 'get_itoperations_df',
            'stats_method': 'get_itoperations_stats',
            'title': 'IT OPERATIONS DASHBOARD DATA ONLY',
            'instruction': 'You are analyzing ONLY the IT Operations dashboard. Use ONLY ticket data provided above.'
        }
    }
    
    if domain in domain_configs:
        config = domain_configs[domain]
        df = getattr(data_reader, config['df_method'])()
        stats = getattr(data_reader, config['stats_method'])()
        data_str = df.to_markdown(index=False) if not df.empty else "No data available"
        if domain == "IT Operations":
            data_str = df.drop(columns=['Description'], errors='ignore').to_markdown(index=False) if not df.empty else "No data available"
        
        context = f"""=== {config['title']} ===
You MUST ONLY use this {domain.lower()} data. Do NOT reference data from other dashboards.

Statistics: {stats}
All Records:
{data_str}
"""
        instruction = config['instruction']
    else:
        # General - all data
        all_stats = data_reader.get_all_stats()
        cyber_df = data_reader.get_cybersecurity_df()
        ds_df = data_reader.get_datascience_df()
        it_df = data_reader.get_itoperations_df()
        context = f"""=== ALL DASHBOARD DATA ===
CYBERSECURITY: {all_stats['cybersecurity']}
Recent Incidents (top 5): {cyber_df.head(5).to_markdown(index=False) if not cyber_df.empty else "No data"}

DATA SCIENCE: {all_stats['datascience']}
Datasets (top 5): {ds_df.head(5).to_markdown(index=False) if not ds_df.empty else "No data"}

IT OPERATIONS: {all_stats['itoperations']}
Recent Tickets (top 5): {it_df.drop(columns=['Description'], errors='ignore').head(5).to_markdown(index=False) if not it_df.empty else "No data"}
"""
        instruction = "You can analyze data from all dashboards provided above."
    
    prompt = f"""{instruction}

AVAILABLE DATA:
{context}

USER QUESTION: {user_query}

Provide a concise, accurate response based STRICTLY on the data provided above.
If the question cannot be answered from the available data, clearly state that the dashboard does not contain that information.
"""
    return _generate_response(prompt)


# ----------------------------------------------------------------------
# GeminiClient Wrapper
# ----------------------------------------------------------------------

class GeminiClient:
    """Wrapper providing OpenAI-style interface using Gemini"""
    
    def __init__(self, api_key: str = None, db_manager=None):
        self._data_reader = DashboardDataReader(db_manager)
        if api_key:
            try:
                genai.configure(api_key=api_key)
                self._client_initialized = True
            except Exception as e:
                st.error(f"Error initializing Gemini: {e}")
                self._client_initialized = False
        else:
            self._client_initialized = (initialize_gemini_client() is not None)
        self.chat = self._ChatCompletions(self)
    
    def set_database(self, db_manager):
        self._data_reader = DashboardDataReader(db_manager)
    
    class _ChatCompletions:
        def __init__(self, parent):
            self._parent = parent
            self.completions = self
        
        def create(self, model: str, messages: list, stream: bool = False, 
                   temperature: float = 1.0, domain: str = "General"):
            user_message = next((m.get("content", "") for m in messages if m.get("role") == "user"), "")
            if not user_message or not self._parent._client_initialized:
                return self._create_response("AI service unavailable. Please configure the API key.")
            
            if not self._parent._data_reader:
                self._parent._data_reader = DashboardDataReader()
            
            # Detect domain from system message
            system_msg = next((m.get("content", "") for m in messages if m.get("role") == "system"), "")
            if system_msg and domain == "General":
                domain_map = {
                    ("cybersecurity", "security"): "Cybersecurity",
                    ("data science", "data scientist"): "Data Science",
                    ("it", "operations"): "IT Operations"
                }
                for keywords, detected in domain_map.items():
                    if any(kw in system_msg.lower() for kw in keywords):
                        domain = detected
                        break
            
            response = get_custom_dashboard_query(self._parent._data_reader, user_message, domain, None)
            return self._stream_response(response) if stream else self._create_response(response)
        
        def _create_response(self, content: str):
            return type('ChatCompletion', (), {
                'choices': [type('Choice', (), {
                    'message': type('Message', (), {'content': content, 'role': 'assistant'})()
                })()]
            })()
        
        def _stream_response(self, content: str):
            yield type('StreamChunk', (), {
                'choices': [type('Choice', (), {
                    'delta': type('Delta', (), {'content': content})()
                })()]
            })()


AIAssistant = GeminiClient
