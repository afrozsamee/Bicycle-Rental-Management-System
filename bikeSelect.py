import pandas as pd
import numpy as np
import sqlite3
from database import *
from datetime import datetime
from IPython.display import display, clear_output, Markdown, HTML
import matplotlib.pyplot as plt
from matplotlib.font_manager import FontProperties
import matplotlib.font_manager as fm
import matplotlib.animation as animation
from matplotlib.collections import PathCollection

"""
    StudentID : F418164
    The Aim of this program is to provide a accurate recommendation to the user for replacing old/damaged
    bikes and recommending new purchases depending upon given user budget and use matplotlib packages to displace relations of recommendations
"""

class BicycleSelectionSystem:
    """
    Bicycle selection and recommendation system for rental operations.

    This class is built using object-oriented programming (OOP) principles, enabling modularity, 
    reusability, and maintainability of the rental system. By encapsulating database operations 
    and business logic within separate classes, we can easily maintain and extend the functionality.

    The class allows:
    - Fetching rental history-based recommendations
    - Fetching future bicycle availability data for recommendations

    Reusability is achieved by using database operations as separate reusable modules, 
    and maintainability is ensured by keeping the code organized and clear.
    """

    def __init__(self, db_name='BicycleRental.db'):
        """
        Initialize the rental system and establish database operations.

        Args:
        db_name (str): Name of the SQLite database file (default 'BicycleRental.db').
        """
        self.db_name = db_name
        self.db_operations = databaseOperations() # Handles database queries
        self.db_write = databaseWriteOperations() # Handles database write operations

    def historyRecommendation(self):
        """
        Fetch rental history recommendations from the database.

        This function queries the 'BikesHistoryViews' view in the database to get a
        list of previously rented bicycles and their rental history.

        Returns:
        pd.DataFrame: DataFrame containing rental history data, or None if error occurs.
        """
        try:
            with sqlite3.connect(self.db_name) as conn:
                df = pd.read_sql_query("SELECT * FROM BikesHistoryViews", conn)
                return df
        except sqlite3.Error as e:
            print(f"Database error: {e}")
            return None

    def futureRecommendation(self):
        """
        Fetch future recommendations based on unused bicycles in the inventory.

        This function queries the 'Inventory_Data' table to get a list of bicycles 
        that are available for future rentals.

        Returns:
        pd.DataFrame: DataFrame containing available bicycles, or None if error occurs.
        """
        try:
            with sqlite3.connect(self.db_name) as conn:
                df = pd.read_sql_query("""SELECT * FROM Inventory_Data;""", conn)
                return df
        except sqlite3.Error as e:
            print(f"Database error: {e}")
            return None

