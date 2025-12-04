"""
Database Setup Script
Creates tables, loads sample data, and sets up demo accounts
"""

import pandas as pd
from pathlib import Path
from app.services.database_manager import DatabaseManager
from app.services.auth_manager import AuthManager
from app.data.schema import create_all_tables

# Configuration
DATA_DIR = Path("DATA")
DB_PATH = DATA_DIR / "intelligence_platform.db"

def setup_database():
    """Complete database setup process."""
    
    print("\n" + "=" * 80)
    print("🚀 MULTI-DOMAIN INTELLIGENCE PLATFORM - DATABASE SETUP")
    print("=" * 80)
    
    # Ensure DATA directory exists
    DATA_DIR.mkdir(exist_ok=True)
    print(f"\n📁 Data directory: {DATA_DIR.resolve()}")
    
    # Step 1: Connect to database
    print("\n[1/5] Connecting to database...")
    db = DatabaseManager(str(DB_PATH))
    db.connect()
    print("    ✅ Connected to database")
    
    # Step 2: Create tables
    print("\n[2/5] Creating database tables...")
    create_all_tables(db.get_connection())
    
    # Step 3: Create demo user accounts
    print("\n[3/5] Creating demo user accounts...")
    auth = AuthManager(db)
    
    demo_users = [
        ("admin", "AdminPass123!", "admin"),
        ("analyst", "SecurePass123!", "analyst"),
        ("user", "UserPass123!", "user"),
        ("alice", "AlicePass123!", "analyst"),
        ("bob", "BobPass123!", "user")
    ]
    
    for username, password, role in demo_users:
        success, message = auth.register_user(username, password, role)
        if success:
            print(f"    ✅ Created user: {username} ({role})")
        else:
            print(f"    ⚠️  User {username} already exists")
    
    # Step 4: Load sample data from CSV files
    print("\n[4/5] Loading sample data from CSV files...")
    
    # Load cyber incidents
    incidents_csv = DATA_DIR / "cyber_incidents.csv"
    if incidents_csv.exists():
        try:
            df_incidents = pd.read_csv(incidents_csv)
            df_incidents.to_sql('cyber_incidents', db.get_connection(), if_exists='append', index=False)
            print(f"    ✅ Loaded {len(df_incidents)} cyber incidents")
        except Exception as e:
            print(f"    ⚠️  Could not load cyber_incidents.csv: {e}")
    else:
        print(f"    ℹ️  cyber_incidents.csv not found, creating sample data...")
        create_sample_incidents(db)
    
    # Load datasets metadata
    datasets_csv = DATA_DIR / "datasets_metadata.csv"
    if datasets_csv.exists():
        try:
            df_datasets = pd.read_csv(datasets_csv)
            df_datasets.to_sql('datasets_metadata', db.get_connection(), if_exists='append', index=False)
            print(f"    ✅ Loaded {len(df_datasets)} datasets")
        except Exception as e:
            print(f"    ⚠️  Could not load datasets_metadata.csv: {e}")
    else:
        print(f"    ℹ️  datasets_metadata.csv not found, creating sample data...")
        create_sample_datasets(db)
    
    # Load IT tickets
    tickets_csv = DATA_DIR / "it_tickets.csv"
    if tickets_csv.exists():
        try:
            df_tickets = pd.read_csv(tickets_csv)
            df_tickets.to_sql('it_tickets', db.get_connection(), if_exists='append', index=False)
            print(f"    ✅ Loaded {len(df_tickets)} IT tickets")
        except Exception as e:
            print(f"    ⚠️  Could not load it_tickets.csv: {e}")
    else:
        print(f"    ℹ️  it_tickets.csv not found, creating sample data...")
        create_sample_tickets(db)
    
    # Step 5: Verify setup
    print("\n[5/5] Verifying database setup...")
    verify_database(db)
    
    # Close connection
    db.close()
    
    print("\n" + "=" * 80)
    print("✅ DATABASE SETUP COMPLETE!")
    print("=" * 80)
    print(f"\n📍 Database location: {DB_PATH.resolve()}")
    print("\n🔐 Demo Accounts:")
    print("   • Username: admin    | Password: AdminPass123!    | Role: admin")
    print("   • Username: analyst  | Password: SecurePass123!   | Role: analyst")
    print("   • Username: user     | Password: UserPass123!     | Role: user")
    print("\n🚀 Ready to run: streamlit run Home.py")
    print()


