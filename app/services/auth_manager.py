"""Authentication manager - Handles user registration and login with bcrypt"""

import bcrypt
from typing import Optional, Tuple
from app.models.user import User
from app.services.database_manager import DatabaseManager


class AuthManager:
    """Manages user authentication with secure password hashing"""
    
    def __init__(self, db_manager: DatabaseManager):
        """Initialise with database manager"""
        self._db = db_manager
    
    def _hash_password(self, plain_password: str) -> str:
        """Hash password using bcrypt"""
        password_bytes = plain_password.encode('utf-8')
        salt = bcrypt.gensalt()
        hashed = bcrypt.hashpw(password_bytes, salt)
        return hashed.decode('utf-8')
    
    def _verify_password(self, plain_password: str, password_hash: str) -> bool:
        """Verify password against bcrypt hash"""
        password_bytes = plain_password.encode('utf-8')
        hash_bytes = password_hash.encode('utf-8')
        return bcrypt.checkpw(password_bytes, hash_bytes)
    
    def register_user(self, username: str, password: str, role: str = "user") -> Tuple[bool, str]:
        """Register new user with hashed password"""
        # Validate input
        if not username or not password:
            return False, "Username and password cannot be empty"
        
        if len(password) < 8:
            return False, "Password must be at least 8 characters long"
        
        # Check if username exists
        existing = self._db.fetch_one(
            "SELECT username FROM users WHERE username = ?",
            (username,)
        )
        
        if existing:
            return False, f"Username '{username}' already exists"
        
        # Hash password and insert user
        password_hash = self._hash_password(password)
        
        try:
            self._db.execute_query(
                "INSERT INTO users (username, password_hash, role) VALUES (?, ?, ?)",
                (username, password_hash, role)
            )
            return True, f"User '{username}' registered successfully"
        except Exception as e:
            return False, f"Registration failed: {str(e)}"
    
    def login_user(self, username: str, password: str) -> Tuple[bool, Optional[User], str]:
        """Authenticate user and return User object if successful"""
        # Validate input
        if not username or not password:
            return False, None, "Username and password cannot be empty"
        
        # Fetch user from database
        row = self._db.fetch_one(
            "SELECT id, username, password_hash, role FROM users WHERE username = ?",
            (username,)
        )
        
        if row is None:
            return False, None, "Invalid username or password"
        
        # Verify password
        user_id, db_username, password_hash, role = row
        
        if not self._verify_password(password, password_hash):
            return False, None, "Invalid username or password"
        
        # Create User object
        user = User(username=db_username, password_hash=password_hash, role=role)
        
        return True, user, f"Welcome back, {username}!"
    
    def get_user_by_username(self, username: str) -> Optional[User]:
        """Retrieve User object by username"""
        row = self._db.fetch_one(
            "SELECT username, password_hash, role FROM users WHERE username = ?",
            (username,)
        )
        
        if row is None:
            return None
        
        db_username, password_hash, role = row
        return User(username=db_username, password_hash=password_hash, role=role)