class BikeRecommendationSystem(BicycleSelectionSystem):
    """
    BikeRecommendationSystem utilizes data from past rental history and future predictions to recommend bicycles 
    based on various factors such as rental frequency, durability, condition, and bike age. This class leverages 
    object-oriented programming techniques for reusability, maintainability, and scalability. It supports the 
    recommendation of both the best and worst bicycles by analyzing historical data and preparing future 
    recommendations while also allowing budget-based filtering.

    Key features:
    - Calculate durability scores based on condition, status, and recency.
    - Clean and prepare data for generating recommendations.
    - Generate good and bad bike recommendations based on calculated scores.
    - Filter recommendations based on budget for future purchases.

    In this class, inheritance is used from `BicycleSelectionSystem` to extend functionalities for bike 
    recommendations, ensuring a modular and maintainable codebase.
    """
    def __init__(self):
        """
        Initializes the BikeRecommendationSystem by loading the historical and predicted bike data.
        Sets up data preparation and recommendation dataframes.

        Attributes:
            HistoryRecommendation_df (DataFrame): Historical data for bike rentals.
            PredictRecommendation_df (DataFrame): Predicted future data for bikes.
            recommendation_df (DataFrame): Data prepared for recommendations.
        """
        super().__init__()
        # Load historical and predicted bike data
        self.HistoryRecommendation_df = self.historyRecommendation()
        self.PredictRecommendation_df = self.futureRecommendation()

        # Prepare the recommendation DataFrame once during initialization
        self.recommendation_df = self.data_cleaningPreparation()
        if self.recommendation_df is not None:
            self.recommendation_df = self.prepare_recommendation_df(self.recommendation_df)

    def calculate_durability(self, row):
        """
        Calculates the durability score for a bike based on its condition, status, and recency of use.

        Args:
            row (DataFrame row): Data for a specific bike.

        Returns:
            float: Durability score calculated from condition, status, and time factor.
        """
        try:
            # Condition score based on bike's condition
            condition_score = {'New': 3, 'Good': 2, 'Damaged': 1}.get(row['Condition'], 0)
            
            # Status score based on bike's current status
            status_score = {'Available': 2, 'Rented': 1, 'Under Maintenance': 0}.get(row['Status'], 0)
            
            # Calculate the time factor based on the last usage
            last_used_date = row['ReturnDate'] if pd.notnull(row['ReturnDate']) else row['RentalDate']
            if pd.notnull(last_used_date):
                days_since_last_used = (self.current_date - last_used_date).days
                time_factor = max(0, 1 - days_since_last_used / 365)
            else:
                time_factor = 0  # Lower time factor if no rental history available
            
            # Final durability score
            durability_score = (condition_score + status_score) * time_factor
            
            return durability_score
        except Exception as e:
            print(f"Error in calculating durability: {e}")
            return 0  # Return 0 if an error occurs

    def data_cleaningPreparation(self):
        """
        Prepares the data for recommendation by cleaning, merging, and calculating necessary metrics.

        Returns:
            DataFrame: A cleaned and prepared DataFrame for generating recommendations.
        """
        try:
            # Clean and prepare the history and predicted recommendation data
            self.HistoryRecommendation_df = self.HistoryRecommendation_df.fillna(0)
            self.PredictRecommendation_df = self.PredictRecommendation_df.rename(columns={'BrandName':'Brand'})
            
            # Mark bikes as 'inuse' or 'new' based on whether they appear in the history
            in_use_ids = self.HistoryRecommendation_df['InventoryID'].unique()
            self.PredictRecommendation_df['Condition'] = self.PredictRecommendation_df['InventoryID'].apply(
                lambda x: 'inuse' if x in in_use_ids else 'new'
            )
            
            # Convert date columns to datetime format
            self.current_date = datetime.now()
            self.HistoryRecommendation_df['DateOfPurchase'] = pd.to_datetime(self.HistoryRecommendation_df['DateOfPurchase'], errors='coerce')
            self.HistoryRecommendation_df['RentalDate'] = pd.to_datetime(self.HistoryRecommendation_df['RentalDate'], errors='coerce')
            self.HistoryRecommendation_df['ReturnDate'] = pd.to_datetime(self.HistoryRecommendation_df['ReturnDate'], errors='coerce')

            # Calculate Rental Frequency for each bike type and brand
            rental_frequency = self.HistoryRecommendation_df.groupby(['Type', 'Brand']).size().reset_index(name='RentalFrequency')
            

            # Calculate bike age based on the DateOfPurchase
            self.HistoryRecommendation_df['BikeAge'] = self.HistoryRecommendation_df['DateOfPurchase'].apply(
                lambda x: (self.current_date - x).days / 365 if pd.notnull(x) else None)

            # Apply durability score calculation
            self.HistoryRecommendation_df['DurabilityScore'] = self.HistoryRecommendation_df.apply(self.calculate_durability, axis=1)

            # Merge rental frequency with history dataframe
            recommendation_df = self.HistoryRecommendation_df.merge(rental_frequency, on=['Type', 'Brand'], how='left')
            return recommendation_df
        except Exception as e:
            print(f"Error during data preparation: {e}")
            return None  # Return None if an error occurs during data preparation


    def prepare_recommendation_df(self, recommendation_df):
        """
        Prepares the recommendation DataFrame by calculating scores based on rental frequency, durability, 
        and bike age.

        Args:
            recommendation_df (DataFrame): The DataFrame containing the bike data.

        Returns:
            DataFrame: The final recommendation DataFrame with calculated scores.
        """
        try:
            if recommendation_df is None:
                raise ValueError("Recommendation DataFrame is None.")
            
            # Weights for different factors in the recommendation
            Weight_1 = 1.5  # Rental Frequency Weight
            Weight_2 = 1.0  # Condition Weight
            Weight_3 = 0.8  # Age Weight

            # Calculate the final recommendation score
            recommendation_df['Score'] = (
                (recommendation_df['RentalFrequency'] * Weight_1) +
                (recommendation_df['DurabilityScore'] * Weight_2) -
                (recommendation_df['BikeAge'] * Weight_3)
            )

            # Sort by Score to identify top bikes
            recommendation_df.sort_values(by='Score', ascending=False, inplace=True)

            return recommendation_df
        except Exception as e:
            print(f"Error preparing recommendation DataFrame: {e}")
            return None  # Return None if an error occurs during preparation

    def filter_future_recommendations(self,final_recommendations, budget=5000):
        """
        Filters the future bike recommendations based on the budget and preferences.

        Args:
            final_recommendations (DataFrame): DataFrame containing final recommendations.
            budget (float): The budget available for purchasing bikes.

        Returns:
            DataFrame: Filtered recommendations within the given budget.
            float: Total amount spent.
            str: Status message indicating the result.
        """
        try:
            filtered_future_recommendations = pd.DataFrame()
            for _, row in final_recommendations.iterrows():
                target_type = row['Type']
                target_brand = row['Brand']
                filtered_df = self.PredictRecommendation_df[
                (self.PredictRecommendation_df['Brand'] == target_brand) &
                (self.PredictRecommendation_df['Type'] == target_type) &
                (self.PredictRecommendation_df['Condition'] == 'new')
                ]
                filtered_future_recommendations = pd.concat([filtered_future_recommendations, filtered_df])
            
            filtered_future_recommendations = filtered_future_recommendations.drop_duplicates().reset_index(drop=True)
            if filtered_future_recommendations.empty:
                print(f"No bikes found for brand: {target_brand}, type: {target_type}")
                return filtered_future_recommendations, 0, 'No bikes found within the budget and criteria.'
            # Initialize budget allocation and quantities
            total_spent = 0 
            quantities = [0] * filtered_future_recommendations.shape[0]  
            remaining_budget = budget  
            unit_increase_factor = 1  

            # Allocate budget to bikes
            while remaining_budget > 0:
                iteration_total_spent = 0  
                for i, row in filtered_future_recommendations.iterrows():
                    bike_price = row['Price']
                    units_to_add = unit_increase_factor
                    cost_for_units = (bike_price * units_to_add)

                    if remaining_budget >= cost_for_units:
                        quantities[i] += units_to_add  
                        remaining_budget -= cost_for_units  
                        iteration_total_spent += cost_for_units
                    else:
                        max_units = (remaining_budget // bike_price)
                        quantities[i] += max_units
                        remaining_budget -= (max_units * bike_price)
                        iteration_total_spent += (max_units * bike_price)

                if iteration_total_spent == 0:
                    break

                unit_increase_factor *= 1  # Adjust the unit increase factor

            total_spent = sum(quantities[i] * filtered_future_recommendations.iloc[i]['Price'] for i in range(len(filtered_future_recommendations)))
            filtered_future_recommendations.loc[:, 'RecommendedUnits'] = quantities
            total_spent = f"{total_spent:.2f}"
            filtered_future_recommendations.set_index(['ImageURL'], inplace=True)
            
            return filtered_future_recommendations, total_spent, 'Successful purchase recommendations within budget.'
        
        except Exception as e:
            print(f"Error in filter_future_recommendations: {e}")
            return pd.DataFrame(), 0, 'Error occurred while filtering recommendations.'



    def generate_goodrecommendations(self, top_n=10):
        """Generate top bike recommendations using the shared recommendation DataFrame."""
        try:
            if self.recommendation_df is None:
                raise ValueError("Recommendation DataFrame is not available.")

            grouped_recommendation_df = self.recommendation_df.groupby(
                ['InventoryID', 'Brand', 'Type'], as_index=False
            ).agg({
                'Score': 'max',
                'DurabilityScore': 'max',
                'RentalFrequency': 'max',
            })

            top_bikes = grouped_recommendation_df.nlargest(top_n, 'Score')

            enriched_top_bikes = pd.merge(
                top_bikes, 
                self.PredictRecommendation_df.drop(columns=['Brand', 'Type', 'Condition']),  # Avoid duplicates
                on='InventoryID', 
                how='left'
            )

            additional_columns = self.recommendation_df.drop(columns=['InventoryID', 'Brand', 'Type', 'DurabilityScore', 'RentalFrequency', 'Score']).columns
            
            additional_data = self.recommendation_df[['InventoryID'] + list(additional_columns)]

            final_recommendations = pd.merge(
                enriched_top_bikes, 
                additional_data.drop_duplicates('InventoryID'), 
                on='InventoryID', 
                how='left'
            )

            final_recommendations = final_recommendations.drop(columns=['CustomerRating','BicycleID','DailyRate','WeeklyRate','DateOfPurchase','RentalDate','ReturnDate'])
            final_recommendations.set_index(['ImageURL'], inplace=True)

            return (final_recommendations, "Recommendations based on top bikes from past rental patterns.")

        except Exception as e:
            print(f"Error generating good recommendations: {e}")
            return None, f'Error generating recommendations: {e}'
        
    def generate_badrecommendations(self, replace_n=10):
        """Generate bottom bike recommendations using the shared recommendation DataFrame."""
        try:
            if self.recommendation_df is None:
                raise ValueError("Recommendation DataFrame is not available.")

            grouped_recommendation_df = self.recommendation_df.groupby(
                ['InventoryID', 'Brand', 'Type'], as_index=False
            ).agg({
                'Score': 'min',
                'DurabilityScore': 'min',
                'RentalFrequency': 'min',
            })

            bad_bikes = grouped_recommendation_df.nsmallest(replace_n, 'Score')

            merged_bad_bikes = bad_bikes.merge(
                self.PredictRecommendation_df.drop(columns=['Brand', 'Type','Condition'], errors='ignore'),
                on='InventoryID',
                how='left'
            )
            additional_columns = self.recommendation_df.drop(columns=['InventoryID', 'Brand', 'Type', 'DurabilityScore', 'RentalFrequency', 'Score']).columns
            
            additional_data = self.recommendation_df[['InventoryID'] + list(additional_columns)]
            final_recommendations = pd.merge(
                merged_bad_bikes, 
                additional_data.drop_duplicates('InventoryID'), 
                on='InventoryID', 
                how='left'
            )
            final_recommendations = final_recommendations.drop(columns=['CustomerRating','BicycleID','DailyRate','WeeklyRate','DateOfPurchase','RentalDate','ReturnDate'])
            final_recommendations.set_index(['ImageURL'], inplace=True)
            return final_recommendations, 'Recommendations for bike replacements.'

        except Exception as e:
            print(f"Error generating bad recommendations: {e}")
            return None, 'Error generating bad recommendations.'

class display_graphs(BikeRecommendationSystem):
    """
    Class to handle displaying various plots related to bike recommendations.

    This class is part of the BikeRecommendationSystem program, designed to visualize bike purchase recommendations.
    It demonstrates the usage of object-oriented programming (OOP) principles such as inheritance, reusability, and maintainability.
    
    By inheriting from the `BikeRecommendationSystem` class, this class leverages functionality from its parent 
    while focusing on visual representation of the recommendations through various types of plots.
    The purpose of this class is to visualize recommendations in ways that help users make informed decisions, 
    improving system reusability and enhancing the user experience.

    The class provides functionality for plotting:
        1. Animated future purchase recommendations.
        2. Scatter plot of score, durability, and rental frequency.
        3. Rental frequency by brand and frame size.

    All plots are designed with enhanced visuals and dynamically updated content to allow users to easily track 
    their budget and rental choices.

    In addition, OOP techniques ensure that this class can be easily extended and maintained as the recommendation 
    system evolves over time.
    """
    
    def __init__(self):
        """Initialize the class and generate the recommendations."""
        super().__init__()  # Initialize the parent class
        
        self.good_recommendations, message = self.generate_goodrecommendations()
        self.bad_recommendations, bad_message = self.generate_badrecommendations()

    def plot_animated_future_recommendations(self, user_budget):
        """
        Plot an animated graph for future purchase recommendations, with dynamic updates for cumulative spending and 
        remaining budget.

        The plot dynamically visualizes the budget allocation by showing how much has been spent and how much is left
        as different bike units are purchased within the user-defined budget. This visualization helps users better understand
        how their budget can be used to make purchases.

        Args:
            user_budget (float): The total amount of money the user is willing to spend.

        Returns:
            HTML: The animated plot as HTML content to be rendered in a browser.
        """
        future_recommendations,total_spent, purchase_message = self.filter_future_recommendations(self.good_recommendations,user_budget)
        if future_recommendations.empty:
            print("No future recommendations available.")
            return

        # Sort recommendations by price to make the plot more meaningful
        future_recommendations = future_recommendations.sort_values(by='Price')
        prices = future_recommendations['Price'].values
        recommended_units = future_recommendations['RecommendedUnits'].values

        # Variables to track cumulative spending and remaining budget
        cumulative_spent = 0
        remaining_budget = user_budget
        units_bought = np.zeros(len(future_recommendations))
        cumulative_spent_list = []
        remaining_budget_list = []

        # Pre-calculate cumulative spending and remaining budget for each recommendation
        for i, (price, units) in enumerate(zip(prices, recommended_units)):
            cost = price * units
            if remaining_budget >= cost:
                cumulative_spent += cost
                remaining_budget -= cost
                units_bought[i] = units
            cumulative_spent_list.append(cumulative_spent)
            remaining_budget_list.append(remaining_budget)

        # Set font properties for the plot
        plt.rcParams['font.family'] = 'DejaVu Sans'
        plt.rcParams['font.size'] = 11

        # Create a figure and axis for the plot
        fig, ax = plt.subplots(figsize=(12, 5))
        fig.patch.set_facecolor('#f7f7f7')
        
        # Function to update each frame
        def animate(i):
            ax.clear()
            
            # Define color gradient for lines based on cumulative budget spent
            color_gradient = plt.cm.viridis(np.linspace(0, 1, len(cumulative_spent_list)))
            
            # Draw main line with gradient colors
            for j in range(1, i + 1):
                ax.plot(prices[j-1:j+1], units_bought[j-1:j+1], color=color_gradient[j], linewidth=2)
            
            # Enlarged marker at the current point
            ax.scatter(prices[:i+1], units_bought[:i+1], s=[100] * i + [200], color=color_gradient[:i+1], edgecolor='black', zorder=5)

            # Display cumulative budget details on each frame
            ax.text(1.0, 0.95, f'Total Spent: £{round(cumulative_spent_list[i], 2):.2f}\nBudget Left: £{round(remaining_budget_list[i], 2):.2f}', 
                    transform=ax.transAxes, fontsize=12, color='#1b5e20', verticalalignment='top', horizontalalignment='right', fontweight='bold')
            
            # Set title, labels, and limits with enhanced visuals
            ax.set_title(f"Purchase Recommendation with in budget", fontsize=18, fontweight='bold', color='#00796b')
            ax.set_xlabel("Price", fontsize=13, fontweight='bold', color='#37474f')
            ax.set_ylabel("Recommended Units", fontsize=13, fontweight='bold', color='#37474f')
            
            # Set axis limits dynamically
            max_units = np.max(units_bought) if np.max(units_bought) != 0 else 1  # Prevent zero-size limit
            ax.set_ylim(0, max_units * 1.2)
            ax.set_xlim(np.min(prices) * 0.8, np.max(prices) * 1.2)
            
            ax.grid(True, which='both', linestyle='--', linewidth=0.5, color='#b0bec5')
            
            # Add a legend dynamically
            if i == len(prices) - 1:
                ax.legend(['Budget Allocation Line'], loc='upper left', fontsize=10, frameon=True, framealpha=0.9)

        # Create and display the animated plot
        anim = animation.FuncAnimation(fig, animate, frames=len(future_recommendations), repeat=False)

        return HTML(anim.to_jshtml())
        

    def plot_score_durability_vs_rental_frequency(self):
        """
        Plot a scatter plot to visualize the relationship between rental frequency and durability score, 
        differentiating between good and bad recommendations.

        This plot helps to analyze the rental frequency and durability score for both good and bad recommendations 
        to better understand the performance of different bikes.

        Returns:
            None
        """
        # Create subplots for good and bad recommendations
        fig, axes = plt.subplots(1, 2, figsize=(10, 5), sharey=True)
        categories = ['Good Recommendations', 'Replacement Recommendation']
        dataframes = [self.good_recommendations, self.bad_recommendations]

        # Plot data for each category
        for ax, category, df in zip(axes, categories, dataframes):
            x = df['RentalFrequency']
            y = df['DurabilityScore']
            sizes = df['Score'] * 10  
            colors = df['Score']  

            scatter = ax.scatter(x, y, s=sizes, c=colors, cmap='viridis', alpha=0.7, edgecolors='w', linewidth=0.5)
            
            plt.colorbar(scatter, ax=ax, label='Score')
            
            ax.set_title(f'{category}')
            ax.set_xlabel('Rental Frequency')
            ax.set_ylabel('DurabilityScore')
        
        plt.tight_layout()
        plt.show()
        

    def plot_popularity_by_brand(self):
        """
        Plot rental frequency by brand and frame size, comparing good and bad recommendations.
        
        This plot visualizes which bike brands and frame sizes are most popular based on rental frequency, 
        helping users see trends in brand popularity.

        Returns:
            None
        """
        # Create a figure with subplots for each category
        fig, axes = plt.subplots(1, 2, figsize=(12, 6), sharey=True)
        categories = ['Good Recommendations', 'Replace Recommendations']
        dataframes = [self.good_recommendations, self.bad_recommendations]

        title_colors = ['#2a9d8f', '#e76f51']  
        font_prop = FontProperties(weight='bold')  

        for ax, category, df, color in zip(axes, categories, dataframes, title_colors):
            brand_counts = df.groupby(['Brand', 'FrameSize'])['RentalFrequency'].sum().sort_values(ascending=False)
            brands_frame_sizes = [f"{brand} ({frame_size})" for brand, frame_size in brand_counts.index]
            colors = plt.cm.plasma(np.linspace(0, 1, len(brand_counts)))
            
            bar_positions = np.arange(len(brands_frame_sizes))
            bars = ax.bar(bar_positions, brand_counts.values, color=colors, edgecolor='black', linewidth=0.5)

            for bar in bars:
                ax.bar(bar.get_x() + 0.05, bar.get_height(), width=0.9, color='lightgray', alpha=0.3, zorder=1)
            
            ax.set_title(f'Rental Frequency by Brand - {category}', fontsize=16, fontproperties=font_prop, color=color)
            ax.set_xlabel('Brand (Frame Size)', fontsize=12, fontproperties=font_prop, color='#264653')
            ax.set_ylabel('Rental Frequency', fontsize=12, fontproperties=font_prop, color='#264653')
            
            ax.set_xticks(bar_positions)
            ax.set_xticklabels(brands_frame_sizes, rotation=45, ha='right', fontsize=10, color='#2d2d2d')
            
            for i, bar in enumerate(bars):
                ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 0.05, 
                        f"{int(bar.get_height())}", ha='center', color='#023047', fontsize=10, fontweight='bold')

        plt.style.use('ggplot')
        plt.tight_layout()
        plt.show()
    
