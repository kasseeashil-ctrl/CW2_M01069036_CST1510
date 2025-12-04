"""User entity model with role-based access control"""

class User:
    """Represents an authenticated user with domain permissions"""
    
    # Define which domains each role can access
    ROLE_PERMISSIONS = {
        'cybersecurity': ['cybersecurity', 'ai_assistant'],
        'datascience': ['datascience', 'ai_assistant'],
        'itoperations': ['itoperations', 'ai_assistant'],
        'admin': ['cybersecurity', 'datascience', 'itoperations', 'ai_assistant']
    }
    
    def __init__(self, username: str, password_hash: str, role: str):
        """Initialise user with private attributes"""
        self.__username = username
        self.__password_hash = password_hash
        self.__role = role.lower()
    
    # Getter methods
    def get_username(self) -> str:
        return self.__username
    
    def get_role(self) -> str:
        return self.__role
    
    def get_password_hash(self) -> str:
        return self.__password_hash
    
    # Business logic methods
    def can_access_domain(self, domain: str) -> bool:
        """Check if user has permission for a domain"""
        allowed = self.ROLE_PERMISSIONS.get(self.__role, [])
        return domain.lower() in allowed
    
    def get_allowed_domains(self) -> list:
        """Get all domains user can access"""
        return self.ROLE_PERMISSIONS.get(self.__role, [])
    
    def get_role_display_name(self) -> str:
        """Get human-readable role name"""
        names = {
            'cybersecurity': 'Cybersecurity Analyst',
            'datascience': 'Data Scientist',
            'itoperations': 'IT Operations Engineer',
            'admin': 'System Administrator'
        }
        return names.get(self.__role, self.__role.title())
    
    def get_home_page(self) -> str:
        """Get default home page for user's role"""
        pages = {
            'cybersecurity': 'pages/1_🛡️_Cybersecurity.py',
            'datascience': 'pages/2_📊_Data_Science.py',
            'itoperations': 'pages/3_💻_IT_Operations.py',
            'admin': 'pages/1_🛡️_Cybersecurity.py'
        }
        return pages.get(self.__role, 'pages/1_🛡️_Cybersecurity.py')
    
    def __str__(self) -> str:
        return f"User(username={self.__username}, role={self.get_role_display_name()})"