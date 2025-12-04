"""
Authentication Manager Service
Handles user registration, login, and password security using bcrypt
"""

import bcrypt
from typing import Optional, Tuple
from app.models.user import User
from app.services.database_manager import DatabaseManager


class AuthManager:
    """
    Manages user authentication with secure password hashing.
    
    Uses bcrypt for password hashing and provides methods for
    registering new users and authenticating existing ones.
    """
    
    def __init__(self, db_manager: DatabaseManager):
        """
        Initialise the AuthManager with a database connection.
        
        Args:
            db_manager: An instance of DatabaseManager for database operations
        """
        self._db = db_manager
    
    def _hash_password(self, plain_password: str) -> str:
        """
        Hash a plain text password using bcrypt.
        
        Args:
            plain_password: The password to hash
            
        Returns:
            The hashed password as a UTF-8 string
        """
        password_bytes = plain_password.encode('utf-8')
        salt = bcrypt.gensalt()
        hashed = bcrypt.hashpw(password_bytes, salt)
        return hashed.decode('utf-8')
    
    def _verify_password(self, plain_password: str, password_hash: str) -> bool:
        """
        Verify a plain text password against a bcrypt hash.
        
        Args:
            plain_password: The password to verify
            password_hash: The stored bcrypt hash
            
        Returns:
            True if password matches, False otherwise
        """
        password_bytes = plain_password.encode('utf-8')
        hash_bytes = password_hash.encode('utf-8')
        return bcrypt.checkpw(password_bytes, hash_bytes)
    
    def register_user(
        self, 
        username: str, 
        password: str, 
        role: str = "user"
    ) -> Tuple[bool, str]:
        """
        Register a new user in the system.
        
        Args:
            username: Desired username (must be unique)
            password: Plain text password (will be hashed)
            role: User role (default: 'user', options: 'user', 'analyst', 'admin')
            
        Returns:
            Tuple of (success: bool, message: str)
            
        Example:
            success, message = auth.register_user("alice", "SecurePass123!", "analyst")
            if success:
                print(message)  # "User 'alice' registered successfully"
        """
        # Validate input
        if not username or not password:
            return False, "Username and password cannot be empty"
        
        if len(password) < 8:
            return False, "Password must be at least 8 characters long"
        
        # Check if username already exists
        existing_user = self._db.fetch_one(
            "SELECT username FROM users WHERE username = ?",
            (username,)
        )
        
        if existing_user:
            return False, f"Username '{username}' already exists"
        
        # Hash the password
        password_hash = self._hash_password(password)
        
        # Insert new user into database
        try:
            self._db.execute_query(
                "INSERT INTO users (username, password_hash, role) VALUES (?, ?, ?)",
                (username, password_hash, role)
            )
            return True, f"User '{username}' registered successfully"
        except Exception as e:
            return False, f"Registration failed: {str(e)}"
    
    def login_user(
        self, 
        username: str, 
        password: str
    ) -> Tuple[bool, Optional[User], str]:
        """
        Authenticate a user and return a User object if successful.
        
        Args:
            username: The username to authenticate
            password: The plain text password to verify
            
        Returns:
            Tuple of (success: bool, user: User or None, message: str)
            
        Example:
            success, user, message = auth.login_user("alice", "SecurePass123!")
            if success:
                print(f"Welcome, {user.get_username()}!")
            else:
                print(message)  # "Invalid username or password"
        """
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
        
        # Unpack row data
        user_id, db_username, password_hash, role = row
        
        # Verify password
        if not self._verify_password(password, password_hash):
            return False, None, "Invalid username or password"
        
        # Create User object
        user = User(username=db_username, password_hash=password_hash, role=role)
        
        return True, user, f"Welcome back, {username}!"
    
    def get_user_by_username(self, username: str) -> Optional[User]:
        """
        Retrieve a User object by username.
        
        Args:
            username: The username to look up
            
        Returns:
            User object if found, None otherwise
        """
        row = self._db.fetch_one(
            "SELECT username, password_hash, role FROM users WHERE username = ?",
            (username,)
        )
        
        if row is None:
            return None
        
        db_username, password_hash, role = row
        return User(username=db_username, password_hash=password_hash, role=role)
    
    def change_password(
        self, 
        username: str, 
        old_password: str, 
        new_password: str
    ) -> Tuple[bool, str]:
        """
        Change a user's password after verifying their current password.
        
        Args:
            username: The username
            old_password: Current password for verification
            new_password: New password to set
            
        Returns:
            Tuple of (success: bool, message: str)
        """
        # Verify old password first
        success, user, message = self.login_user(username, old_password)
        
        if not success:
            return False, "Current password is incorrect"
        
        if len(new_password) < 8:
            return False, "New password must be at least 8 characters long"
        
        # Hash new password
        new_password_hash = self._hash_password(new_password)
        
        # Update in database
        try:
            self._db.execute_query(
                "UPDATE users SET password_hash = ? WHERE username = ?",
                (new_password_hash, username)
            )
            return True, "Password changed successfully"
        except Exception as e:
            return False, f"Password change failed: {str(e)}"