def create_sample_incidents(db):
    """Create sample security incidents if CSV doesn't exist."""
    sample_incidents = [
        ("2024-11-01", "Phishing", "High", "Resolved", "Suspicious email with urgent payment request", "alice"),
        ("2024-11-03", "Malware", "Critical", "Investigating", "Ransomware detected on finance server", "bob"),
        ("2024-11-05", "DDoS", "High", "Open", "Distributed denial of service attack on web portal", "alice"),
        ("2024-11-07", "Data Breach", "Critical", "Investigating", "Unauthorised access to customer database", "admin"),
        ("2024-11-10", "Phishing", "Medium", "Resolved", "Fake Microsoft login page reported", "analyst"),
        ("2024-11-12", "Insider Threat", "High", "Open", "Unusual data export activity detected", "alice"),
        ("2024-11-15", "Malware", "Low", "Closed", "Adware detected on marketing laptop", "user"),
        ("2024-11-18", "Phishing", "High", "Investigating", "CEO impersonation email targeting finance team", "analyst")
    ]
    
    query = """
    INSERT INTO cyber_incidents (date, incident_type, severity, status, description, reported_by)
    VALUES (?, ?, ?, ?, ?, ?)
    """
    
    for incident in sample_incidents:
        db.execute_query(query, incident)
    
    print(f"    ✅ Created {len(sample_incidents)} sample incidents")


def create_sample_datasets(db):
    """Create sample datasets if CSV doesn't exist."""
    sample_datasets = [
        ("Network Traffic Logs Q4 2024", "Network Logs", "Internal SIEM", "2024-11-20", 2500000, 450.5),
        ("Threat Intelligence Feed", "Threat Intelligence", "External API", "2024-11-22", 150000, 25.8),
        ("User Login Patterns", "User Behaviour", "Internal Database", "2024-11-18", 500000, 120.3),
        ("Server Performance Metrics", "System Metrics", "Monitoring Tool", "2024-11-25", 1800000, 380.2),
        ("Security Alerts Archive", "Security Alerts", "Internal SIEM", "2024-11-15", 750000, 95.7),
        ("Firewall Logs", "Network Logs", "Perimeter Security", "2024-11-21", 3200000, 620.4)
    ]
    
    query = """
    INSERT INTO datasets_metadata (dataset_name, category, source, last_updated, record_count, file_size_mb)
    VALUES (?, ?, ?, ?, ?, ?)
    """
    
    for dataset in sample_datasets:
        db.execute_query(query, dataset)
    
    print(f"    ✅ Created {len(sample_datasets)} sample datasets")


def create_sample_tickets(db):
    """Create sample IT tickets if CSV doesn't exist."""
    sample_tickets = [
        ("TICK-0001", "Critical", "Open", "Hardware", "Server overheating alert", "Primary server showing critical temperature warnings", "2024-11-01", None, None),
        ("TICK-0002", "High", "In Progress", "Network", "Slow network connectivity", "Users reporting slow connection speeds in Building A", "2024-11-03", None, "alice"),
        ("TICK-0003", "Medium", "Resolved", "Software", "Application crashes frequently", "CRM software crashes when exporting reports", "2024-11-05", "2024-11-10", "bob"),
        ("TICK-0004", "Low", "Closed", "Access", "Password reset request", "User forgot password for email account", "2024-11-07", "2024-11-08", "user"),
        ("TICK-0005", "High", "Open", "Security", "Unauthorised login attempts", "Multiple failed login attempts detected from unknown IP", "2024-11-12", None, "analyst"),
        ("TICK-0006", "Medium", "In Progress", "Hardware", "Printer not responding", "Office printer showing offline status", "2024-11-15", None, "bob"),
        ("TICK-0007", "Critical", "Open", "Network", "Internet outage in data centre", "Complete loss of internet connectivity", "2024-11-20", None, None),
        ("TICK-0008", "Low", "Resolved", "Software", "Email client synchronisation issue", "Outlook not syncing with server", "2024-11-18", "2024-11-19", "alice")
    ]
    
    query = """
    INSERT INTO it_tickets (ticket_id, priority, status, category, subject, description, created_date, resolved_date, assigned_to)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """
    
    for ticket in sample_tickets:
        db.execute_query(query, ticket)
    
    print(f"    ✅ Created {len(sample_tickets)} sample tickets")


def verify_database(db):
    """Verify that all tables have data."""
    tables = ['users', 'cyber_incidents', 'datasets_metadata', 'it_tickets']
    
    print("\n    📊 Database Summary:")
    print(f"    {'Table':<25} {'Row Count':<15}")
    print("    " + "-" * 40)
    
    for table in tables:
        count = db.fetch_one(f"SELECT COUNT(*) FROM {table}")[0]
        print(f"    {table:<25} {count:<15}")
    
    print()


if __name__ == "__main__":
    setup_database()