"""IT ticket entity model"""

class ITTicket:
    """Represents an IT support ticket"""
    
    PRIORITY_LEVELS = {"low": 1, "medium": 2, "high": 3, "critical": 4}
    
    def __init__(self, ticket_id: int, ticket_number: str, priority: str, status: str,
                 category: str, subject: str, description: str, created_date: str,
                 resolved_date: str = None, assigned_to: str = None):
        """Initialise ticket with private attributes"""
        self.__id = ticket_id
        self.__ticket_number = ticket_number
        self.__priority = priority
        self.__status = status
        self.__category = category
        self.__subject = subject
        self.__description = description
        self.__created_date = created_date
        self.__resolved_date = resolved_date
        self.__assigned_to = assigned_to
    
    # Getter methods
    def get_id(self) -> int:
        return self.__id
    
    def get_ticket_number(self) -> str:
        return self.__ticket_number
    
    def get_priority(self) -> str:
        return self.__priority
    
    def get_status(self) -> str:
        return self.__status
    
    def get_category(self) -> str:
        return self.__category
    
    def get_subject(self) -> str:
        return self.__subject
    
    def get_description(self) -> str:
        return self.__description
    
    def get_created_date(self) -> str:
        return self.__created_date
    
    def get_resolved_date(self) -> str:
        return self.__resolved_date or "Not resolved"
    
    def get_assigned_to(self) -> str:
        return self.__assigned_to or "Unassigned"
    
    # Setter methods for ticket management
    def assign_to(self, staff_username: str) -> None:
        """Assign ticket to staff member"""
        self.__assigned_to = staff_username
        if self.__status.lower() == "open":
            self.__status = "In Progress"
    
    def update_status(self, new_status: str) -> None:
        """Update ticket status"""
        self.__status = new_status
    
    def close_ticket(self, resolution_date: str = None) -> None:
        """Close the ticket"""
        self.__status = "Closed"
        if resolution_date:
            self.__resolved_date = resolution_date
    
    # Business logic methods
    def get_priority_level(self) -> int:
        """Get numeric priority for sorting"""
        return self.PRIORITY_LEVELS.get(self.__priority.lower(), 0)
    
    def is_critical(self) -> bool:
        """Check if ticket is critical"""
        return self.__priority.lower() == "critical"
    
    def is_open(self) -> bool:
        """Check if ticket is still active"""
        return self.__status.lower() in ["open", "in progress"]
    
    def is_assigned(self) -> bool:
        """Check if ticket has been assigned"""
        return self.__assigned_to is not None
    
    def get_ai_context(self) -> str:
        """Format ticket details for AI analysis"""
        return f"""Ticket Number: {self.__ticket_number}
Category: {self.__category}
Priority: {self.__priority}
Status: {self.__status}
Subject: {self.__subject}
Description: {self.__description}
Created: {self.__created_date}
Assigned To: {self.get_assigned_to()}
Resolved: {self.get_resolved_date()}"""
    
    def __str__(self) -> str:
        return f"ITTicket(number={self.__ticket_number}, priority={self.__priority}, status={self.__status})"