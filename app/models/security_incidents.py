"""
Security Incident Entity Model
Represents a cybersecurity incident in the platform
"""

class SecurityIncident:
    """
    Represents a cybersecurity incident with severity classification
    and status tracking.
    
    Provides methods for incident management and priority assessment.
    """
    
    # Define severity level mapping as a class constant
    SEVERITY_LEVELS = {
        "low": 1,
        "medium": 2,
        "high": 3,
        "critical": 4
    }
    
    def __init__(
        self, 
        incident_id: int, 
        date: str,
        incident_type: str, 
        severity: str,
        status: str, 
        description: str,
        reported_by: str = None
    ):
        """
        Initialise a new SecurityIncident instance.
        
        Args:
            incident_id: Unique identifier for the incident
            date: Date the incident occurred (YYYY-MM-DD format)
            incident_type: Type of incident (e.g., 'Phishing', 'Malware', 'DDoS')
            severity: Severity level ('Low', 'Medium', 'High', 'Critical')
            status: Current status (e.g., 'Open', 'Investigating', 'Resolved', 'Closed')
            description: Detailed description of the incident
            reported_by: Username of the person who reported it (optional)
        """
        self.__id = incident_id
        self.__date = date
        self.__incident_type = incident_type
        self.__severity = severity
        self.__status = status
        self.__description = description
        self.__reported_by = reported_by
    
    # Getter methods
    def get_id(self) -> int:
        """Return the incident ID."""
        return self.__id
    
    def get_date(self) -> str:
        """Return the incident date."""
        return self.__date
    
    def get_incident_type(self) -> str:
        """Return the incident type."""
        return self.__incident_type
    
    def get_severity(self) -> str:
        """Return the severity level."""
        return self.__severity
    
    def get_status(self) -> str:
        """Return the current status."""
        return self.__status
    
    def get_description(self) -> str:
        """Return the incident description."""
        return self.__description
    
    def get_reported_by(self) -> str:
        """Return the username of who reported the incident."""
        return self.__reported_by or "Unknown"
    
    # Business logic methods
    def update_status(self, new_status: str) -> None:
        """
        Update the incident status.
        
        Args:
            new_status: New status value (e.g., 'Investigating', 'Resolved')
        """
        self.__status = new_status
    
    def get_severity_level(self) -> int:
        """
        Return a numeric severity level for sorting/filtering.
        
        Returns:
            Integer from 1 (Low) to 4 (Critical), or 0 if unknown
        """
        return self.SEVERITY_LEVELS.get(self.__severity.lower(), 0)
    
    def is_critical(self) -> bool:
        """Check if this incident is classified as critical."""
        return self.__severity.lower() == "critical"
    
    def is_open(self) -> bool:
        """Check if this incident is still open."""
        return self.__status.lower() in ["open", "investigating"]
    
    def get_ai_context(self) -> str:
        """
        Generate a formatted context string for AI analysis.
        
        Returns:
            A formatted string with incident details for AI processing
        """
        return f"""
Incident Type: {self.__incident_type}
Severity: {self.__severity}
Status: {self.__status}
Date: {self.__date}
Description: {self.__description}
Reported By: {self.get_reported_by()}
        """.strip()
    
    def __str__(self) -> str:
        """Return a readable string representation."""
        return (
            f"SecurityIncident(id={self.__id}, "
            f"type={self.__incident_type}, "
            f"severity={self.__severity}, "
            f"status={self.__status})"
        )
    
    def __repr__(self) -> str:
        """Return a detailed string representation for debugging."""
        return (
            f"SecurityIncident("
            f"id={self.__id}, "
            f"date='{self.__date}', "
            f"type='{self.__incident_type}', "
            f"severity='{self.__severity}', "
            f"status='{self.__status}', "
            f"reported_by='{self.__reported_by}'"
            f")"
        )