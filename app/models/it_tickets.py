"""IT ticket entity model"""  

class ITTicket:
    """Represents an IT support ticket"""  # describes what this class represents
    
    PRIORITY_LEVELS = {"low": 1, "medium": 2, "high": 3, "critical": 4}  # Class constant  maps priority names to numeric values.
    
    def __init__(self, ticket_id: int, ticket_number: str, priority: str, status: str,
                 category: str, subject: str, description: str, created_date: str,
                 resolved_date: str = None, assigned_to: str = None):
        """Initialise ticket with private attributes"""  # Constructor docstring
        self.__id = ticket_id  # Set private ID attribute (database primary key)
        self.__ticket_number = ticket_number  # Set private ticket number 
        #Setting private attributes
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
        return self.__id  # Return the private ID attribute
    
    def get_ticket_number(self) -> str:
        return self.__ticket_number  # Return the private ticket number attribute
    
    def get_priority(self) -> str:
        return self.__priority  # Return the private priority attribute
    
    def get_status(self) -> str:
        return self.__status  # Return the private status attribute
    
    def get_category(self) -> str:
        return self.__category  # Returning the private category attribute
    
    def get_subject(self) -> str:
        return self.__subject  # Returning the private subject attribute
    
    def get_description(self) -> str:
        return self.__description  # Returning the private description attribute
    
    def get_created_date(self) -> str:
        return self.__created_date  # Returning the private creation date attribute
    
    def get_resolved_date(self) -> str:
        return self.__resolved_date or "Not resolved"  # Return resolved date or default message if None
    
    def get_assigned_to(self) -> str:
        return self.__assigned_to or "Unassigned"  # Return assignee or default message if None
    
    # Setter methods for ticket management
    def assign_to(self, staff_username: str) -> None:
        """Assign ticket to staff member"""  
        self.__assigned_to = staff_username  # Update the assigned_to attribute
        if self.__status.lower() == "open":  # Check if current status is "open"
            self.__status = "In Progress"  # Automatically update status to "In Progress"
    
    def update_status(self, new_status: str) -> None:
        """Update ticket status"""  
        self.__status = new_status  # Update the status attribute
    
    def close_ticket(self, resolution_date: str = None) -> None:
        """Close the ticket"""  
        self.__status = "Closed"  # Set status to "Closed"
        if resolution_date:  # Check if resolution_date was provided
            self.__resolved_date = resolution_date  # Update resolved_date if provided
    
    # Business logic methods
    def get_priority_level(self) -> int:
        """Get numeric priority for sorting"""  
        return self.PRIORITY_LEVELS.get(self.__priority.lower(), 0)  # Return numeric priority or 0 if not found
    
    def is_critical(self) -> bool:
        """Check if ticket is critical"""  
        return self.__priority.lower() == "critical"  # Return True if priority is "critical"
    
    def is_open(self) -> bool:
        """Check if ticket is still active"""  
        return self.__status.lower() in ["open", "in progress"]  # Return True if status is open or in progress
    
    def is_assigned(self) -> bool:
        """Check if ticket has been assigned"""  
        return self.__assigned_to is not None  # Return True if assigned_to is not None
    
    def get_ai_context(self) -> str:
        """Format ticket details for AI analysis"""  
        return f"""Ticket Number: {self.__ticket_number}
Category: {self.__category}
Priority: {self.__priority}
Status: {self.__status}
Subject: {self.__subject}
Description: {self.__description}
Created: {self.__created_date}
Assigned To: {self.get_assigned_to()}  # Use getter method for formatted output
Resolved: {self.get_resolved_date()}"""  # Multi-line string with ticket summary
    
    def __str__(self) -> str:
        return f"ITTicket(number={self.__ticket_number}, priority={self.__priority}, status={self.__status})"  # String representation for printing.