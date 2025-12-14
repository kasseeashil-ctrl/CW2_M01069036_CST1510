# Multi-Domain Intelligence Platform

A web application I built for managing cybersecurity incidents, datasets, and IT support tickets. It's built with Streamlit and Python, and I've tried to apply proper Object-Oriented design throughout.

## What's This All About?

This platform brings together three IT domains into one place:

- **Cybersecurity** — Track security incidents, analyse threats, and get AI-powered recommendations
- **Data Science** — Manage datasets, run analytics, and get ML suggestions
- **IT Operations** — Handle support tickets, troubleshoot issues, and monitor workloads

The whole thing uses role-based access control, so people only see what's relevant to their job. There's also an AI assistant (powered by Google Gemini) that can analyse data and give recommendations for each domain.

## How It's Built

I've structured the application in layers, which keeps things organised and makes the code easier to maintain:

```
┌─────────────────────────────────────────────────────────────┐
│                    Presentation Layer                        │
│         (Streamlit Pages: Home.py, pages/*.py)              │
├─────────────────────────────────────────────────────────────┤
│                     Service Layer                            │
│    (AuthManager, DatabaseManager, AIAssistant)              │
├─────────────────────────────────────────────────────────────┤
│                      Model Layer                             │
│      (User, SecurityIncident, Dataset, ITTicket)            │
├─────────────────────────────────────────────────────────────┤
│                      Data Layer                              │
│           (SQLite Database, Schema Definitions)             │
└─────────────────────────────────────────────────────────────┘
```

### Design Patterns I've Used

| Pattern | Where It's Used | Why I Used It |
|---------|-----------------|---------------|
| **Singleton** | `DatabaseManager` with `@st.cache_resource` | So there's only one database connection shared across the app |
| **Factory** | `AuthManager.login_user()` | Creates the right type of User object based on their role |
| **Repository** | `DatabaseManager` | Keeps all the database stuff separate from the business logic |
| **Strategy** | Role-based page routing | Different users get different behaviours |

## The Object-Oriented Bits

This is where I've tried to apply what I've learnt about OOP. Let me walk you through the main parts.

### User Classes (Inheritance and Polymorphism)

The user system is probably the best example of OOP in this project. I've got a base `User` class, and then specific classes for each role that inherit from it.

```python
class User:
    """
    Base class for all user types.
    This defines what every user should be able to do.
    """
    
    def __init__(self, user_id, username, role):
        # I've made these protected (with underscore) to encourage 
        # using the getter methods instead of accessing directly
        self._user_id = user_id
        self._username = username
        self._role = role
    
    def get_username(self):
        """Returns the username - this is encapsulation in action."""
        return self._username
    
    def get_role(self):
        return self._role
    
    def get_home_page(self):
        """Each subclass will override this to return their own home page."""
        raise NotImplementedError("Subclasses must implement this")
    
    def get_role_display_name(self):
        """Returns a nice readable name for the role."""
        raise NotImplementedError("Subclasses must implement this")
    
    def has_access_to(self, domain):
        """Checks if this user can access a particular domain."""
        raise NotImplementedError("Subclasses must implement this")
```

Then each role has its own class that fills in the specifics:

```python
class CybersecurityAnalyst(User):
    """For people working in the security team."""
    
    def get_home_page(self):
        return "pages/1_🛡️_Cybersecurity.py"
    
    def get_role_display_name(self):
        return "Cybersecurity Analyst"
    
    def has_access_to(self, domain):
        return domain == "cybersecurity"


class DataScientist(User):
    """For the data science folks."""
    
    def get_home_page(self):
        return "pages/2_📊_Data_Science.py"
    
    def get_role_display_name(self):
        return "Data Scientist"
    
    def has_access_to(self, domain):
        return domain == "datascience"


class ITEngineer(User):
    """For IT operations staff."""
    
    def get_home_page(self):
        return "pages/3_💻_IT_Operations.py"
    
    def get_role_display_name(self):
        return "IT Operations Engineer"
    
    def has_access_to(self, domain):
        return domain == "itoperations"


class Administrator(User):
    """Admins can see everything."""
    
    def get_home_page(self):
        return "pages/1_🛡️_Cybersecurity.py"
    
    def get_role_display_name(self):
        return "Administrator"
    
    def has_access_to(self, domain):
        return True  # They've got the keys to the kingdom
```

