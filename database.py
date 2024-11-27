"""
StudentID : F418164
This program manages database operations for a bicycle rental system using object-oriented programming.
The program includes classes and methods to handle various aspects of database management, including:
- Writing data to a SQLite3 database
- Creating and managing database tables
- Reading and processing data from external files

By structuring the program with classes and modular methods, we achieve:
- **Reusability:** Each method can be reused across different parts of the program.
- **Maintainability:** Code is organized logically, making it easier to update and debug.
- **Encapsulation:** Related data and methods are grouped, improving organization and functionality.
- **Normalisation:** Made sure the database tables, Bicycle_Info, Rental_Histor, Inventory_Data is normalised to 3rd normal form

The main components include classes for reading data files, database writing, and data retrieval.
"""
import sqlite3
import datetime
import membershipManager as M 

class readFromFile():
    """
    Class to read and process data from external text files for bicycle inventory, rental history, and other data.

    Methods:
        - `read_bicycleInfo_from_file`: Reads bicycle information, processes rental rates.
        - `read_rentalHistory_from_file`: Reads rental history data.
        - `read_InventoryData_from_file`: Reads inventory data.
    """
    def read_bicycleInfo_from_file():
        """
        Reads bicycle information from a tab-delimited text file and processes rental rates.

        Returns:
            list of tuples: Each tuple contains details of a bicycle, including ID, brand, type,
            frame size, daily and weekly rental rates, status, purchase date, and condition.
        """
        records = []
        try:
            file=open("./data/Bicycle_Info.txt","r")
            header = next(file)  # Skip the header line
            for line in file:
                BicycleID, Brand, Type, FrameSize, RentalRate, Status, DateOfPurchase, Condition = line.strip().split('\t')
                BicycleID = int(BicycleID)
                    
                # Split RentalRate into DailyRate and WeeklyRate
                try:
                    daily_rate, weekly_rate = RentalRate.split(';')
                    DailyRate = int(daily_rate.replace('/day', '').strip())  
                    WeeklyRate = int(weekly_rate.replace('/week', '').strip())  
                except ValueError:
                    print(f"Error parsing rental rate for BicycleID {BicycleID}: {RentalRate}")
                    continue

                records.append((BicycleID, Brand, Type, FrameSize, DailyRate, WeeklyRate, Status, DateOfPurchase, Condition))
                    
        except FileNotFoundError:
            print("File not found. Please check the file path or name.")
        except Exception as e:
            print(f"Error reading file: {e}")
        except IOError as e:
            errno,strerror=e.args
            print ("I/O error(%d):%s"%(errno,strerror))
        
        return records

    def read_rentalHistory_from_file():
        """
        Reads rental history data from a tab-delimited text file.

        Returns:
            list of tuples: Each tuple includes a record of bicycle ID, member ID, rental date, and return date.
        """
        records = []
        try:
            file=open("./data/Rental_History.txt","r")
            header = next(file)  # Skip the header line
            for line in file:
                BicycleID, MemberID, RentalDate, ReturnDate = line.strip().split('\t')
                BicycleID = int(BicycleID)
                MemberID = int(MemberID)

                records.append((BicycleID, MemberID, RentalDate, ReturnDate))
           
        except Exception as e:
            print(f"Error reading file: {e}")
        except IOError as e:
            errno,strerror=e.args
            print ("I/O error(%d):%s"%(errno,strerror))
        except ValueError:
            print ("That was no valid number")
        except FileNotFoundError:
            print("File not found. Please check the file path or name.")
            
        return records

    def read_InventoryData_from_file():
        """
        Reads inventory data from a tab-delimited text file.

        Returns:
            list of tuples: Each tuple contains details of an inventory item, including ID, price, image URL,
            brand, size, type, gender, speed, frame, brake type, age, suspension, tire type, and customer rating.
        """
        records = []
        try:
            file=open("./data/Inventory_Data.txt","r")
            header = next(file)  # Skip the header line
            for line in file:
                InventoryID, Price, ImageURL, BrandName, Size, Type, Gender, Speed, Frame, BrakeType, Age, Suspension, TireType, CustomerRating = line.strip().split('\t')
                InventoryID = int(InventoryID)
                records.append((InventoryID, Price, ImageURL, BrandName, Size, Type, Gender, Speed, Frame, BrakeType, Age, Suspension, TireType, CustomerRating))
                    
        except FileNotFoundError:
            print("File not found. Please check the file path or name.")
        except Exception as e:
            print(f"Error reading file: {e}")
        except IOError as e:
            errno,strerror=e.args
            print ("I/O error(%d):%s"%(errno,strerror))
        
        return records

