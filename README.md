# Multi-Domain Intelligence Platform

A web application for managing cybersecurity incidents, datasets, and IT support tickets. Built with Streamlit and Python.

## Overview

This platform provides a centralised dashboard for three IT domains:

- **Cybersecurity** - Security incident tracking and threat analysis
- **Data Science** - Dataset management and analytics
- **IT Operations** - Support ticket management and troubleshooting

The system uses role-based access control, so users only see the domains relevant to their job role. An integrated AI assistant (powered by Google Gemini) provides analysis and recommendations for each domain.

## Requirements

- Python 3.8 or higher
- Google Gemini API key

## Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/your-repo.git
cd your-repo
```

2. Create and activate a virtual environment:
```bash
# Windows
python -m venv venv
venv\Scripts\activate

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Create the secrets file at `.streamlit/secrets.toml`:
```toml
GEMINI_API_KEY = "your-api-key-here"
DB_PATH = "DATA/intelligence_platform.db"
```

5. Initialise the database:
```bash
python setup_database.py
```

6. Run the application:
```bash
streamlit run Home.py
```

The app will open at `http://localhost:8501`

## Project Structure

```
├── Home.py                     # Login and registration page
├── setup_database.py           # Database initialisation script
├── requirements.txt
│
├── app/
│   ├── models/                 # Entity classes
│   │   ├── user.py
│   │   ├── security_incidents.py
│   │   ├── dataset.py
│   │   └── it_tickets.py
│   │
│   ├── services/               # Business logic
│   │   ├── database_manager.py
│   │   ├── auth_manager.py
│   │   └── ai_assistant.py
│   │
│   └── data/
│       └── schema.py           # Database table definitions
│
├── pages/
│   ├── 1_🛡️_Cybersecurity.py
│   ├── 2_📊_Data_Science.py
│   ├── 3_💻_IT_Operations.py
│   └── 4_🤖_AI_Assistant.py
│
├── DATA/
│   └── intelligence_platform.db
│
└── .streamlit/
    └── secrets.toml            # API keys (not tracked in git)
```

## Demo Accounts

The setup script creates these test accounts:

| Role | Username | Password |
|------|----------|----------|
| Cybersecurity Analyst | cyber_analyst | CyberPass123! |
| Data Scientist | data_scientist | DataPass123! |
| IT Engineer | it_engineer | ITPass123! |
| Administrator | admin | AdminPass123! |

Each role can only access their respective domain. The admin account has access to all domains.

## Features

### Authentication
- Secure password hashing with bcrypt
- Role-based access control
- Session management with Streamlit

### Dashboards
Each domain dashboard includes:
- Summary metrics
- Interactive charts (Plotly)
- Data tables with filtering
- CRUD operations for records
- AI-powered analysis

### AI Integration
- Google Gemini API (gemini-2.0-flash model)
- Dashboard analysis - summarises current metrics
- Item analysis - detailed review of selected records
- Domain-specific insights - threat intelligence, ML recommendations, SLA analysis
- Streaming responses for better UX

## Database Schema

**users** - Authentication and role management
- id, username, password_hash, role

**cyber_incidents** - Security incident records
- id, date, incident_type, severity, status, description, reported_by

**datasets_metadata** - Dataset registry
- id, dataset_name, category, source, last_updated, record_count, file_size_mb

**it_tickets** - Support tickets
- id, ticket_id, priority, status, category, subject, description, created_date, resolved_date, assigned_to

## Technologies

- **Frontend**: Streamlit
- **Database**: SQLite
- **Charts**: Plotly
- **Authentication**: bcrypt
- **AI**: Google Gemini API
- **Language**: Python 3.8+

## Configuration

All configuration is stored in `.streamlit/secrets.toml`:

```toml
GEMINI_API_KEY = "your-gemini-api-key"
DB_PATH = "DATA/intelligence_platform.db"
```

## Troubleshooting

**ModuleNotFoundError**  
Make sure you've activated the virtual environment and run `pip install -r requirements.txt`

**AI features not working**  
Check that your API key is correctly set in `.streamlit/secrets.toml`

**Access Denied error**  
You're trying to access a domain your role doesn't have permission for. Log in with the admin account to access all domains.

**Database errors**  
Delete the database file and run `python setup_database.py` again to reset.

## Author

Student ID: M01069036  
Course: CST1510  
Middlesex University

## License
This project was created for educational purposes as part of CST1510 coursework.