**What OOP concepts does this show?**

- **Encapsulation** — The attributes are protected and accessed through methods
- **Inheritance** — All the user types inherit from the base `User` class
- **Polymorphism** — Each subclass has its own version of methods like `get_home_page()`
- **Abstraction** — The base class defines what users should do, without saying how

### Domain Models

These are the classes that represent the actual data in the system:

```python
class SecurityIncident:
    """Represents a security incident that's been reported."""
    
    def __init__(self, incident_id, date, incident_type, severity, 
                 status, description, reported_by):
        self._id = incident_id
        self._date = date
        self._incident_type = incident_type
        self._severity = severity
        self._status = status
        self._description = description
        self._reported_by = reported_by
    
    def is_critical(self):
        """Quick check to see if this needs immediate attention."""
        return self._severity in ["Critical", "High"]
    
    def is_resolved(self):
        """Has this been dealt with?"""
        return self._status in ["Resolved", "Closed"]
    
    def to_dict(self):
        """Handy for when we need to save to the database."""
        return {
            "date": self._date,
            "incident_type": self._incident_type,
            "severity": self._severity,
            "status": self._status,
            "description": self._description,
            "reported_by": self._reported_by
        }


class Dataset:
    """Represents metadata about a dataset in the catalogue."""
    
    def __init__(self, dataset_id, name, category, source, 
                 last_updated, record_count, file_size_mb):
        self._id = dataset_id
        self._name = name
        self._category = category
        self._source = source
        self._last_updated = last_updated
        self._record_count = record_count
        self._file_size_mb = file_size_mb
    
    def get_size_formatted(self):
        """Returns the file size in a readable format."""
        if self._file_size_mb >= 1000:
            return f"{self._file_size_mb / 1000:.2f} GB"
        return f"{self._file_size_mb:.2f} MB"


class ITTicket:
    """Represents a support ticket from the IT helpdesk."""
    
    def __init__(self, id, ticket_id, priority, status, category,
                 subject, description, created_date, resolved_date, assigned_to):
        self._id = id
        self._ticket_id = ticket_id
        self._priority = priority
        self._status = status
        self._category = category
        self._subject = subject
        self._description = description
        self._created_date = created_date
        self._resolved_date = resolved_date
        self._assigned_to = assigned_to
    
    def calculate_resolution_time(self):
        """Works out how long it took to fix this ticket."""
        if self._resolved_date and self._created_date:
            return self._resolved_date - self._created_date
        return None
    
    def is_overdue(self, sla_hours):
        """Checks if we've breached the SLA on this one."""
        # Would contain the actual SLA checking logic
        pass
```

### The Service Layer

This is where the business logic lives. I've tried to keep it separate from both the UI and the database.

#### DatabaseManager (Repository Pattern)

This class handles all the database operations. The idea is that the rest of the code doesn't need to know anything about SQL — it just calls methods on this class.

