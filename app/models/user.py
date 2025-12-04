
class User:
    """
    Represents an authenticated user with role-based permissions.
    
    Roles define which domains users can access:
    - cybersecurity: Only access Cybersecurity domain
    - datascience: Only access Data Science domain
    - itoperations: Only access IT Operations domain
    - admin: Access all domains and management features
    """
    
    # Define allowed domains for each role
    ROLE_PERMISSIONS = {
        'cybersecurity': ['cybersecurity', 'ai_assistant'],
        'datascience': ['datascience', 'ai_assistant'],
        'itoperations': ['itoperations', 'ai_assistant'],
        'admin': ['cybersecurity', 'datascience', 'itoperations', 'ai_assistant', 'admin_panel']
    }
    
    def __init__(self, username: str, password_hash: str, role: str):
        """
        Initialise a new User instance.
        
        Args:
            username: Unique username for login
            password_hash: Bcrypt hashed password (never store plain text!)
            role: User role (cybersecurity, datascience, itoperations, admin)
        """
        self.__username = username
        self.__password_hash = password_hash
        self.__role = role.lower()
    
    def get_username(self) -> str:
        """Return the user's username."""
        return self.__username
    
    def get_role(self) -> str:
        """Return the user's role."""
        return self.__role
    
    def get_password_hash(self) -> str:
        """Return the password hash (used for verification)."""
        return self.__password_hash
    
    def can_access_domain(self, domain: str) -> bool:
        """
        Check if user can access a specific domain.
        
        Args:
            domain: Domain identifier (cybersecurity, datascience, itoperations, ai_assistant)
            
        Returns:
            True if user has permission to access this domain
        """
        allowed_domains = self.ROLE_PERMISSIONS.get(self.__role, [])
        return domain.lower() in allowed_domains
    
    def get_allowed_domains(self) -> list:
        """
        Get list of all domains this user can access.
        
        Returns:
            List of domain identifiers user has permission for
        """
        return self.ROLE_PERMISSIONS.get(self.__role, [])
    
    def get_role_display_name(self) -> str:
        """
        Get human-readable role name.
        
        Returns:
            Formatted role name for display
        """
        role_names = {
            'cybersecurity': 'Cybersecurity Analyst',
            'datascience': 'Data Scientist',
            'itoperations': 'IT Operations Engineer',
            'admin': 'System Administrator'
        }
        return role_names.get(self.__role, self.__role.title())
    
    def get_home_page(self) -> str:
        """
        Get the default home page for this user's role.
        
        Returns:
            Path to the user's primary dashboard
        """
        home_pages = {
            'cybersecurity': 'pages/1_🛡️_Cybersecurity.py',
            'datascience': 'pages/2_📊_Data_Science.py',
            'itoperations': 'pages/3_💻_IT_Operations.py',
            'admin': 'pages/1_🛡️_Cybersecurity.py'  # Admin sees all
        }
        return home_pages.get(self.__role, 'pages/1_🛡️_Cybersecurity.py')
    
    def is_admin(self) -> bool:
        """Check if user has administrator privileges."""
        return self.__role == 'admin'
    
    def __str__(self) -> str:
        """Return a string representation of the user."""
        return f"User(username={self.__username}, role={self.get_role_display_name()})"
    
    def __repr__(self) -> str:
        """Return a detailed string representation for debugging."""
        return f"User(username='{self.__username}', role='{self.__role}')"