def test():
    """
    Test function to verify functionality of the BicycleSelectionSystem class.
    
    This test function serves as a profile and debugger, calling key functions
    and printing results to ensure they work as expected. It also helps identify 
    any potential issues or errors in the system.
    """
    try:
        select_system = BicycleSelectionSystem()
        bike_recommendation_system = BikeRecommendationSystem()
        display_plots = display_graphs()
        user_budget = 500

        # Test: Fetch rental history recommendations
        print("Testing history recommendation function...")
        history_df = system.historyRecommendation()
        if history_df is not None:
            print("Rental history recommendations fetched successfully.")
            print(history_df.head()) 
        else:
            print("Failed to fetch rental history recommendations.")

        print("\nTesting future recommendation function...")
        future_df = system.futureRecommendation()
        if future_df is not None:
            print("Future bicycle recommendations fetched successfully.")
            print(future_df.head())     
        else:
            print("Failed to fetch future bicycle recommendations.")

        # Fetch history and future recommendations
        history_df = select_system.historyRecommendation()
        print("History Recommendations:")
        print(history_df)

        future_df = select_system.futureRecommendation()
        print("\nFuture Recommendations:")
        print(future_df)
        
        (good_recommendations, message) = bike_recommendation_system.generate_goodrecommendations()
        print("\nGood Recommendations:")
        print(good_recommendations)
        
        
        (filtered_future_recommendations,total_spent, message) = bike_recommendation_system.filter_future_recommendations(good_recommendations, user_budget)
        print(f"\nMessage: {message}")
        print(f"\nFuture Recommendations based on budget: {filtered_future_recommendations}")
        print(f"\nTotal amount of recommended bikes: {total_spent}")

        bad_recommendations, bad_message = bike_recommendation_system.generate_badrecommendations()
        print(f"\nBad Recommendations Message: {bad_message}")
        print(bad_recommendations)
        
        display_plots.plot_animated_future_recommendations(user_budget)
        display_plots.plot_score_durability_vs_rental_frequency()
        display_plots.plot_popularity_by_brand()

        
    except Exception as e:
        print(f"Error in test function: {e}")

if __name__ == "__main__":
    test()
    