```python
class DatabaseManager:
    """
    Handles all the database stuff.
    
    I've used the Repository pattern here, which basically means
    this class is the only thing that talks to the database directly.
    """
    
    def __init__(self, db_path):
        self._db_path = db_path
        self._connection = None
    
    def connect(self):
        """Opens a connection to the database."""
        self._connection = sqlite3.connect(
            self._db_path, 
            check_same_thread=False
        )
        return self._connection
    
    def get_connection(self):
        """Returns the existing connection, or creates one if needed."""
        if self._connection is None:
            self.connect()
        return self._connection
    
    def execute_query(self, query, params=None):
        """For INSERT, UPDATE, DELETE operations."""
        cursor = self._connection.cursor()
        if params:
            cursor.execute(query, params)
        else:
            cursor.execute(query)
        self._connection.commit()
        return cursor.lastrowid
    
    def fetch_all(self, query, params=None):
        """Runs a SELECT and gives back all the results."""
        cursor = self._connection.cursor()
        if params:
            cursor.execute(query, params)
        else:
            cursor.execute(query)
        return cursor.fetchall()
    
    def fetch_one(self, query, params=None):
        """Runs a SELECT and gives back just one result."""
        cursor = self._connection.cursor()
        if params:
            cursor.execute(query, params)
        else:
            cursor.execute(query)
        return cursor.fetchone()
    
    def close(self):
        """Closes the connection when we're done."""
        if self._connection:
            self._connection.close()
            self._connection = None
```

#### AuthManager (Factory Pattern)

This handles logging in and registering users. The interesting bit is how it creates different User objects depending on what role someone has — that's the Factory pattern.

```python
class AuthManager:
    """
    Handles user authentication.
    
    The Factory pattern comes in when we log someone in — we create
    the right type of User object based on their role.
    """
    
    def __init__(self, db_manager):
        # This is dependency injection — we pass in the database
        # manager rather than creating it ourselves
        self._db = db_manager
    
    def register_user(self, username, password, role):
        """Creates a new user account."""
        # Check if username is already taken
        existing = self._db.fetch_one(
            "SELECT id FROM users WHERE username = ?", 
            (username,)
        )
        if existing:
            return False, "Username already exists"
        
        # Hash the password properly with bcrypt
        password_hash = bcrypt.hashpw(
            password.encode('utf-8'), 
            bcrypt.gensalt()
        ).decode('utf-8')
        
        # Save to database
        self._db.execute_query(
            "INSERT INTO users (username, password_hash, role) VALUES (?, ?, ?)",
            (username, password_hash, role)
        )
        return True, "Account created successfully"
    
    def login_user(self, username, password):
        """
        Checks credentials and returns the right type of User object.
        
        This is where the Factory pattern kicks in.
        """
        user_data = self._db.fetch_one(
            "SELECT id, username, password_hash, role FROM users WHERE username = ?",
            (username,)
        )
        
        if not user_data:
            return False, None, "Invalid username or password"
        
        user_id, db_username, password_hash, role = user_data
        
        # Check the password
        if not bcrypt.checkpw(
            password.encode('utf-8'), 
            password_hash.encode('utf-8')
        ):
            return False, None, "Invalid username or password"
        
        # Here's the factory bit — create the right type of user
        user = self._create_user(user_id, db_username, role)
        return True, user, "Login successful"
    
    def _create_user(self, user_id, username, role):
        """
        Factory method — creates the appropriate User subclass.
        """
        role_mapping = {
            "cybersecurity": CybersecurityAnalyst,
            "datascience": DataScientist,
            "itoperations": ITEngineer,
            "admin": Administrator
        }
        
        user_class = role_mapping.get(role, User)
        return user_class(user_id, username, role)
```

#### AIAssistant

This wraps the Google Gemini API and provides domain-specific analysis:

