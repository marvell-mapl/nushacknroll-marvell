"""
Data Loader Utilities
Handles loading and accessing mock JSON data files.
"""

import json
import os
from typing import List, Dict, Any
from pathlib import Path


class DataLoader:
    """
    Centralized data loading for all mock JSON files.
    
    Why this exists:
    - Single source of truth for data access
    - Caching to avoid repeated file reads
    - Easy path management
    """
    
    def __init__(self, data_dir: str = "data"):
        """
        Initialize the data loader.
        
        Args:
            data_dir: Directory containing JSON files (relative to project root)
        """
        self.data_dir = Path(data_dir)
        self._cache = {}
    
    def _load_json(self, filename: str) -> List[Dict[str, Any]]:
        """
        Load a JSON file with caching.
        
        Args:
            filename: Name of the JSON file (e.g., 'flights.json')
        
        Returns:
            List of dictionaries from the JSON file
        """
        if filename in self._cache:
            return self._cache[filename]
        
        filepath = self.data_dir / filename
        
        if not filepath.exists():
            raise FileNotFoundError(f"Data file not found: {filepath}")
        
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        self._cache[filename] = data
        return data
    
    def get_flights(self) -> List[Dict[str, Any]]:
        """Load all flight data."""
        return self._load_json("flights.json")
    
    def get_accommodations(self) -> List[Dict[str, Any]]:
        """Load all accommodation data."""
        return self._load_json("accommodations.json")
    
    def get_attractions(self) -> List[Dict[str, Any]]:
        """Load all attraction data."""
        return self._load_json("attractions.json")
    
    def filter_flights(
        self, 
        origin: str = None, 
        destination: str = None,
        max_price: float = None
    ) -> List[Dict[str, Any]]:
        """
        Filter flights by criteria.
        
        Args:
            origin: Departure city
            destination: Arrival city
            max_price: Maximum price constraint
        
        Returns:
            Filtered list of flights
        """
        flights = self.get_flights()
        
        if origin:
            flights = [f for f in flights if f["origin"].lower() == origin.lower()]
        
        if destination:
            flights = [f for f in flights if f["destination"].lower() == destination.lower()]
        
        if max_price is not None:
            flights = [f for f in flights if f["price"] <= max_price]
        
        return flights
    
    def filter_accommodations(
        self, 
        city: str = None, 
        max_price_per_night: float = None
    ) -> List[Dict[str, Any]]:
        """
        Filter accommodations by criteria.
        
        Args:
            city: Destination city
            max_price_per_night: Maximum nightly rate
        
        Returns:
            Filtered list of accommodations
        """
        accommodations = self.get_accommodations()
        
        if city:
            accommodations = [a for a in accommodations if a["city"].lower() == city.lower()]
        
        if max_price_per_night is not None:
            accommodations = [a for a in accommodations if a["price_per_night"] <= max_price_per_night]
        
        return accommodations
    
    def filter_attractions(
        self, 
        city: str = None, 
        category: str = None
    ) -> List[Dict[str, Any]]:
        """
        Filter attractions by criteria.
        
        Args:
            city: Destination city
            category: Type of attraction (Culture, Nature, Landmark, Food)
        
        Returns:
            Filtered list of attractions
        """
        attractions = self.get_attractions()
        
        if city:
            attractions = [a for a in attractions if a["city"].lower() == city.lower()]
        
        if category:
            attractions = [a for a in attractions if a["category"].lower() == category.lower()]
        
        return attractions


# Singleton instance
_data_loader_instance = None


def get_data_loader() -> DataLoader:
    """
    Get or create the shared data loader instance.
    
    Returns:
        Singleton DataLoader instance
    """
    global _data_loader_instance
    if _data_loader_instance is None:
        _data_loader_instance = DataLoader()
    return _data_loader_instance

