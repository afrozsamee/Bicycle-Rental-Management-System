"""
    StudentID : F418164
    This system leverages Object-Oriented Programming (OOP) principles to provide modularity, reuseability, 
    and maintainability. The system encapsulates the process of verifying the bicycle ID, calculating late fees, 
    processing damage charges, updating bicycle statuses, and logging the return details.
    
    By using OOP, this program can easily be extended with additional features, and its components can be reused 
    in other contexts where bicycle rentals are managed. Furthermore, each method is designed to focus on a specific 
    task, making the system easy to maintain and update.  
"""
import datetime
from database import *

# Global Variables
LATE_FEE = 0  # Late fee per day
DAMAGE_CHARGE = 0  # Initialize default damage charge

class BicycleReturnSystem:
    """
    BicycleReturnSystem handles the process of returning a rented bicycle.
    The system encapsulates the process of verifying the bicycle ID, calculating late fees, 
    processing damage charges, updating bicycle statuses i the bicycle_info table,
    for late returns updates in the rental history table correct return date and logging the return details.
    """
    def __init__(self):
        """
        Initializes the BicycleReturnSystem with necessary database operations and default charges.
        
        Creates instances of databaseOperations and databaseWriteOperations for interacting with the database.
        Initializes late_fee and damage_charge to default values.
        """
        self.db_operations = databaseOperations()
        self.db_write = databaseWriteOperations()
        self.late_fee = LATE_FEE
        self.damage_charge = DAMAGE_CHARGE

    def id_verification(self, bicycle_id):
        """
        Verifies the bicycle's ID and rental status.
        
        Args:
            bicycle_id (int): The ID of the bicycle being returned.
        
        Returns:
            tuple: A tuple containing a boolean verification status and a message.
        """
        # Step 1: Verify the bicycle ID and rental status
        verified, message = self.db_operations.verify_bicycleIDRentalStatus(bicycle_id)
        return verified,message

    def process_return(self, bicycle_id, damage_charge=0, damage_note=None):
        """
        Manages the bicycle return process including verification, late fee calculation, damage charge handling, 
        and logging of return details.
        
        Args:
            bicycle_id (int): The ID of the bicycle being returned.
            damage_charge (float, optional): The damage charge applied (default is 0).
            damage_note (str, optional): A note describing the damage, if any (default is None).
        
        Returns:
            str: A summary message of the return process, including charges and status.
        """
        # Step 2: Calculate late fees, if applicable
        records, late_fee_message = self.db_operations.return_lateFeesCalculation(bicycle_id)
        if records is None:
            return late_fee_message
        elif records:
            self.late_fee, return_date = records 
            late_fee_status = late_fee_message
        else:
            return_date = None
            late_fee_status = "No late fee."

        # Step 3: Update bicycle's condition and status based on damage
        self.damage_charge = damage_charge  
        status_update_result, message = self.db_write.write_returnUpdate(
            bicycle_id, damage_charge=self.damage_charge, return_date=return_date
        )

        # Step 4: Log the return information in LogTable
        log_result = self.db_write.write_inLogtable(
            bicycle_id,
            late_fee=self.late_fee,
            damage_charge=self.damage_charge,
            damage_note=damage_note
        )

        # If logging was successful, return the detailed summary of the return
        if log_result:
            total_charge = self.late_fee + self.damage_charge
            return_message = (
                f"**Return Summary for Bicycle ID: {bicycle_id}**\n"
                f"- Return Status: Successfully returned\n"
                f"- Late Fee: £{self.late_fee:.2f}\n"
                f"- Damage Charge: £{self.damage_charge:.2f}\n"
                f"- Total Charges: **£{total_charge:.2f}**\n"
                f"- Damage Note: {damage_note if damage_note else 'None'}\n"
            )
            return return_message
        else:
            return (f"Failed to process return for Bicycle ID: {bicycle_id}")

def test():
    """
    Main function to simulate the return process of a bicycle.
    
    It takes user input for the bicycle ID, verifies the ID, and processes the return 
    along with any damage charge or notes provided by the user.
    """
    # Create an instance of the return process handler
    return_process = BicycleReturnSystem()

    bicycle_id = int(input("Enter the Bicycle ID to return: "))
    verify = return_process.id_verification(bicycle_id)
    if verify:
        # Test return with damage charge
        try:
            test_damage_charge = float(input("Enter the damage charge (if any, otherwise enter 0): "))
        except ValueError:
            print("Invalid input for damage charge. Setting to 0.")
            test_damage_charge = 0  # Default if input is invalid

        test_damage_note = input("Enter a description of the damage (leave blank if none): ") or None

        return_process.process_return(bicycle_id, damage_charge=test_damage_charge, damage_note=test_damage_note)
    
if __name__ == "__main__":
    """
    Testing the Bicycle Return Process
    """
    test()
    