```python
class AIAssistant:
    """
    Provides AI-powered analysis using Google's Gemini.
    
    I've set it up so it gives different types of analysis
    depending on which domain you're working in.
    """
    
    def __init__(self, api_key):
        self._api_key = api_key
        self._model = None
        self._configure()
    
    def _configure(self):
        """Sets up the Gemini client."""
        genai.configure(api_key=self._api_key)
        self._model = genai.GenerativeModel('gemini-2.0-flash')
    
    def analyse_dashboard(self, domain, metrics_data):
        """
        Gets AI analysis of the dashboard metrics.
        The prompt changes depending on which domain you're in.
        """
        prompt = self._build_dashboard_prompt(domain, metrics_data)
        response = self._model.generate_content(prompt, stream=True)
        return response
    
    def analyse_item(self, domain, item_data):
        """Gets detailed analysis of a specific record."""
        prompt = self._build_item_prompt(domain, item_data)
        response = self._model.generate_content(prompt, stream=True)
        return response
    
    def _build_dashboard_prompt(self, domain, data):
        """Builds the right prompt for each domain."""
        prompts = {
            "cybersecurity": f"Analyse these security metrics: {data}. "
                           f"Identify potential threats and recommend actions.",
            "datascience": f"Analyse these dataset metrics: {data}. "
                          f"Suggest ML opportunities and data quality improvements.",
            "itoperations": f"Analyse these IT metrics: {data}. "
                           f"Identify SLA risks and suggest optimisations."
        }
        return prompts.get(domain, f"Analyse: {data}")
```

### How Sessions Work

Streamlit has this handy session state feature that I've used to keep track of who's logged in:

```python
# Set up the session variables when the app starts
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "username" not in st.session_state:
    st.session_state.username = ""
if "user_role" not in st.session_state:
    st.session_state.user_role = ""
if "user_object" not in st.session_state:
    st.session_state.user_object = None

# When someone logs in successfully
st.session_state.logged_in = True
st.session_state.username = user.get_username()
st.session_state.user_role = user.get_role()
st.session_state.user_object = user  # This stores the actual User object
```

The nice thing about storing the `user_object` is that we can call methods on it later, and polymorphism means we get the right behaviour regardless of which type of user it is.

## Getting It Running

### What You'll Need

- Python 3.8 or higher
- A Google Gemini API key

### Setup Steps

1. **Clone the repository:**
   ```bash
   git clone https://github.com/kasseeashil-ctrl/CW2_M01069036_CST1510.git
   cd CW2_M01069036_CST1510
   ```

2. **Create a virtual environment:**
   ```bash
   # On Windows
   python -m venv venv
   venv\Scripts\activate
   
   # On macOS/Linux
   python3 -m venv venv
   source venv/bin/activate
   ```

3. **Install the dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up your secrets:**
   
   Create a file at `.streamlit/secrets.toml` with:
   ```toml
   GEMINI_API_KEY = "your-api-key-here"
   DB_PATH = "DATA/intelligence_platform.db"
   ```

5. **Set up the database:**
   ```bash
   python setup_database.py
   ```

6. **Run it:**
   ```bash
   streamlit run Home.py
   ```

It should open automatically at `http://localhost:8501`

## Test Accounts

The setup script creates a few accounts you can use to test things:

| Role | Username | Password | What They Can Access |
|------|----------|----------|---------------------|
| Cybersecurity Analyst | `cyber_analyst` | `CyberPass123!` | Security incidents |
| Data Scientist | `data_scientist` | `DataPass123!` | Dataset management |
| IT Engineer | `it_engineer` | `ITPass123!` | IT tickets |
| Administrator | `admin` | `AdminPass123!` | Everything |

## What Each Domain Does

**Cybersecurity Dashboard:**
- View and track security incidents
- Filter by severity, status, and type
- Get AI-powered threat analysis
- Create and update incidents

**Data Science Dashboard:**
- Browse the dataset catalogue
- View analytics and visualisations
- Get ML recommendations from the AI
- Manage dataset metadata

**IT Operations Dashboard:**
- Manage the ticket queue
- Track priorities and SLAs
- View workload analytics
- Get AI troubleshooting suggestions

## Project Structure

