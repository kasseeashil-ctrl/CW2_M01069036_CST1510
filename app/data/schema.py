"""
Database Schema Definition
Creates all tables for the Multi-Domain Intelligence Platform
"""

def create_users_table(conn):
    """
    Create the users table for authentication.
    
    Stores user credentials with bcrypt hashed passwords and role-based access.
    """
    cursor = conn.cursor()
    
    create_table_sql = """
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT NOT NULL UNIQUE,
        password_hash TEXT NOT NULL,
        role TEXT DEFAULT 'user',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """
    
    cursor.execute(create_table_sql)
    conn.commit()
    print("✅ Users table created successfully")


def create_cyber_incidents_table(conn):
    """
    Create the cyber_incidents table for the Cybersecurity domain.
    
    Tracks security incidents with severity levels, status, and reporting details.
    """
    cursor = conn.cursor()
    
    create_table_sql = """
    CREATE TABLE IF NOT EXISTS cyber_incidents (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        date TEXT NOT NULL,
        incident_type TEXT NOT NULL,
        severity TEXT NOT NULL,
        status TEXT NOT NULL,
        description TEXT,
        reported_by TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (reported_by) REFERENCES users(username)
    )
    """
    
    cursor.execute(create_table_sql)
    conn.commit()
    print("✅ Cyber incidents table created successfully")


def create_datasets_metadata_table(conn):
    """
    Create the datasets_metadata table for the Data Science domain.
    
    Manages information about available datasets including size, source, and update frequency.
    """
    cursor = conn.cursor()
    
    create_table_sql = """
    CREATE TABLE IF NOT EXISTS datasets_metadata (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        dataset_name TEXT NOT NULL,
        category TEXT,
        source TEXT,
        last_updated TEXT,
        record_count INTEGER,
        file_size_mb REAL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """
    
    cursor.execute(create_table_sql)
    conn.commit()
    print("✅ Datasets metadata table created successfully")


def create_it_tickets_table(conn):
    """
    Create the it_tickets table for the IT Operations domain.
    
    Tracks support tickets with priority levels, assignment, and resolution status.
    """
    cursor = conn.cursor()
    
    create_table_sql = """
    CREATE TABLE IF NOT EXISTS it_tickets (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        ticket_id TEXT UNIQUE NOT NULL,
        priority TEXT NOT NULL,
        status TEXT NOT NULL,
        category TEXT,
        subject TEXT NOT NULL,
        description TEXT,
        created_date TEXT,
        resolved_date TEXT,
        assigned_to TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """
    
    cursor.execute(create_table_sql)
    conn.commit()
    print("✅ IT tickets table created successfully")


def create_all_tables(conn):
    """
    Create all database tables in the correct order.
    
    This ensures foreign key relationships are properly established.
    """
    print("\n🔨 Creating database tables...")
    print("=" * 60)
    
    create_users_table(conn)
    create_cyber_incidents_table(conn)
    create_datasets_metadata_table(conn)
    create_it_tickets_table(conn)
    
    print("=" * 60)
    print("✅ All tables created successfully!\n")