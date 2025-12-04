"""Database manager service - Handles all SQLite operations"""

import sqlite3
from pathlib import Path
from typing import Any, List, Tuple, Optional


class DatabaseManager:
    """Manages database connections and executes parameterised queries"""
    
    def __init__(self, db_path: str):
        """Initialise with database file path"""
        self._db_path = str(Path(db_path))  # Normalise and store the path
        self._connection: Optional[sqlite3.Connection] = None  
    
    def connect(self) -> None:
        """Establish database connection and enable foreign keys"""
        if self._connection is None:
            self._connection = sqlite3.connect(self._db_path, check_same_thread=False)
            self._connection.execute("PRAGMA foreign_keys = ON")  # Enable FK constraints
            print(f"✅ Connected to database: {self._db_path}")
    
    def close(self) -> None:
        """Close database connection"""
        if self._connection is not None:
            self._connection.close()
            self._connection = None
            print("🔒 Database connection closed")
    
    def execute_query(self, sql: str, params: Tuple[Any, ...] = ()) -> sqlite3.Cursor:
        """Execute write query (INSERT, UPDATE, DELETE) with auto-commit"""
        if self._connection is None:
            self.connect()
        
        cursor = self._connection.cursor()
        cursor.execute(sql, params)  # Parameterised query prevents SQL injection
        self._connection.commit()  # Auto-commit changes
        return cursor
    
    def fetch_one(self, sql: str, params: Tuple[Any, ...] = ()) -> Optional[Tuple]:
        """Execute SELECT query and fetch single row"""
        if self._connection is None:
            self.connect()
        
        cursor = self._connection.cursor()
        cursor.execute(sql, params)
        return cursor.fetchone()  # Returns None if no results
    
    def fetch_all(self, sql: str, params: Tuple[Any, ...] = ()) -> List[Tuple]:
        """Execute SELECT query and fetch all rows"""
        if self._connection is None:
            self.connect()
        
        cursor = self._connection.cursor()
        cursor.execute(sql, params)
        return cursor.fetchall()  # Returns empty list if no results
    
    def get_connection(self) -> sqlite3.Connection:
        """Get raw connection for pandas operations"""
        if self._connection is None:
            self.connect()
        return self._connection
    
    def __enter__(self):
        """Context manager entry for 'with' statement"""
        self.connect()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit - auto closes connection"""
        self.close()