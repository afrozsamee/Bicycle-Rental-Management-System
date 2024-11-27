"""
    StudentID : F418164
    Aim of this program is provide functionality for renting a bike. 
    It uses object-oriented programming (OOP) techniques to promote reusability, maintainability, and organization.
    This class interacts with the database to validate members, check bicycle availability, and process rental transactions.
    By employing methods for specific operations like renting a bicycle and calculating rental costs, the class ensures
    modularity and easy maintenance. The system is designed to be extended or modified with minimal changes due to its
    clear separation of concerns.
"""
import datetime
from database import *

class BicycleRentalSystem:
    """
    BicycleRentalSystem is a class designed to handle the bicycle rental operations. 
    This class interacts with the database to validate members, check bicycle availability, and process rental transactions.
    By employing methods for specific operations like renting a bicycle and calculating rental costs, the class ensures
    modularity and easy maintenance.
    """
    def __init__(self):
        """
        Initializes the BicycleRentalSystem class. 
        Sets up database operations for interacting with the database.
        """
        self.db_operations = databaseOperations() # Object for handling database queries
        self.db_write = databaseWriteOperations() # Object for writing data to the database

    def rent_bicycle(self, member_id, bicycle_id, rental_days=1):
        """
        Processes the bicycle rental transaction.
        
        Validates the member and checks the rental status of the bicycle.
        If valid, calculates the rental cost based on daily/weekly rates,
        if rental days are more than 7 days weekly cost will be applied and 
        returns a rental confirmation message.
        
        Args:
            member_id (int): ID of the renting member.
            bicycle_id (int): ID of the bicycle being rented.
            rental_days (int): Number of days for the rental. Default is 1 day.
        
        Returns:
            str: A message indicating the rental status and details.
        """
        # Validate the member ID
        valid_member, member_message = self.db_operations.validate_member(member_id)
        if not valid_member:
            return f"Rental failed: {member_message}"
        
        # Check if the bicycle is available for rent
        available_bike, bike_message = self.db_operations.know_rentalStatus(bicycle_id)
        if not available_bike:
            return f"Rental failed: {bike_message}"
        
        # Rent the bicycle and write to the database
        rental_result = self.db_write.write_rentingBicycle(member_id, bicycle_id, rental_days)
        if rental_result is None:
            return "Rental failed due to a database error."

        # Retrieve details of the rented bicycle
        bike_details = self.db_operations.know_rentedDetails(bicycle_id)
        
        # If bike details are found, proceed with rental confirmation
        if bike_details[0]:  
            details = bike_details[1]

            # Calculate the rental cost based on the rental days
            if rental_days >= 7:
                weeks = rental_days // 7
                extra_days = rental_days % 7
                rental_paid = (weeks * details['Weekly Rate']) + (extra_days * details['Daily Rate'])
            else:
                rental_paid = rental_days * details['Daily Rate']

            # Prepare confirmation message with rental details
            confirmation_message = (
                f"**Rental Confirmed!**\n"
                f"- Bicycle ID: **{details['Bicycle ID']}**\n"
                f"- Bicycle: {details['Brand']} - {details['Type']}\n"
                f"- Daily Rate: **£{details['Daily Rate']}**\n"
                f"- Weekly Rate: **£{details['Weekly Rate']}**\n"
                f"- Total Price: **£{rental_paid:.2f}**\n"  
                f"- Status: **{details['Status']}**\n"
                f"- Rental Start: {details['Rental Date']}\n"
                f"- Expected Return: **{details['Return Date']}**\n"
            )
            return confirmation_message
        else:
            return "Rental confirmed, but bicycle details could not be retrieved."


def test():
    """
    A test function for debugging and verifying bicycle rental transactions.
    
    This function allows a user to input member and bicycle IDs and the number of rental days.
    It simulates the renting process by calling the `rent_bicycle` method of the BicycleRentalSystem class,
    and prints the result to verify that the system is working as expected.
    """
    rental_system = BicycleRentalSystem()
    
    # Prompt for member and bicycle IDs and rental days from the user
    member_id = input("Enter Member ID: ")
    bicycle_id = input("Enter Bicycle ID: ")
    rental_days = int(input("Enter number of days want to rent the bike for default is 1:"))

    # Attempt to rent a bicycle and display the result
    result = rental_system.rent_bicycle(member_id, bicycle_id, rental_days)
    print(result)

if __name__ == "__main__":
    """
    Debugs the code using test function
    """
    test()
