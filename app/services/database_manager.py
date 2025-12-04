"""
Database Manager Service
Handles all SQLite database connections and query execution
"""

import sqlite3
from pathlib import Path
from typing import Any, List, Tuple, Optional


class DatabaseManager:
    """
    Manages database connections and provides methods for executing
    queries safely using parameterised statements.
    
    This class follows the Singleton pattern to ensure only one
    database connection exists at a time.
    """
    
    def __init__(self, db_path: str):
        """
        Initialise the DatabaseManager with a database file path.
        
        Args:
            db_path: Path to the SQLite database file
        """
        self._db_path = str(Path(db_path))
        self._connection: Optional[sqlite3.Connection] = None
    
    def connect(self) -> None:
        """
        Establish a connection to the SQLite database.
        Creates the database file if it doesn't exist.
        """
        if self._connection is None:
            self._connection = sqlite3.connect(self._db_path, check_same_thread=False)
            # Enable foreign key constraints (disabled by default in SQLite)
            self._connection.execute("PRAGMA foreign_keys = ON")
            print(f"✅ Connected to database: {self._db_path}")
    
    def close(self) -> None:
        """
        Close the database connection if it's open.
        Always call this when you're done with database operations.
        """
        if self._connection is not None:
            self._connection.close()
            self._connection = None
            print("🔒 Database connection closed")
    
    def execute_query(
        self, 
        sql: str, 
        params: Tuple[Any, ...] = ()
    ) -> sqlite3.Cursor:
        """
        Execute a write query (INSERT, UPDATE, DELETE) with automatic commit.
        
        Args:
            sql: SQL query string with ? placeholders
            params: Tuple of parameters to safely substitute into the query
            
        Returns:
            The cursor object after execution
            
        Example:
            db.execute_query(
                "INSERT INTO users (username, role) VALUES (?, ?)",
                ("alice", "analyst")
            )
        """
        if self._connection is None:
            self.connect()
        
        cursor = self._connection.cursor()
        cursor.execute(sql, params)
        self._connection.commit()
        return cursor
    
    def fetch_one(
        self, 
        sql: str, 
        params: Tuple[Any, ...] = ()
    ) -> Optional[Tuple]:
        """
        Execute a SELECT query and fetch a single row.
        
        Args:
            sql: SQL query string with ? placeholders
            params: Tuple of parameters to safely substitute into the query
            
        Returns:
            A tuple representing the row, or None if no results
            
        Example:
            row = db.fetch_one(
                "SELECT * FROM users WHERE username = ?",
                ("alice",)
            )
        """
        if self._connection is None:
            self.connect()
        
        cursor = self._connection.cursor()
        cursor.execute(sql, params)
        return cursor.fetchone()
    
    def fetch_all(
        self, 
        sql: str, 
        params: Tuple[Any, ...] = ()
    ) -> List[Tuple]:
        """
        Execute a SELECT query and fetch all rows.
        
        Args:
            sql: SQL query string with ? placeholders
            params: Tuple of parameters to safely substitute into the query
            
        Returns:
            A list of tuples, each representing a row
            
        Example:
            rows = db.fetch_all(
                "SELECT * FROM cyber_incidents WHERE severity = ?",
                ("High",)
            )
        """
        if self._connection is None:
            self.connect()
        
        cursor = self._connection.cursor()
        cursor.execute(sql, params)
        return cursor.fetchall()
    
    def get_connection(self) -> sqlite3.Connection:
        """
        Get the raw SQLite connection object.
        Useful for pandas operations like pd.read_sql_query().
        
        Returns:
            The active SQLite connection
        """
        if self._connection is None:
            self.connect()
        return self._connection
    
    def __enter__(self):
        """Context manager entry: connect to database."""
        self.connect()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit: close database connection."""
        self.close()