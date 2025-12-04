"""Dataset entity model"""

class Dataset:
    """Represents a data science dataset"""
    
    def __init__(self, dataset_id: int, name: str, category: str, source: str,
                 last_updated: str, record_count: int, file_size_mb: float):
        """Initialise dataset with private attributes"""
        self.__id = dataset_id
        self.__name = name
        self.__category = category
        self.__source = source
        self.__last_updated = last_updated
        self.__record_count = record_count
        self.__file_size_mb = file_size_mb
    
    # Getter methods
    def get_id(self) -> int:
        return self.__id
    
    def get_name(self) -> str:
        return self.__name
    
    def get_category(self) -> str:
        return self.__category
    
    def get_source(self) -> str:
        return self.__source
    
    def get_last_updated(self) -> str:
        return self.__last_updated
    
    def get_record_count(self) -> int:
        return self.__record_count
    
    def get_file_size_mb(self) -> float:
        return self.__file_size_mb
    
    # Business logic methods
    def calculate_size_gb(self) -> float:
        """Convert size from MB to GB"""
        return round(self.__file_size_mb / 1024, 2)
    
    def is_large_dataset(self) -> bool:
        """Check if dataset is large (>100MB)"""
        return self.__file_size_mb > 100
    
    def get_records_per_mb(self) -> float:
        """Calculate record density"""
        if self.__file_size_mb == 0:
            return 0.0
        return round(self.__record_count / self.__file_size_mb, 2)
    
    def get_ai_context(self) -> str:
        """Format dataset details for AI analysis"""
        return f"""Dataset Name: {self.__name}
Category: {self.__category}
Source: {self.__source}
Last Updated: {self.__last_updated}
Record Count: {self.__record_count:,} records
File Size: {self.__file_size_mb:.2f} MB ({self.calculate_size_gb()} GB)
Records per MB: {self.get_records_per_mb()}"""
    
    def __str__(self) -> str:
        return f"Dataset(id={self.__id}, name={self.__name}, size={self.__file_size_mb:.2f}MB)"