class writeToSql():
    """
    The `writeToSql` class manages creating tables, inserting records, managing relationships, and creating 
    views. Utilizing object-oriented programming principles, this class enhances code 
    reusability and maintainability by providing a single interface to handle all SQL 
    operations for managing bicycles, rentals, inventory, and logs in an SQLite database.
    
    Classes and methods within this file are designed for:
    - Writing records to tables in a consistent manner.
    - Defining and maintaining table structures for various entities.
    - Supporting retrieval and search operations through views.
    - Relationship between the tables have been used properly
    """
    def __init__(self, db_name = 'BicycleRental.db'):
        """Initialize the database with the specified name or default to 'BicycleRental.db'."""
        self.db_name = db_name
        

    def write_bicycleData_to_db(self, records):
        """
        Inserts bicycle records into the Bicycle_Info table, linking each record to 
        an existing (Brand, Type) combination in Inventory_Data.

        Args:
            records (list of tuples): List of bicycle records to insert.

        Raises:
            ValueError: If a (Brand, Type) combination doesn't exist in Inventory_Data.
        """
        try:
            with sqlite3.connect(self.db_name) as conn:
                cursor = conn.cursor()
                # Create Bicycle_Info table if it does not exist
                cursor.execute('''CREATE TABLE IF NOT EXISTS "Bicycle_Info" (
                    BicycleID INTEGER PRIMARY KEY,     -- Unique identifier for bicycles
                    Brand TEXT NOT NULL,               -- Brand name (mandatory)
                    Type TEXT NOT NULL,                -- Type of bicycle (mandatory)
                    FrameSize TEXT NOT NULL,           -- Frame size (mandatory)
                    DailyRate INTEGER NOT NULL,        -- Daily rental rate as an integer
                    WeeklyRate INTEGER NOT NULL,       -- Weekly rental rate as an integer
                    Status TEXT NOT NULL,              -- Availability status (e.g., Available/Rented)
                    DateOfPurchase DATE NOT NULL,      -- Purchase date (stored as text in 'YYYY-MM-DD')
                    Condition TEXT NOT NULL,           -- Bicycle condition (e.g., New/Good/Fair)
                    InventoryID INTEGER,               -- Foreign key to Inventory_Data
                    FOREIGN KEY (InventoryID) REFERENCES Inventory_Data(InventoryID)
                )''')

                # Insert each record if matching InventoryID is found
                for record in records:
                    bicycle_id, brand, type_, frame_size, daily_rate, weekly_rate, status, date_of_purchase, condition = record
                    cursor.execute('''
                        SELECT InventoryID FROM Inventory_Data
                        WHERE BrandName = ? AND Type = ?
                    ''', (brand, type_))

                    inventory_id = cursor.fetchone()

                    if inventory_id is None:
                        raise ValueError(f"No matching Inventory record found for Brand '{brand}' and Type '{type_}'.")

                    inventory_id = inventory_id[0]
                    cursor.execute('''
                        INSERT INTO Bicycle_Info (
                            BicycleID, Brand, Type, FrameSize, DailyRate, WeeklyRate,
                            Status, DateOfPurchase, Condition, InventoryID
                        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    ''', (bicycle_id, brand, type_, frame_size, daily_rate, weekly_rate,
                          status, date_of_purchase, condition, inventory_id))

                conn.commit()
                print("Records inserted successfully into Bicycle_Info.")

        except ValueError as ve:
            print(f"Error: {ve}")
        except sqlite3.Error as e:
            print(f"Database error: {e}")
        finally:
            conn.close()

    def write_rentalData_to_db(self, records):
        """
        Inserts rental records into the Rental_History table, ensuring valid rental dates.
        
        Args:
            records (list of tuples): List of rental records to insert.
        """
        try:
            with sqlite3.connect(self.db_name) as conn:
                cursor = conn.cursor()

                cursor.execute('''CREATE TABLE IF NOT EXISTS "Rental_History" (
                BicycleID INTEGER NOT NULL,                 -- References Bicycle_Info (cannot be null)
                MemberID INTEGER  NOT NULL,                 -- Can be null (for non-members)
                RentalDate DATE NOT NULL,                   -- Date of rental (YYYY-MM-DD format)
                ReturnDate DATE NOT NULL,                   -- Date of return (YYYY-MM-DD format),

                -- Foreign key constraints
                FOREIGN KEY (BicycleID) REFERENCES Bicycle_Info(BicycleID)
                ON DELETE CASCADE ON UPDATE CASCADE,

                -- Ensure rental dates are valid
                CHECK (RentalDate < ReturnDate)
                )''')

                cursor.executemany('''
                    INSERT INTO Rental_History (BicycleID, MemberID, RentalDate, ReturnDate)
                    VALUES (?, ?, ?, ?)''', records)

            conn.commit()
            print("Records inserted successfully into normalized tables.")

        except sqlite3.Error as e:
            print(f"Database error: {e}")
        finally:
            conn.close()

    def write_InventoryData_to_db(self, records):
        """
        Inserts inventory data records into the Inventory_Data table.
        
        Args:
            records (list of tuples): List of inventory records to insert.
        """
        try:
            with sqlite3.connect(self.db_name) as conn:
                cursor = conn.cursor()
                cursor.execute('''CREATE TABLE IF NOT EXISTS "Inventory_Data" (
                    InventoryID INTEGER PRIMARY KEY,         -- Primary Key for Inventory table
                    Price REAL NOT NULL,                     -- Purchase price of the bicycle
                    ImageURL TEXT NOT NULL,                  -- URL for the bicycle image
                    BrandName TEXT NOT NULL,                 -- Brand name of the bicycle
                    Size TEXT NOT NULL,                      -- Size (e.g., M, L, S)
                    Type TEXT NOT NULL,                      -- Type of bicycle (e.g., Mountain, Road)
                    Gender TEXT NOT NULL,                    -- Gender (e.g., Unisex, Men, Women)
                    Speed TEXT NOT NULL,                     -- Number of speeds
                    Frame TEXT NOT NULL,                     -- Frame material (e.g., Carbon, Aluminum)
                    BrakeType TEXT NOT NULL,                 -- Brake type (e.g., Disc, V-Brake)
                    Age TEXT NOT NULL,                       -- Age group (e.g., 1 for one year)
                    Suspension TEXT NOT NULL, 
                    TireType TEXT NOT NULL, 
                    CustomerRating INTEGER
                )''')

                cursor.executemany('''
                    INSERT INTO Inventory_Data (InventoryID, Price, ImageURL, BrandName, Size, Type, Gender, Speed, Frame, BrakeType, Age, Suspension, TireType, CustomerRating)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''', records)

            conn.commit()
            print("Records inserted successfully into Inventory_Data.")

        except sqlite3.Error as e:
            print(f"Database error: {e}")

    def write_logTable_to_db(self):
        """
        Creates a LogTable for recording late fees, damage charges, and repairs, if it doesn't exist.
        """
        try:
            with sqlite3.connect(self.db_name) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                CREATE TABLE IF NOT EXISTS LogTable (
                    LogID INTEGER PRIMARY KEY AUTOINCREMENT,
                    BicycleID INTEGER,
                    ActionDate DATE DEFAULT CURRENT_TIMESTAMP,
                    LateFee REAL DEFAULT NULL,
                    DamageCharge REAL DEFAULT NULL,
                    DamageNote TEXT DEFAULT NULL,
                    StatusChange TEXT,
                    FOREIGN KEY (BicycleID) REFERENCES Bicycle_Info (BicycleID)
                )''')
                
            conn.commit()
            print("Table created successfully.")

        except sqlite3.Error as e:
            print(f"Database error: {e}")
        finally:
            conn.close()

    def droptable(self, table_name):
        """
        Drops a specified table from the database, if it exists.
        
        Args:
            table_name (str): The name of the table to drop.
        
        Returns:
            bool: True if successful, None if an error occurs.
        """
        try:
            with sqlite3.connect(self.db_name) as conn:
                cursor = conn.cursor()
                cursor.execute(f'''DROP TABLE IF EXISTS {table_name}''')
                conn.commit()
                return True
        except sqlite3.Error as e:
            print(f"Database error: {e}")
            return None
        finally:
                conn.close()

    def dropviewtable(self, view_name):
        """
        Drops a specified view from the database, if it exists.
        
        Args:
            view_name (str): The name of the view to drop.
        
        Returns:
            bool: True if successful, None if an error occurs.
        """
        try:
            with sqlite3.connect(self.db_name) as conn:
                cursor = conn.cursor()
                cursor.execute(f"DROP VIEW IF EXISTS {view_name}")
                conn.commit()
                print(f"View '{view_name}' dropped successfully.")
                return True
        except sqlite3.Error as e:
            print(f"Database error while dropping view '{view_name}': {e}")
            return None
        finally:
                conn.close()
                
    def createViewTable(self):
        """
        Creates a BikesHistoryViews view in the database, combining Bicycle_Info and Rental_History 
        data for enhanced query capabilities.
        
        Returns:
            bool: True if successful, None if an error occurs.
        """
        try:
            with sqlite3.connect(self.db_name) as conn:
                cursor = conn.cursor()
                cursor.execute('''CREATE VIEW BikesHistoryViews AS
                    SELECT 
                        bi.BicycleID, bi.Brand, bi.Type, bi.FrameSize, bi.DailyRate, 
                        bi.WeeklyRate, bi.Status, bi.Condition, bi.DateOfPurchase, bi.InventoryID,
                        rh.RentalDate, rh.ReturnDate                       
                    FROM 
                        Bicycle_Info bi
                    LEFT JOIN Rental_History rh ON bi.BicycleID = rh.BicycleID                  
                ''')
                conn.commit()
                print("BikeRecommendationView created successfully.")
                return True
        except sqlite3.Error as e:
            print(f"Database error while creating view: {e}")
            return None
        finally:
                conn.close()
    
class databaseOperations(writeToSql):
    """
    DatabaseOperations class.

    This class handles various database operations for a bicycle rental system, 
    utilizing object-oriented programming techniques to promote reusability and maintainability.
    The class integrates with an SQLite database to perform tasks such as validating memberships, 
    retrieving inventory data, managing rental history, and calculating late fees.

    Key responsibilities:
    - Membership validation
    - Bicycle information retrieval
    - Rental status checking and management
    - Fee calculation for overdue rentals

    Methods are designed for modularity, making it easy to extend and maintain while allowing 
    the main application to interact with the database in a streamlined manner.
    """
    def __init__(self, db_name='BicycleRental.db'):
        """Initialize with database name and load membership data."""
        super().__init__(db_name)
        self.memberships = M.load_memberships("members.txt")  

    def validate_member(self, member_id):
        """Validate membership status and rental limit for a given member ID."""
        member_id = str(member_id)
        if member_id not in self.memberships:
            return False, "Invalid Member ID."
        
        if not M.check_membership(member_id, self.memberships):
            return False, "Inactive membership."
        
        rental_limit = int(M.get_rental_limit(member_id, self.memberships))
        current_rentals = self.get_currentRentals(member_id)
        
        if current_rentals >= rental_limit:
            return False, "Rental limit exceeded."

        return True, "Membership is valid."

    def read_BicycleInfoTable(self):
        """Retrieve all records from the Bicycle_Info table."""
        try:
            with sqlite3.connect(self.db_name) as conn:
                cursor = conn.cursor()
                cursor.execute('''SELECT * FROM Bicycle_Info''')
                results = cursor.fetchall() 
                return results
                
        except sqlite3.Error as e:
            print(f"Database error: {e}")
            return None
        finally:
            conn.close()

    def read_RentalHistoryTable(self):
        """Retrieve all records from the Rental_History table."""
        try:
            with sqlite3.connect(self.db_name) as conn:
                cursor = conn.cursor()
                cursor.execute('''SELECT * FROM Rental_History''')
                results = cursor.fetchall()  
                return results
                
        except sqlite3.Error as e:
            print(f"Database error: {e}")
            return None
        finally:
            conn.close()

    def read_InventoryDataTable(self):
        """Retrieve all records from the Inventory_Data table."""
        try:
            with sqlite3.connect(self.db_name) as conn:
                cursor = conn.cursor()
                cursor.execute('''SELECT * FROM Inventory_Data''')
                results = cursor.fetchall()  
                return results
                
        except sqlite3.Error as e:
            print(f"Database error: {e}")
            return None
        finally:
            conn.close()

    def read_BikeRecommendatonView(self):
        """Retrieve data from BikesHistoryViews."""
        try:
            with sqlite3.connect(self.db_name) as conn:
                cursor = conn.cursor()
                cursor.execute('''SELECT * FROM BikesHistoryViews''')
                results = cursor.fetchall()  
                return results
                
        except sqlite3.Error as e:
            print(f"Database error: {e}")
            return None
        finally:
            conn.close()
        

    def searchBicycles(self, search_value, search_field):
        """
        Search bicycles by a specified field and value.
        
        Parameters:
            search_value (str): Value to search for (e.g., 'Mountain Bike').
            search_field (str): Field to search in (e.g., 'Type', 'FrameSize', 'Brand').
        
        Returns:
            list: Matched bicycle records, with Image URLs if available.
        """
        valid_fields = {'type': 'Type', 'frame_size': 'FrameSize', 'brand': 'Brand'}
        field_column = valid_fields.get(search_field.lower())
        if not field_column:
            print(f"Invalid search field: {search_field}. Valid options are: {', '.join(valid_fields.keys())}")
            return []

        try:
            with sqlite3.connect(self.db_name) as conn:
                cursor = conn.cursor()
                query = f'''SELECT * FROM Bicycle_Info WHERE LOWER({field_column}) = LOWER(?)'''
                cursor.execute(query, (search_value,))
                results = cursor.fetchall()
                image_data = self.get_Images()
                image_dict = {image[0]: image[1] for image in image_data}
                merged_results = []

                for row in results:
                    inventory_id = row[-1]
                    image_url = image_dict.get(inventory_id, None)

                    merged_results.append(row + (image_url,))
                    
                return merged_results  
                if merged_results:
                    return merged_results
                else:
                    return []

        except sqlite3.Error as e:
            print(f"Database error: {e}")
            return []
        finally:
            conn.close()

    def get_uniquevalues(self):
        """Retrieve distinct values for Type, Brand, and FrameSize from Bicycle_Info."""
        try:
            with sqlite3.connect(self.db_name) as conn:
                cursor = conn.cursor()
                cursor.execute('''SELECT DISTINCT Type FROM Bicycle_Info''')
                results_type = [row[0] for row in cursor.fetchall()]  # Return as a list of values
                cursor.execute('''SELECT DISTINCT Brand FROM Bicycle_Info''')
                results_brand = [row[0] for row in cursor.fetchall()]   
                cursor.execute('''SELECT DISTINCT FrameSize FROM Bicycle_Info''')
                results_framesize = [row[0] for row in cursor.fetchall()]  
            return results_type, results_brand, results_framesize
                
        except sqlite3.Error as e:
            print(f"Database error: {e}")
            return None
        finally:
            conn.close()
        
    def know_rentalStatus(self, bicycle_id):
        """Check if a bicycle is available for rent by Bicycle ID."""
        try:
            with sqlite3.connect(self.db_name) as conn:
                cursor = conn.cursor()
                cursor.execute('''SELECT Status FROM Bicycle_Info WHERE BicycleID = ?''', (bicycle_id,))
                results = cursor.fetchone()  
                if not results:
                    return False, f"Invalid Bicycle ID: {bicycle_id}"
                elif results[0].lower() != "available":
                    return False, f"{bicycle_id} not avaliable"
            return True, f"bicycle is available for Bicycle ID: {bicycle_id}"
                
        except sqlite3.Error as e:
            print(f"Database error: {e}")
            return None
        finally:
            conn.close()

    def verify_bicycleIDRentalStatus(self, bicycle_id):
        """Verify bicycle ID and rental status; returns confirmation if rented."""
        try:
            with sqlite3.connect(self.db_name) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT BicycleID, Status 
                    FROM Bicycle_Info 
                    WHERE BicycleID = ?
                ''', (bicycle_id,))
                result = cursor.fetchone()

                if result is None:
                    return False, f"Bicycle ID - {bicycle_id} not found."
                
                _, status = result
                if status.lower() == 'rented':
                    return True, f"Bicycle ID - {bicycle_id} and rental status verified."
                else:
                    return False, f"Bicycle ID - {bicycle_id} found, but rental status is not 'rented'."
                
        except sqlite3.Error as e:
            print(f"Database error: {e}")
            return None
        finally:
            conn.close()

    
    def return_lateFeesCalculation(self, bicycle_id):
        """Calculates late fees if applicable and handles future return dates."""
        try:
            with sqlite3.connect(self.db_name) as conn:
                cursor = conn.cursor()
                
                # Get the most recent rental record for the specified bicycle
                cursor.execute('''
                    SELECT B.DailyRate, R.RentalDate, R.ReturnDate 
                    FROM Rental_History R 
                    JOIN Bicycle_Info B ON R.BicycleID = B.BicycleID
                    WHERE B.BicycleID = ? AND LOWER(B.Status) = LOWER('rented')
                    ORDER BY R.RentalDate DESC
                    LIMIT 1
                ''', (bicycle_id,))
                
                result = cursor.fetchone()
                
                if not result:
                    return None, f"No rental record found for bicycle ID: {bicycle_id}."

                daily_rate, rental_date, return_date = result
                actual_return_date = datetime.datetime.now().date()
                return_date = datetime.datetime.strptime(return_date, "%Y-%m-%d").date()

                if return_date > actual_return_date:
                    return None, f"**Bicycle ID**: {bicycle_id} has a scheduled return date of **{return_date}**, which is in the future. **Return cannot be processed.**"

                overdue_days = (actual_return_date - return_date).days
                late_fee = 0
                if overdue_days > 0:
                    late_fee = overdue_days * (daily_rate + 5) 
                    records = late_fee, return_date
                    return records, f"Late fee applicable for bicycle ID {bicycle_id}. Charged £{late_fee} for {overdue_days} days overdue."
                else:
                    return False, f"There is no late fee charge for bicycle ID {bicycle_id}."

        except sqlite3.Error as e:
            print(f"Database error: {e}")
            return None
        finally:
            conn.close()

    def know_rentedDetails(self, bicycle_id):
        """Retrieve rental details for a given bicycle ID if still rented."""
        try:
            with sqlite3.connect(self.db_name) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT B.Brand, B.Type, B.DailyRate, B.WeeklyRate, B.Status, R.RentalDate, R.ReturnDate
                    FROM Bicycle_Info B 
                    JOIN Rental_History R ON B.BicycleID = R.BicycleID
                    WHERE R.BicycleID = ? AND R.ReturnDate > DATE('now')
                ''', (bicycle_id,))
                results = cursor.fetchone()  

                if results:
                    brand, bike_type, daily_rate, weekly_rate, status, rental_date, return_date = results
                    return True, {
                        "Bicycle ID": bicycle_id,
                        "Brand": brand,
                        "Type": bike_type,
                        "Daily Rate": daily_rate,
                        "Weekly Rate": weekly_rate,
                        "Status": status,
                        "Rental Date": rental_date,
                        "Return Date": return_date
                    }
                else:
                    return False, f"Invalid Bicycle ID: {bicycle_id}"
                    
        except sqlite3.Error as e:
            print(f"Database error: {e}")
            return None
        finally:
            conn.close()

    def get_currentRentals(self,member_id):
        """Check how many active rentals with the given member ID to validate rental limit"""
        try:
            with sqlite3.connect(self.db_name) as conn:
                cursor = conn.cursor()
                cursor.execute('''SELECT COUNT(*) FROM Rental_History WHERE MemberID = ? AND  DATE(ReturnDate) > DATE('now')''', (member_id,))
                results = cursor.fetchone()[0]  

                if results>=0:
                    return results
                else:
                    return f"No bicycles active rental for this member ID: {member_id}"
                
        except sqlite3.Error as e:
            print(f"Database error: {e}")
            return None
        finally:
            conn.close()

    def get_Images(self):
        """Retrive the images based on inventory id, for display"""
        try:
            with sqlite3.connect(self.db_name) as conn:
                cursor = conn.cursor()
                cursor.execute('''SELECT id.InventoryID,id.ImageURl
                                FROM Inventory_Data id JOIN Bicycle_Info bi
                                ON id.InventoryID = bi.InventoryID''')
                results = cursor.fetchall()  

                if results:
                    return results
                else:
                    return []
                
        except sqlite3.Error as e:
            print(f"Database error: {e}")
            return None
        finally:
            conn.close()

class databaseWriteOperations(writeToSql):
    """
    The `databaseWriteOperations` class is part of a bicycle rental management system, utilizing object-oriented programming
    techniques to maintain, update, and log rental and return information for bicycles in a SQLite3 database. This class
    provides reusable and maintainable methods for handling operations such as renting bicycles, processing returns, and
    logging details of rentals and damage reports. By defining operations in discrete methods, the class ensures easy
    integration with other database operations and improves readability and maintainability.
    
    Key Functionalities:
    - Write rental information to the database and update bicycle status.
    - Process bicycle returns, update conditions, and handle damage charges.
    - Log late fees, damage reports, and other pertinent details.
    """
    def __init__(self, db_name='BicycleRental.db'):
        """
        Initializes the database connection and loads membership data.
        
        Parameters:
        - db_name (str): The name of the SQLite database file. Defaults to 'BicycleRental.db'.
        """
        super().__init__(db_name)
        self.memberships = M.load_memberships("members.txt")  # Load memberships data

    def write_rentingBicycle(self, member_id, bicycle_id, rental_days = 1):
        """
        Records a bicycle rental in the database and updates the bicycle's status to "Rented".
        
        Parameters:
        - member_id (int): ID of the member renting the bicycle.
        - bicycle_id (int): ID of the bicycle being rented.
        - rental_days (int): Number of days for the rental. Defaults to 1 day.
        
        Returns:
        - True if rental record is successfully inserted, None if an error occurs.
        """
        try:
            rental_date = datetime.date.today()
            return_date = rental_date + datetime.timedelta(days=rental_days)
            with sqlite3.connect(self.db_name) as conn:
                cursor = conn.cursor()
                cursor.execute('''UPDATE Bicycle_Info SET Status = "Rented" WHERE BicycleID = ?''', (bicycle_id,))
                cursor.execute('''
                    INSERT INTO Rental_History (BicycleID, MemberID, RentalDate, ReturnDate)
                    VALUES (?, ?, ?, ?)
                    ''', (bicycle_id, member_id, rental_date, return_date))
                conn.commit()
                return True
        except sqlite3.Error as e:
            print(f"Database error: {e}")
            return None
        finally:
            conn.close()
       
    def write_returnUpdate(self, bicycle_id,damage_charge=0, return_date=None):
        """
        Updates the status and condition of a returned bicycle based on damage charges and logs the return date.
        
        Parameters:
        - bicycle_id (int): ID of the returned bicycle.
        - damage_charge (int): Charge for any damages, defaults to 0.
        - return_date (datetime, optional): Expected return date for validating actual return.
        
        Returns:
        - Tuple containing success status and message indicating updated status and condition.
        """
        try:
            update_date = datetime.date.today()
            with sqlite3.connect(self.db_name) as conn:
                cursor = conn.cursor()
                new_status = "Available" if damage_charge == 0 else "Unavailable"
                new_condition = "Good" if damage_charge == 0 else "Damaged"
                cursor.execute('''
                    UPDATE Bicycle_Info
                    SET Status = ?, Condition = ?
                    WHERE BicycleID = ?
                    ''', (new_status, new_condition, bicycle_id))
                if return_date:
                    cursor.execute('''UPDATE Rental_History SET ReturnDate = ? WHERE BicycleID = ? AND ReturnDate = ?''', (update_date, bicycle_id, return_date))
                    conn.commit()
                    return True, f"BicycleID- {bicycle_id}'s, status {new_status} and condition {new_condition} along with the return date in Rental_History table {update_date}"
                return True, f"BicycleID- {bicycle_id}'s, status {new_status} and condition {new_condition}"
        except sqlite3.Error as e:
            print(f"Database error: {e}")
            return None
        finally:
            conn.close()

    def write_inLogtable(self, bicycle_id, late_fee = 0, damage_charge=0, damage_note=None):
        """
        Logs bicycle return details into the LogTable, recording late fees, damage charges, and notes.
        
        Parameters:
        - bicycle_id (int): ID of the bicycle being logged.
        - late_fee (int): Fee for late return, defaults to 0.
        - damage_charge (int): Charge for any damages, defaults to 0.
        - damage_note (str, optional): Note describing the damage.
        
        Returns:
        - True if log entry is successfully added, None if an error occurs.
        """
        try:
            with sqlite3.connect(self.db_name) as conn:
                cursor = conn.cursor()
                # Update return_date
                cursor.execute('''INSERT INTO LogTable (BicycleID, LateFee, DamageCharge, DamageNote, StatusChange) VALUES (?, ?, ?, ?, ?)''',
                               (bicycle_id, late_fee, damage_charge, damage_note, "Damaged" if damage_charge > 0 else "Good"))
                conn.commit()
                return True
        except sqlite3.Error as e:
            print(f"Database error: {e}")
            return None
        finally:
            conn.close()

def test():
    """
    Test function for debugging and verifying database operations.
    
    This function acts as a comprehensive tester for database operations
    related to bicycle inventory, rentals, and membership validations. It:
    - Creates instances for interacting with the database.
    - Tests various database operations such as fetching images, searching,
      creating views, inserting data, and calculating fees.
    - Provides clear output for each operation to assist with debugging.
    
    Prerequisites:
        - Database tables and views must be initialized.
        - Input files should be available if file reading is enabled.
    """
    # Initialize database instance and handlers
    database = writeToSql()  # Assuming this sets up a database connection
    handler = databaseOperations()  # Handles general database queries
    writer = databaseWriteOperations()  # Manages database write operations
    try:
        # File read and database write operations
        print("Reading inventory data from file and writing to database...")
        inventory_records = readFromFile.read_InventoryData_from_file()
        if inventory_records:
            database.write_InventoryData_to_db(inventory_records)
            print("Inventory data inserted successfully.")
        else:
            print("No inventory data found to insert.")

        print("Reading bicycle info from file and writing to database...")
        bicycle_info_records = readFromFile.read_bicycleInfo_from_file()
        if bicycle_info_records:
            database.write_bicycleData_to_db(bicycle_info_records)
            print("Bicycle info inserted successfully.")
        else:
            print("No bicycle info found to insert.")

        print("Reading rental history from file and writing to database...")
        rental_history_records = readFromFile.read_rentalHistory_from_file()
        if rental_history_records:
            database.write_rentalData_to_db(rental_history_records)
            print("Rental history data inserted successfully.")
        else:
            print("No rental history data found to insert.")

        print("Creating new view table...")
        if database.createViewTable():
            print("View created successfully.")
        else:
            print("Failed to create view.")

        # dropping a view
        print("Dropping view table if exists...")
        if database.dropviewtable('read_BikesRecommendationView'):
            print("View dropped successfully.")
        else:
            print("View not found or unable to drop.")

        drop = database.droptable('Bicycle_Info')
        if drop is True:
            print('Dropped successfully given table')
        else:
            print("Table not found or unable to drop.")

        # Test retrieval and search functionalities
        print("Retrieving all bicycle info records...")
        bicycle_info = handler.read_BicycleInfoTable()
        print("Bicycle Info:", bicycle_info)

        print("Reading inventory data table...")
        inventory_data = handler.read_InventoryDataTable()
        print("Inventory Data:", inventory_data)

        print("Reading from Bike Recommendation View...")
        bike_recommendations = handler.read_BikeRecommendatonView()
        print("Bike Recommendations:", bike_recommendations)

        print("Testing bicycle search by frame size...")
        large_bikes = handler.searchBicycles('Large', 'frame_Size')
        print("Bicycles with Large frame size:", large_bikes)
        
        print("Unique Values of TYpe, Brand and Frame Size to display in the program")
        results_type, results_brand, results_framesize = handler.get_uniquevalues()
        print("Unique Values:", results_type, results_brand, results_framesize)

        # Test rental and membership functionalities
        print("Checking Member validation for renting...")
        valid_Member = handler.validate_Member('1021')
        print("Member ID:", valid_Member)
        
        print("Checking rental status for bicycle ID '12'...")
        rental_status = handler.know_rentalStatus('12')
        print("Rental status:", rental_status)

        print("Getting current rentals for member ID 1015...")
        current_rentals = handler.get_currentRentals(1015)
        print("Current rentals for member 1015:", current_rentals)

        print("Validating membership for member ID 1015...")
        is_valid_member = handler.validate_member(1015)
        print("Is member valid:", is_valid_member)

        print("Calculating late fees for bicycle ID '42'...")
        late_fees = handler.return_lateFeesCalculation('42')
        print("Late fees:", late_fees)

        print("the bicycleID which already rented know its details")
        result = handler.know_rentedDetails('9')
        print("Details: ",result)

        print("check where the bicycle id is rented or not")
        result = handler.verify_bicycleIDRentalStatus('55')
        print("Rental Status: ",result)
        database.write_logTable_to_db()

        print("get all images from inventory_data table whose inventoryid are in bicyle_info table")
        image = handler.get_Images()
        print("Image URls from Inventory Data",image)
        
        print("Writing rental record for member ID 1015, bicycle ID 9...")
        writer.write_rentingBicycle(1015, 9, 1)
        print("Rental record written.")
        
        print("Update the rental records in bicycle_info table, bicycle ID, damage charge, return date")
        writer.write_rentingUpdate('9', 100, '1/9/2024')
        print("Rental update written.")

        print("Update the rental records into logTable, bicycle ID, late fees, damage charge, damage note")
        writer.write_rentingUpdate('9', 100, 10, "brake damage")
        print("Rental log records written.")
    

   
    except Exception as e:
        print("An error occurred during testing:", e)

# Main workflow
if __name__ == "__main__":
    """
    Entry point for running the test function.
    Executes the test function to validate database operations.
    """
    test()


    


