"""
Dataset Entity Model
Represents a data science dataset in the platform
"""

class Dataset:
    """
    Represents a dataset with metadata about size, source, and record count.
    
    Provides utility methods for size calculations and data management.
    """
    
    def __init__(
        self,
        dataset_id: int,
        name: str,
        category: str,
        source: str,
        last_updated: str,
        record_count: int,
        file_size_mb: float
    ):
        """
        Initialise a new Dataset instance.
        
        Args:
            dataset_id: Unique identifier for the dataset
            name: Human-readable dataset name
            category: Dataset category (e.g., 'Threat Intelligence', 'Network Logs')
            source: Origin of the dataset (e.g., 'Internal', 'External API')
            last_updated: Last update date (YYYY-MM-DD format)
            record_count: Number of records in the dataset
            file_size_mb: File size in megabytes
        """
        self.__id = dataset_id
        self.__name = name
        self.__category = category
        self.__source = source
        self.__last_updated = last_updated
        self.__record_count = record_count
        self.__file_size_mb = file_size_mb
    
    # Getter methods
    def get_id(self) -> int:
        """Return the dataset ID."""
        return self.__id
    
    def get_name(self) -> str:
        """Return the dataset name."""
        return self.__name
    
    def get_category(self) -> str:
        """Return the dataset category."""
        return self.__category
    
    def get_source(self) -> str:
        """Return the dataset source."""
        return self.__source
    
    def get_last_updated(self) -> str:
        """Return the last update date."""
        return self.__last_updated
    
    def get_record_count(self) -> int:
        """Return the number of records."""
        return self.__record_count
    
    def get_file_size_mb(self) -> float:
        """Return the file size in MB."""
        return self.__file_size_mb
    
    # Business logic methods
    def calculate_size_gb(self) -> float:
        """
        Convert file size from MB to GB.
        
        Returns:
            File size in gigabytes (rounded to 2 decimal places)
        """
        return round(self.__file_size_mb / 1024, 2)
    
    def is_large_dataset(self) -> bool:
        """
        Determine if this is a large dataset (> 100 MB).
        
        Returns:
            True if dataset is larger than 100 MB
        """
        return self.__file_size_mb > 100
    
    def get_records_per_mb(self) -> float:
        """
        Calculate the average number of records per MB.
        
        Returns:
            Records per MB (rounded to 2 decimal places), or 0 if size is 0
        """
        if self.__file_size_mb == 0:
            return 0.0
        return round(self.__record_count / self.__file_size_mb, 2)
    
    def get_ai_context(self) -> str:
        """
        Generate a formatted context string for AI analysis.
        
        Returns:
            A formatted string with dataset details for AI processing
        """
        return f"""
Dataset Name: {self.__name}
Category: {self.__category}
Source: {self.__source}
Last Updated: {self.__last_updated}
Record Count: {self.__record_count:,} records
File Size: {self.__file_size_mb:.2f} MB ({self.calculate_size_gb()} GB)
Records per MB: {self.get_records_per_mb()}
        """.strip()
    
    def __str__(self) -> str:
        """Return a readable string representation."""
        return (
            f"Dataset(id={self.__id}, "
            f"name={self.__name}, "
            f"size={self.__file_size_mb:.2f}MB, "
            f"records={self.__record_count:,})"
        )
    
    def __repr__(self) -> str:
        """Return a detailed string representation for debugging."""
        return (
            f"Dataset("
            f"id={self.__id}, "
            f"name='{self.__name}', "
            f"category='{self.__category}', "
            f"source='{self.__source}', "
            f"record_count={self.__record_count}, "
            f"file_size_mb={self.__file_size_mb}"
            f")"
        )