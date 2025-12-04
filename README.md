# 🛡️ Multi-Domain Intelligence Platform

A professional web-based intelligence platform integrating **Cybersecurity**, **Data Science**, and **IT Operations** with AI-powered analysis.

## 📋 Table of Contents

- [Features](#features)
- [Architecture](#architecture)
- [Installation](#installation)
- [Configuration](#configuration)
- [Usage](#usage)
- [Project Structure](#project-structure)
- [Demo Accounts](#demo-accounts)
- [Technologies Used](#technologies-used)

---

## ✨ Features

### 🛡️ Cybersecurity Domain
- **Incident Management** - Track and manage security incidents
- **Severity Classification** - Categorise threats by severity level
- **AI-Powered Analysis** - Get expert recommendations for incident response
- **Real-time Dashboards** - Visualise incident statistics with interactive charts

### 📊 Data Science Domain
- **Dataset Registry** - Manage metadata for datasets
- **Storage Analytics** - Track dataset sizes and record counts
- **AI Insights** - Get recommendations for data analysis techniques
- **Visual Analytics** - Explore data characteristics with Plotly charts

### 💻 IT Operations Domain
- **Ticket System** - Create and manage support tickets
- **Priority Management** - Prioritise critical issues
- **AI Troubleshooting** - Get step-by-step resolution guides
- **Assignment Tracking** - Monitor ticket assignments and resolution

### 🤖 AI Assistant
- **Domain-Specific Expertise** - Specialised AI for each domain
- **Context-Aware Responses** - AI remembers conversation history
- **Streaming Interface** - Real-time response generation
- **Cross-Domain Support** - General AI for multi-domain questions

---

## 🏗️ Architecture

### Object-Oriented Design

```
├── Models (Entity Classes)
│   ├── User - Authentication and role management
│   ├── SecurityIncident - Cybersecurity domain entities
│   ├── Dataset - Data Science domain entities
│   └── ITTicket - IT Operations domain entities
│
├── Services (Business Logic)
│   ├── DatabaseManager - Database connection and query execution
│   ├── AuthManager - User authentication and password security
│   └── AIAssistant - OpenAI API integration with domain prompts
│
└── Views (Streamlit Pages)
    ├── Home.py - Login and registration
    ├── Cybersecurity.py - Security incident dashboard
    ├── Data_Science.py - Dataset management dashboard
    ├── IT_Operations.py - IT ticket dashboard
    └── AI_Assistant.py - General AI chat interface
```

### Database Schema

**Users Table**
- Authentication with bcrypt password hashing
- Role-based access control (user, analyst, admin)

**Cyber Incidents Table**
- Incident tracking with severity levels
- Status management (Open, Investigating, Resolved, Closed)
- Foreign key to users (reported_by)

**Datasets Metadata Table**
- Dataset registry with size and record tracking
- Category classification
- Update history

**IT Tickets Table**
- Support ticket management
- Priority and status tracking
- Assignment to staff members

---

## 🚀 Installation

### Prerequisites

- Python 3.8 or higher
- pip (Python package manager)
- OpenAI API key ([Get one here](https://platform.openai.com/api-keys))

### Step 1: Clone or Download the Project

```bash
# If using Git
git clone <your-repository-url>
cd CW2_M0123456_CST1510

# Or download and extract the ZIP file
```

### Step 2: Create Virtual Environment (Recommended)

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS/Linux
python3 -m venv venv
source venv/bin/activate
```

### Step 3: Install Dependencies

```bash
pip install -r requirements.txt
```

### Step 4: Configure Secrets

Create `.streamlit/secrets.toml` with your API key:

```toml
OPENAI_API_KEY = "sk-proj-your-actual-key-here"
DB_PATH = "DATA/intelligence_platform.db"
```

**⚠️ IMPORTANT:** Never commit this file to Git!

### Step 5: Set Up Database

```bash
python setup_database.py
```

This will:
- Create all database tables
- Create demo user accounts
- Load sample data

### Step 6: Run the Application

```bash
streamlit run Home.py
```

The application will open in your browser at `http://localhost:8501`

---

## ⚙️ Configuration

### Environment Variables

All secrets are managed in `.streamlit/secrets.toml`:

```toml
# OpenAI API Configuration
OPENAI_API_KEY = "your-api-key-here"

# Database Configuration
DB_PATH = "DATA/intelligence_platform.db"
```

### Security Settings

- **Password Hashing:** bcrypt with automatic salt generation
- **SQL Injection Protection:** Parameterised queries throughout
- **Session Management:** Streamlit session state for authentication
- **API Key Security:** Stored in secrets.toml (gitignored)

---

## 📖 Usage

### 1. Login

- Navigate to `http://localhost:8501`
- Use one of the demo accounts (see below)
- Or register a new account

### 2. Navigate Domains

Use the sidebar to access:
- 🛡️ **Cybersecurity** - View and manage security incidents
- 📊 **Data Science** - Explore and analyse datasets
- 💻 **IT Operations** - Manage support tickets
- 🤖 **AI Assistant** - Chat with domain-specific AI

### 3. Use AI Features

In each domain dashboard:
1. Select an item (incident/dataset/ticket)
2. Click "Analyse with AI"
3. Get expert recommendations
4. Ask follow-up questions

### 4. General AI Chat

Go to the AI Assistant page for:
- Cross-domain questions
- General guidance
- Learning about platform features

---

## 📁 Project Structure

```
CW2_M0123456_CST1510/
│
├── app/
│   ├── models/                  # Entity classes (OOP)
│   │   ├── user.py
│   │   ├── security_incident.py
│   │   ├── dataset.py
│   │   └── it_ticket.py
│   │
│   ├── services/                # Business logic
│   │   ├── database_manager.py
│   │   ├── auth_manager.py
│   │   └── ai_assistant.py
│   │
│   └── data/                    # Database schema
│       └── schema.py
│
├── pages/                       # Streamlit pages
│   ├── 1_🛡️_Cybersecurity.py
│   ├── 2_📊_Data_Science.py
│   ├── 3_💻_IT_Operations.py
│   └── 4_🤖_AI_Assistant.py
│
├── DATA/                        # Data files
│   ├── intelligence_platform.db
│   ├── cyber_incidents.csv (optional)
│   ├── datasets_metadata.csv (optional)
│   └── it_tickets.csv (optional)
│
├── .streamlit/
│   └── secrets.toml             # API keys (DO NOT COMMIT)
│
├── Home.py                      # Main entry point
├── setup_database.py            # Database setup script
├── requirements.txt             # Python dependencies
├── .gitignore                   # Git ignore rules
└── README.md                    # This file
```

---

## 🔐 Demo Accounts

After running `setup_database.py`, these accounts are available:

| Username | Password | Role | Access Level |
|----------|----------|------|--------------|
| `admin` | `AdminPass123!` | Admin | Full access to all features |
| `analyst` | `SecurePass123!` | Analyst | Enhanced analysis capabilities |
| `user` | `UserPass123!` | User | Standard access |
| `alice` | `AlicePass123!` | Analyst | Sample analyst account |
| `bob` | `BobPass123!` | User | Sample user account |

**Security Note:** Change these passwords in a production environment!

---

## 🛠️ Technologies Used

### Core Framework
- **Streamlit** - Web application framework
- **Python 3.8+** - Programming language

### Database
- **SQLite** - Embedded database
- **sqlite3** - Python database interface

### Authentication
- **bcrypt** - Secure password hashing

### AI Integration
- **OpenAI GPT-4o** - AI-powered analysis
- **openai** Python library

### Data & Visualisation
- **pandas** - Data manipulation
- **Plotly** - Interactive charts
- **NumPy** - Numerical operations

### Development
- **PyCharm** - IDE
- **Git** - Version control

---

## 🐛 Troubleshooting

### "ModuleNotFoundError"
**Solution:** Make sure you've activated the virtual environment and installed dependencies:
```bash
pip install -r requirements.txt
```

### "AuthenticationError: Invalid API Key"
**Solution:** Check that your `.streamlit/secrets.toml` has the correct API key format:
```toml
OPENAI_API_KEY = "sk-proj-..."
```

### "Database is locked"
**Solution:** Close all connections to the database and restart the application.

### Pages not showing in sidebar
**Solution:** Make sure all page files in the `pages/` directory start with a number (e.g., `1_`, `2_`, etc.)

---

## 📝 License

This project is created for educational purposes as part of CST1510 coursework.

---

## 👨‍💻 Author

**Student ID:** M0123456  
**Course:** CST1510 - Programming for Data Science  
**Institution:** Middlesex University  
**Year:** 2024

---

## 🙏 Acknowledgements

- Streamlit for the excellent web framework
- OpenAI for GPT-4o API access
- Plotly for interactive visualisations
- Week 8, 9, 10, 11 lab materials and tutorials

---

**🚀 Ready to explore the Multi-Domain Intelligence Platform!**

For questions or issues, please contact your course instructor.