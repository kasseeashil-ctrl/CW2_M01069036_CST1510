"""Security incident entity model"""

class SecurityIncident:
    """Represents a cybersecurity incident"""
    
    SEVERITY_LEVELS = {"low": 1, "medium": 2, "high": 3, "critical": 4} # Class constant - maps severity names to numeric values.
    
    def __init__(self, incident_id: int, date: str, incident_type: str, 
                 severity: str, status: str, description: str, reported_by: str = None):
        """Initialise incident with private attributes"""
        # Setting up private.
        self.__id = incident_id
        self.__date = date
        self.__incident_type = incident_type
        self.__severity = severity
        self.__status = status
        self.__description = description
        self.__reported_by = reported_by
    
    # Getter methods
    def get_id(self) -> int:
        return self.__id
    
    def get_date(self) -> str:
        return self.__date
    
    def get_incident_type(self) -> str:
        return self.__incident_type
    
    def get_severity(self) -> str:
        return self.__severity
    
    def get_status(self) -> str:
        return self.__status
    
    def get_description(self) -> str:
        return self.__description
    
    def get_reported_by(self) -> str:
        return self.__reported_by or "Unknown"
    
    # Business logic methods
    def update_status(self, new_status: str) -> None:
        """Update incident status"""
        self.__status = new_status
    
    def get_severity_level(self) -> int:
        """Get numeric severity for sorting"""
        return self.SEVERITY_LEVELS.get(self.__severity.lower(), 0) #Return numeric severity or 0 if not found.
    
    
    def is_critical(self) -> bool:
        """Check if incident is critical"""
        return self.__severity.lower() == "critical"# Return True if severity is "critical"
    
    def is_open(self) -> bool:
        """Check if incident is still active"""
        return self.__status.lower() in ["open", "investigating"]
    
    def get_ai_context(self) -> str:
        """Format incident details for AI analysis"""
        return f"""Incident Type: {self.__incident_type}
Severity: {self.__severity}
Status: {self.__status}
Date: {self.__date}
Description: {self.__description}
Reported By: {self.get_reported_by()}"""
    
    def __str__(self) -> str:
        # String representation for printing/debugging.
        return f"SecurityIncident(id={self.__id}, type={self.__incident_type}, severity={self.__severity})"
 