```
CW2_M01069036_CST1510/
├── Home.py                     # The login page (entry point)
├── setup_database.py           # Sets up the database with test data
├── requirements.txt            # Python packages needed
│
├── app/
│   ├── models/                 # The OOP model classes
│   │   ├── user.py             # User class hierarchy
│   │   ├── security_incidents.py
│   │   ├── dataset.py
│   │   └── it_tickets.py
│   │
│   ├── services/               # Business logic
│   │   ├── database_manager.py # Repository pattern
│   │   ├── auth_manager.py     # Factory pattern
│   │   └── ai_assistant.py     # Gemini integration
│   │
│   └── data/
│       └── schema.py           # Database table definitions
│
├── pages/                      # The different dashboards
│   ├── 1_🛡️_Cybersecurity.py
│   ├── 2_📊_Data_Science.py
│   ├── 3_💻_IT_Operations.py
│   └── 4_🤖_AI_Assistant.py
│
├── DATA/
│   └── intelligence_platform.db
│
└── .streamlit/
    └── secrets.toml            # API keys (not in git)
```

## Database Design

Here's how the tables relate to each other:

```
┌─────────────┐     ┌──────────────────┐     ┌─────────────────┐
│   users     │     │ cyber_incidents  │     │datasets_metadata│
├─────────────┤     ├──────────────────┤     ├─────────────────┤
│ id (PK)     │     │ id (PK)          │     │ id (PK)         │
│ username    │◄────│ reported_by      │     │ dataset_name    │
│ password_hash│     │ date             │     │ category        │
│ role        │     │ incident_type    │     │ source          │
└─────────────┘     │ severity         │     │ last_updated    │
                    │ status           │     │ record_count    │
                    │ description      │     │ file_size_mb    │
                    └──────────────────┘     └─────────────────┘
                    
                    ┌─────────────────┐
                    │   it_tickets    │
                    ├─────────────────┤
                    │ id (PK)         │
                    │ ticket_id       │
                    │ priority        │
                    │ status          │
                    │ category        │
                    │ subject         │
                    │ description     │
                    │ created_date    │
                    │ resolved_date   │
                    │ assigned_to     │
                    └─────────────────┘
```

### The SQL

```sql
CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    role TEXT NOT NULL
);

CREATE TABLE cyber_incidents (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    date TEXT NOT NULL,
    incident_type TEXT NOT NULL,
    severity TEXT NOT NULL,
    status TEXT NOT NULL,
    description TEXT,
    reported_by TEXT
);

CREATE TABLE datasets_metadata (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    dataset_name TEXT NOT NULL,
    category TEXT,
    source TEXT,
    last_updated TEXT,
    record_count INTEGER,
    file_size_mb REAL
);

CREATE TABLE it_tickets (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    ticket_id TEXT UNIQUE NOT NULL,
    priority TEXT NOT NULL,
    status TEXT NOT NULL,
    category TEXT,
    subject TEXT NOT NULL,
    description TEXT,
    created_date TEXT NOT NULL,
    resolved_date TEXT,
    assigned_to TEXT
);
```

## Technologies Used

| What | Why |
|------|-----|
| **Streamlit** | Makes building web UIs in Python dead simple |
| **SQLite** | Lightweight database that doesn't need a server |
| **Plotly** | Nice interactive charts |
| **bcrypt** | Proper password hashing |
| **Google Gemini** | The AI that powers the analysis features |
| **Python 3.8+** | Because that's what I know best |

## If Something Goes Wrong

| Problem | What To Try |
|---------|-------------|
| **ModuleNotFoundError** | Make sure you've activated the virtual environment and run `pip install -r requirements.txt` |
| **AI features not working** | Double-check your API key in `.streamlit/secrets.toml` |
| **Access Denied** | You're trying to access a domain your role doesn't have permission for — try logging in as admin |
| **Database errors** | Delete `DATA/intelligence_platform.db` and run `python setup_database.py` again |
| **bcrypt won't install** | Try `pip install bcrypt --no-binary bcrypt` or make sure you've got build tools installed |

## About

**Student ID:** M01069036  
**Module:** CST1510  
**University:** Middlesex University

## Licence

This was built as coursework for CST1510. Feel free to have a look at the code, but please don't submit it as your own work!
