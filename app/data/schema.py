"""Database schema Creates all the tables for the platform"""  

def create_users_table(conn):
    """Create users table with bcrypt password hashing"""  #Describes what this function does
    cursor = conn.cursor()  # Create a cursor object to execute SQL commands
    cursor.execute("""  # Execute the SQL query to create the users table
        CREATE TABLE IF NOT EXISTS users (  # Create table only if it doesn't exist
            id INTEGER PRIMARY KEY AUTOINCREMENT,  # Auto-incrementing primary key
            username TEXT NOT NULL UNIQUE,  # Username must be unique and not null
            password_hash TEXT NOT NULL,  # Store hashed passwords (not plain text)
            role TEXT DEFAULT 'user',  # Default role is 'user'
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP  # Auto-set timestamp on creation
        )
    """)
    conn.commit()  # Save (commit) the changes to the database
    print("✅ Users table created")  # Printing a success message


def create_cyber_incidents_table(conn):
    """Create cyber incidents table for security domain"""  #Function docstring
    cursor = conn.cursor()  # Create cursor for SQL execution.
    cursor.execute("""  # Execute SQL to create cyber_incidents table
        CREATE TABLE IF NOT EXISTS cyber_incidents (  # Create table if not exists
            id INTEGER PRIMARY KEY AUTOINCREMENT,  # Auto-incrementing primary key
            date TEXT NOT NULL,  # Date of the incident
            incident_type TEXT NOT NULL,  # Type/category of incident
            severity TEXT NOT NULL,  # How severe the incident was
            status TEXT NOT NULL,  # Current status (open, closed, etc.)
            description TEXT,  # Detailed description (optional)
            reported_by TEXT,  # Who reported the incident
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,  # Auto timestamp
            FOREIGN KEY (reported_by) REFERENCES users(username)  # Link to users table
        )
    """)
    conn.commit()# Commit the table creation
    print("✅ Cyber incidents table created")  #Success message with an emoji 


def create_datasets_metadata_table(conn):
    """Create datasets table for data science domain"""  # Function docstring
    cursor = conn.cursor()  # Create cursor object
    cursor.execute("""  # Execute SQL for datasets metadata table
        CREATE TABLE IF NOT EXISTS datasets_metadata (  # Create if not exists
            id INTEGER PRIMARY KEY AUTOINCREMENT,  # Auto-incrementing primary key
            dataset_name TEXT NOT NULL,  # Name of the dataset
            category TEXT,  # Category/type of data (optional)
            source TEXT,  # Where the data came from (optional)
            last_updated TEXT,  # When the data was last updated
            record_count INTEGER,  # Number of records/rows in dataset
            file_size_mb REAL,  # Size in megabytes (decimal number)
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP  # Auto timestamp
        )
    """)
    conn.commit()  # Commit changes to database
    print("✅ Datasets metadata table created")  # Success message


def create_it_tickets_table(conn):
    """Create IT tickets table for operations domain"""  # Function docstring
    cursor = conn.cursor()  # Create cursor for SQL execution
    cursor.execute("""  # Execute SQL to create IT tickets table
        CREATE TABLE IF NOT EXISTS it_tickets (  # Create if not exists
            id INTEGER PRIMARY KEY AUTOINCREMENT,  # Auto-incrementing primary key
            ticket_id TEXT UNIQUE NOT NULL,  # Unique ticket identifier
            priority TEXT NOT NULL,  # Priority level (high, medium, low)
            status TEXT NOT NULL,  # Current status (open, in progress, resolved)
            category TEXT,  # Category/type of ticket (optional)
            subject TEXT NOT NULL,  # Brief subject/title of ticket
            description TEXT,  # Detailed description (optional)
            created_date TEXT,  # When the ticket was created
            resolved_date TEXT,  # When the ticket was resolved (optional)
            assigned_to TEXT,  # Who the ticket is assigned to (optional)
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP  # Auto timestamp
        )
    """)
    conn.commit()  # Commit the table creation
    print("✅ IT tickets table created")  # Success message


def create_all_tables(conn):
    """Create all database tables in correct order"""  # Function docstring
    print("\n🔨 Creating database tables...")  #Start message with an hammer emoji
    print("=" * 60)  # Print separator line (60 equals signs)
    create_users_table(conn)  # Call function to create users table
    create_cyber_incidents_table(conn)  # Call function to create incidents table
    create_datasets_metadata_table(conn)  # Call function to create datasets table
    create_it_tickets_table(conn)  # Call function to create tickets table
    print("=" * 60)  # Print separator line again
    print("✅ All tables created successfully\n")  # Final success message