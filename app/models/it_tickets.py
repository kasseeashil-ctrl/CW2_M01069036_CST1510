"""
IT Ticket Entity Model
Represents an IT support ticket in the platform
"""

class ITTicket:
    """
    Represents an IT support ticket with priority tracking and assignment.
    
    Provides methods for ticket lifecycle management and priority assessment.
    """
    
    # Define priority level mapping as a class constant
    PRIORITY_LEVELS = {
        "low": 1,
        "medium": 2,
        "high": 3,
        "critical": 4
    }
    
    def __init__(
        self,
        ticket_id: int,
        ticket_number: str,
        priority: str,
        status: str,
        category: str,
        subject: str,
        description: str,
        created_date: str,
        resolved_date: str = None,
        assigned_to: str = None
    ):
        """
        Initialise a new ITTicket instance.
        
        Args:
            ticket_id: Unique database ID
            ticket_number: Human-readable ticket number (e.g., 'TICK-001')
            priority: Priority level ('Low', 'Medium', 'High', 'Critical')
            status: Current status (e.g., 'Open', 'In Progress', 'Resolved', 'Closed')
            category: Ticket category (e.g., 'Hardware', 'Software', 'Network')
            subject: Brief summary of the issue
            description: Detailed description of the problem
            created_date: Date ticket was created (YYYY-MM-DD format)
            resolved_date: Date ticket was resolved (YYYY-MM-DD format, optional)
            assigned_to: Username of assigned staff member (optional)
        """
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
        """Return the ticket database ID."""
        return self.__id
    
    def get_ticket_number(self) -> str:
        """Return the human-readable ticket number."""
        return self.__ticket_number
    
    def get_priority(self) -> str:
        """Return the priority level."""
        return self.__priority
    
    def get_status(self) -> str:
        """Return the current status."""
        return self.__status
    
    def get_category(self) -> str:
        """Return the ticket category."""
        return self.__category
    
    def get_subject(self) -> str:
        """Return the ticket subject."""
        return self.__subject
    
    def get_description(self) -> str:
        """Return the ticket description."""
        return self.__description
    
    def get_created_date(self) -> str:
        """Return the creation date."""
        return self.__created_date
    
    def get_resolved_date(self) -> str:
        """Return the resolution date (or 'Not resolved' if still open)."""
        return self.__resolved_date or "Not resolved"
    
    def get_assigned_to(self) -> str:
        """Return the assigned staff member (or 'Unassigned' if not assigned)."""
        return self.__assigned_to or "Unassigned"
    
    # Setter methods for ticket management
    def assign_to(self, staff_username: str) -> None:
        """
        Assign the ticket to a staff member.
        
        Args:
            staff_username: Username of the staff member to assign
        """
        self.__assigned_to = staff_username
        # Automatically set status to 'In Progress' when assigned
        if self.__status.lower() == "open":
            self.__status = "In Progress"
    
    def update_status(self, new_status: str) -> None:
        """
        Update the ticket status.
        
        Args:
            new_status: New status value (e.g., 'In Progress', 'Resolved')
        """
        self.__status = new_status
    
    def close_ticket(self, resolution_date: str = None) -> None:
        """
        Close the ticket and mark it as resolved.
        
        Args:
            resolution_date: Date of resolution (YYYY-MM-DD). Defaults to current date.
        """
        self.__status = "Closed"
        if resolution_date:
            self.__resolved_date = resolution_date
    
    # Business logic methods
    def get_priority_level(self) -> int:
        """
        Return a numeric priority level for sorting/filtering.
        
        Returns:
            Integer from 1 (Low) to 4 (Critical), or 0 if unknown
        """
        return self.PRIORITY_LEVELS.get(self.__priority.lower(), 0)
    
    def is_critical(self) -> bool:
        """Check if this ticket has critical priority."""
        return self.__priority.lower() == "critical"
    
    def is_open(self) -> bool:
        """Check if this ticket is still open or in progress."""
        return self.__status.lower() in ["open", "in progress"]
    
    def is_assigned(self) -> bool:
        """Check if this ticket has been assigned to someone."""
        return self.__assigned_to is not None
    
    def get_ai_context(self) -> str:
        """
        Generate a formatted context string for AI analysis.
        
        Returns:
            A formatted string with ticket details for AI processing
        """
        return f"""
Ticket Number: {self.__ticket_number}
Category: {self.__category}
Priority: {self.__priority}
Status: {self.__status}
Subject: {self.__subject}
Description: {self.__description}
Created: {self.__created_date}
Assigned To: {self.get_assigned_to()}
Resolved: {self.get_resolved_date()}
        """.strip()
    
    def __str__(self) -> str:
        """Return a readable string representation."""
        return (
            f"ITTicket("
            f"number={self.__ticket_number}, "
            f"priority={self.__priority}, "
            f"status={self.__status}, "
            f"assigned={self.get_assigned_to()})"
        )
    
    def __repr__(self) -> str:
        """Return a detailed string representation for debugging."""
        return (
            f"ITTicket("
            f"id={self.__id}, "
            f"number='{self.__ticket_number}', "
            f"priority='{self.__priority}', "
            f"status='{self.__status}', "
            f"category='{self.__category}', "
            f"assigned_to='{self.__assigned_to}'"
            f")"
        )