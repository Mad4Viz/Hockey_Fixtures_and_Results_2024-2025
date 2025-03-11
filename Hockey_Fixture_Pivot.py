#!/usr/bin/env python3
"""
Hockey Fixtures Data Processor

This script takes the original hockey fixtures data, pivots it to create one row per team per match,
and then cleans up the data structure by removing redundant columns and adding a result column.

"""

import os
import pandas as pd
import logging
from datetime import datetime

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

# ============================================================
# SET YOUR FILE PATHS HERE
# ============================================================
# Replace these paths with your actual file locations
INPUT_FILE_PATH = ""
OUTPUT_FILE_PATH = ""
# ============================================================

def read_csv_file(file_path):
    """Read a CSV file into a pandas DataFrame."""
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"File not found: {file_path}")
    
    try:
        df = pd.read_csv(file_path)
        logging.info(f"Successfully read {len(df)} rows from {file_path}")
        return df
    except Exception as e:
        logging.error(f"Error reading file {file_path}: {str(e)}")
        raise

def pivot_and_clean_data(fixtures_df):
    """
    Pivot the fixtures data to create one row per team per match,
    and clean up by removing redundant columns and adding a result column.
    
    Args:
        fixtures_df: DataFrame containing the original fixtures data
        
    Returns:
        Cleaned and pivoted DataFrame
    """
    original_row_count = len(fixtures_df)
    logging.info(f"Original data has {original_row_count} rows and {len(fixtures_df.columns)} columns")
    
    # Make a copy to avoid modifying the original DataFrame
    df = fixtures_df.copy()
    
    # Create a list to hold the restructured data
    restructured_data = []
    
    # Process each row in the original DataFrame
    for _, row in df.iterrows():
        # Create home team row
        home_row = row.copy()
        home_row['Team_Role'] = 'Home'
        home_row['Team'] = row['Home Team']
        home_row['Opponent'] = row['Away Team']
        home_row['Team_Score'] = row['Home Team Score']
        home_row['Opponent_Score'] = row['Away Team Score']
        
        # Create away team row
        away_row = row.copy()
        away_row['Team_Role'] = 'Away'
        away_row['Team'] = row['Away Team']
        away_row['Opponent'] = row['Home Team']
        away_row['Team_Score'] = row['Away Team Score']
        away_row['Opponent_Score'] = row['Home Team Score']
        
        # Add both rows to our restructured data
        restructured_data.append(home_row)
        restructured_data.append(away_row)
    
    # Create a new DataFrame with the restructured data
    pivoted_df = pd.DataFrame(restructured_data)
    
    # Verify the row count (should be double the original)
    expected_row_count = original_row_count * 2
    actual_row_count = len(pivoted_df)
    
    if actual_row_count != expected_row_count:
        logging.warning(f"Expected {expected_row_count} rows but got {actual_row_count}")
    else:
        logging.info(f"Successfully pivoted data: {actual_row_count} rows (2 rows per match)")
    
    # List of columns to remove (now redundant after pivoting)
    columns_to_remove = [
        'Home Team', 
        'Away Team', 
        'Home Team Score', 
        'Away Team Score', 
        'Home Team Badge', 
        'Away Team Badge'
    ]
    
    # Check if these columns exist in the DataFrame
    existing_columns = [col for col in columns_to_remove if col in pivoted_df.columns]
    
    # Remove the columns
    if existing_columns:
        cleaned_df = pivoted_df.drop(columns=existing_columns)
        logging.info(f"Removed columns: {', '.join(existing_columns)}")
    else:
        logging.warning("None of the specified columns were found in the DataFrame")
        cleaned_df = pivoted_df
    
    # Add a new column for match result
    def determine_result(row):
        team_score = row.get('Team_Score')
        opponent_score = row.get('Opponent_Score')
        
        # Handle missing or non-numeric scores
        if pd.isna(team_score) or pd.isna(opponent_score):
            return 'Upcoming'  # Match hasn't been played yet
        
        try:
            team_score = float(team_score)
            opponent_score = float(opponent_score)
            
            if team_score > opponent_score:
                return 'Win'
            elif team_score < opponent_score:
                return 'Loss'
            else:
                return 'Draw'
        except (ValueError, TypeError):
            # Could be a non-numeric value (like forfeit, etc.)
            return 'Unknown'
    
    # Apply the function to create the Result column
    cleaned_df['Result'] = cleaned_df.apply(determine_result, axis=1)
    logging.info("Added 'Result' column with Win/Loss/Draw values")
    
    # Count the different result types
    result_counts = cleaned_df['Result'].value_counts()
    for result, count in result_counts.items():
        logging.info(f"  {result}: {count} matches")
    
    return cleaned_df

def main():
    """Main function to run the script."""
    print("=" * 80)
    print("Hockey Fixtures Data Processor")
    print("=" * 80)
    print(f"Input file: {INPUT_FILE_PATH}")
    print(f"Output file: {OUTPUT_FILE_PATH}")
    print(f"Processing started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    try:
        # Read the input CSV file
        fixtures_df = read_csv_file(INPUT_FILE_PATH)
        
        # Display basic information about the input data
        print("\nInput Data Summary:")
        print(f"Number of rows: {len(fixtures_df)}")
        print(f"Number of columns: {len(fixtures_df.columns)}")
        print(f"Columns: {', '.join(fixtures_df.columns.tolist())}")
        
        # Process the data (pivot and clean)
        processed_df = pivot_and_clean_data(fixtures_df)
        
        # Save the processed data
        processed_df.to_csv(OUTPUT_FILE_PATH, index=False)
        
        # Display summary
        print("\nProcessing Complete:")
        print(f"Input rows: {len(fixtures_df)}")
        print(f"Output rows: {len(processed_df)}")
        print(f"Expansion factor: {len(processed_df) / len(fixtures_df):.2f}x")
        print(f"Original columns: {len(fixtures_df.columns)}")
        print(f"New columns: {len(processed_df.columns)}")
        print(f"Added 'Result' column with Win/Loss/Draw values")
        
        # Show result counts
        result_counts = processed_df['Result'].value_counts()
        for result, count in result_counts.items():
            print(f"  {result}: {count} matches")
        
        print(f"\nOutput file saved to: {OUTPUT_FILE_PATH}")
        print(f"Processing finished at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
    except Exception as e:
        logging.error(f"Error: {str(e)}")
        print(f"\nERROR: {str(e)}")
        return
    
    print("\nProcess completed successfully!")

if __name__ == "__main__":
    main()