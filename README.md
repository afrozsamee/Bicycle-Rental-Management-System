# Bicycle Rental Management System

This project is a comprehensive Bicycle Rental Management System developed as part of the 24COP501 Programming for Specialist Applications course, StudentID F418164. 
It includes a well-structured database, data scraping, data cleaning, object-oriented programming for core functionality, and a user-friendly GUI, providing a complete system for managing bicycle rentals.

Project Structure:

#### Database:

The project started with three raw data files: Bicycle_Info.txt, Rental_History.txt, and Members.txt. 
Additionally, an Inventory_Data.txt file was created by scraping Amazon’s UK bike product pages. Each dataset was cleaned, organized, and prepared for database integration. 
The data cleaning process is documented in the Jupyter notebook data/DataCleaning.ipynb.

For Inventory_Data.txt, I scraped data from Amazon using Beautiful Soup, extracting bike details, images, and page-based IDs. 
The scraping process navigates multiple pages, retrieves data in JSON format, and stores it. After cleaning, this data is linked to Bicycle_Info via inventoryID as a primary key.

#### Object-Oriented Design:

The project follows best practices in object-oriented programming, ensuring reusable and testable code. A central file, database.py, implements four classes:

FileReader: Reads and processes data files.
DatabaseManager: Handles database operations such as creating and dropping tables.
DataHandler: Manages data retrieval and updates, maintaining clean and readable code.
DataWriter: Writes to database tables.
This design ensures modularity and readability, making it easier for future users to understand and build upon the code.

#### Core Functionalities:

Bike Selection (bikeSelect.py): Enables users to search for bikes based on brand, type, and frame size.
Bike Rental (bikeRent.py): Manages the rental process, verifying the memberID using members.txt. 
It integrates with membershipManager.pyc for member validation and processes bike rentals based on rental duration.
Bike Return (bikeReturn.py): Allows users to return bikes, updating records for any reported damage, late returns, or additional costs. 
This feature updates the Rental_History table with actual return dates and logs for future reference.
Bike Recommendation (bikeSelect.py): Ranks bikes based on rental frequency, age, durability, and other criteria. 
An algorithm assigns weights to features, identifying best-sellers, low performers, and potential replacements. 
Data visualizations in graphs and animations (using Matplotlib) help inform decisions on future inventory and recommendations for users based on budget.
Graphical User Interface (GUI):

The front end of the project is built with ipywidgets and managed through menu.ipynb, providing an interactive experience for users.
The GUI directly initializes the relevant classes, linking to backend functionality seamlessly, making it intuitive and responsive.

#### Summary:

This project demonstrates a comprehensive approach to building a rental management system, addressing all coursework specifications while prioritizing usability, scalability, and functionality. 
The modular design, extensive data processing, and interactive GUI make it a robust solution for managing and recommending bike rentals.

<div class="alert alert-block alert-info">
<b>Tip:</b> "To effectively run the whole project please download the archived folder."
</div>
