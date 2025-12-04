"""Dataset entity model""" 

class Dataset:
    """Represents a data science dataset"""  
    
    def __init__(self, dataset_id: int, name: str, category: str, source: str,
                 last_updated: str, record_count: int, file_size_mb: float):
        """Initialise dataset with private attributes"""  
        self.__id = dataset_id  # Set private ID attribute (double underscore makes it private).
        self.__name = name  # Set private name attribute
        self.__category = category  # Set private category attribute
        self.__source = source  # Set private source attribute
        self.__last_updated = last_updated  # Setting private last_updated attribute
        self.__record_count = record_count  # Setting private record_count attribute
        self.__file_size_mb = file_size_mb  # Setting private file_size_mb attribute
    
    #Get methods
    def get_id(self) -> int:
        return self.__id  # Return the private ID attribute
    
    def get_name(self) -> str:
        return self.__name  # Return the private name attribute
    
    def get_category(self) -> str:
        return self.__category  # Return the private category attribute
    
    def get_source(self) -> str:
        return self.__source  # Return the private source attribute
    
    def get_last_updated(self) -> str:
        return self.__last_updated  # Return the private last_updated attribute
    
    def get_record_count(self) -> int:
        return self.__record_count  # Return the private record_count attribute
    
    def get_file_size_mb(self) -> float:
        return self.__file_size_mb  # Return the private file_size_mb attribute
    
    # Business logic methods
    def calculate_size_gb(self) -> float:
        """Convert size from MB to GB"""  
        return round(self.__file_size_mb / 1024, 2)  # Convert MB to GB and round to 2 decimal places.
    
    def is_large_dataset(self) -> bool:
        """Check if dataset is large (>100MB)"""  
        return self.__file_size_mb > 100  # Return True if file size is greater than 100MB
    
    def get_records_per_mb(self) -> float:
        """Calculate record density"""  
        if self.__file_size_mb == 0:  # Check if file size is zero to avoid division by zero
            return 0.0  # Return 0.0 if file size is zero
        return round(self.__record_count / self.__file_size_mb, 2)  # Calculate records per MB and round to 2 decimals
    
    def get_ai_context(self) -> str:
        """Format dataset details for AI analysis""" 
        return f"""Dataset Name: {self.__name}
Category: {self.__category}
Source: {self.__source}
Last Updated: {self.__last_updated}
Record Count: {self.__record_count:,} records  # Format with thousand separators
File Size: {self.__file_size_mb:.2f} MB ({self.calculate_size_gb()} GB)  # Show both MB and GB
Records per MB: {self.get_records_per_mb()}"""  # Multi-line string with dataset summary
    
    def __str__(self) -> str:
        return f"Dataset(id={self.__id}, name={self.__name}, size={self.__file_size_mb:.2f}MB)"  # String representation for printing