"""
    StudentID : F418164
    The Aim of this program to create search functionalities depending upon user selection,
    does retrival operations from databases tables and by using 
    object-oriented programming (OOP) principles, this class ensures reusability 
    and maintainability. With OOP, each operation is encapsulated within methods 
    of this class, making it easy to expand functionality and manage code changes 
    without affecting external components. This modular design improves code readability 
    and reduces duplication, allowing seamless interaction with database operations 
    for bicycle inventory management.
"""
import sqlite3
import pandas as pd
from database import *  # Make sure to have the database operations imported

class BikeSearch:
    """
    The BikeSearch class provides methods to search and retrieve bicycle information
    from a database based on criteria like brand, type, and frame size. 
    """
    def __init__(self):
        """Initialize BikeSearch with unique bicycle types, brands, and frame sizes."""
        self.db = databaseOperations() # Initialize database operations instance
        self.types, self.brands, self.frame_sizes = self.db.get_uniquevalues()
        
    def search_bicycles(self, search_term, search_type):
        """
        Search bicycles by a specified term and type.

        Parameters:
            search_term (str): The term to search for, which can be a brand, type, or frame size.
            search_type (str): The category of search (e.g., 'Brand', 'Type', or 'Frame_Size').

        Returns:
            pd.DataFrame: DataFrame containing the search results if found, else an empty DataFrame.
        """
        all_values = set(self.types) | set(self.brands) | set(self.frame_sizes)

        # Check if search_term is in the combined set
        if search_term not in all_values:
            return pd.DataFrame()
        else:
            bicycles = self.db.searchBicycles(search_term, search_type)
            if bicycles:
                df = pd.DataFrame(bicycles, columns=[
                        "Bicycle ID", "Brand", "Type", "FrameSize",
                        "Daily Rate", "Weekly Rate", "Status",
                        "Date of Purchase","Condition","InventoryID", "ImageURL"
                ])
                 
                if 'ImageURL' in df.columns:
                    df.set_index('ImageURL', inplace=True)
                else:
                    return pd.DataFrame()
                return df  
            else:
                return pd.DataFrame() # Return empty DataFrame if no results

def test():
    """
    Test function to validate and debug the BikeSearch class functionality.
    This function acts as a profile for checking various search operations and 
    confirming expected outputs.
    """
    bike_search = BikeSearch()
    # Test with various search terms and types
    try:
        print("Testing search by frame size 'Large'...")
        result = bike_search.search_bicycles("Large", "Frame_Size")
        print("Search Results for frame size 'Large':\n", result)

        print("Testing search by brand 'Giant'...")
        result = bike_search.search_bicycles("Giant", "Brand")
        print("Search Results for brand 'Giant':\n", result)

        print("Testing search by type 'Mountain Bike'...")
        result = bike_search.search_bicycles("Mountain Bike", "Type")
        print("Search Results for type 'Mountain Bike':\n", result)

        print("Testing invalid search term 'UnknownTerm'...")
        result = bike_search.search_bicycles("UnknownTerm", "Type")
        print("Search Results for 'UnknownTerm':\n", result)

        # Output available unique values
        print("\nAvailable types:", bike_search.types)
        print("Available brands:", bike_search.brands)
        print("Available frame sizes:", bike_search.frame_sizes)

    except Exception as e:
        print("An error occurred during testing:", e)
        
if __name__ == "__main__":
    """
    Test function for debugging and validating BikeSearch class functionality
    """
    test()



