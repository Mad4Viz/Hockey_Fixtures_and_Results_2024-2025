#!/usr/bin/env python3
"""
England Hockey League Table Scraping

A Selenium-based web scraper for extracting hockey league table data from the England Hockey website.
This script handles JavaScript-rendered content and extracts standings data for the
London Women's Premier Division hockey league.

Features:
- Extracts league table data including Position, Team, Played, Won, Drawn, Lost, For, Against, GD, Points
- Processes multiple seasons (2024-2025, 2023-2024)
- Saves data as a single CSV file with all seasons
- Handles JavaScript-loaded dynamic content
- Optimised for macOS
- Optional debug mode for troubleshooting

"""

import os
import time
import argparse
import pandas as pd
import sys
from datetime import datetime
from typing import Dict, List, Optional, Union

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import logging

# Set up logging
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s',
                    handlers=[
                        logging.FileHandler("hockey_scraper.log"),
                        logging.StreamHandler()
                    ])

logger = logging.getLogger(__name__)

# Define constants for the website URLs and parameters
BASE_URL = "https://london.englandhockey.co.uk/competitions"
COMPETITION_PATH = "2024-2025-4477305-london-hockey-league-womens-4477409-london-womens-premier-division/table"

# Season parameters - ID mapping for different seasons
SEASON_PARAMS = {
    "2024-2025": "14edd6a1-2d0e-447a-8550-68b42882e46d",
    "2023-2024": "3d87a2df-f97d-47a1-8371-b8e5267c5360"
}

# Competition group IDs vary by season
COMPETITION_GROUP_PARAMS = {
    "2024-2025": "30df1a93-543a-4352-a493-72e5ae8c102d",  # Current season
    "2023-2024": "8c166342-84d4-4f76-ae04-85bb285359da"   # Previous season (from the HTML)
}

# Competition IDs vary by season
COMPETITION_PARAMS = {
    "2024-2025": "a91902a0-70f5-4edb-8f50-0eba140e972f",  # Current season
    "2023-2024": "bbd3b34a-7621-4e1d-8bf4-e10a1712241e"   # Previous season (from the HTML)
}


class HockeyLeagueTableScraper:
    """
    A class for scraping and processing hockey league table data from England Hockey website.
    
    This scraper uses Selenium to load the page and wait for JavaScript to execute,
    then extracts the table data from the rendered page.
    
    Attributes:
        save_path (str): Directory path where data will be saved
        headless (bool): Whether to run the browser in headless mode
        debug (bool): Whether to save debug information (screenshots, HTML, etc.)
        driver: The Selenium WebDriver instance
        combined_data (pd.DataFrame): DataFrame to store combined data from all seasons
    """
    
    def __init__(self, save_path: str = "hockey_league_data", headless: bool = True, debug: bool = False):
        """
        Initialize the scraper with a location to save the extracted data.
        
        Args:
            save_path (str): Directory path where data will be saved
            headless (bool): Whether to run the browser in headless mode
            debug (bool): Whether to save debug information (screenshots, HTML, etc.)
        """
        self.save_path = save_path
        self.headless = headless
        self.debug = debug
        self.combined_data = pd.DataFrame()
        
        # Create save directory if it doesn't exist
        if not os.path.exists(save_path):
            os.makedirs(save_path)
            logger.info(f"Created directory: {save_path}")
        
        # Initialize the web driver
        self.driver = self.setup_browser(headless)
        
        logger.info(f"Initialized scraper. Data will be saved to: {self.save_path}")
        if self.debug:
            logger.info("Debug mode is enabled - saving screenshots and HTML files")
    
    def setup_browser(self, headless: bool = True) -> webdriver.Chrome:
        """
        Setup a Chrome WebDriver instance.
        
        Args:
            headless (bool): Whether to run the browser in headless mode
            
        Returns:
            webdriver.Chrome: Configured WebDriver instance
        """
        options = Options()
        if headless:
            options.add_argument('--headless=new')  # Use newer headless mode
        
        # Common options for stability
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--disable-gpu')
        options.add_argument('--window-size=1920,1080')
        options.add_argument('--user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100 Safari/537.36')
        
        # Use the default Chrome installation for Mac with regular options
        return webdriver.Chrome(options=options)
    
    def close(self):
        """
        Close the WebDriver when finished.
        """
        if self.driver:
            self.driver.quit()
            logger.info("WebDriver closed")
    
    def take_screenshot(self, filename: str):
        """
        Take a screenshot if debug mode is enabled.
        
        Args:
            filename (str): Name of the screenshot file
        """
        if self.debug and self.driver:
            try:
                filepath = f"{self.save_path}/{filename}"
                self.driver.save_screenshot(filepath)
                logger.info(f"Screenshot saved to {filepath}")
            except Exception as e:
                logger.error(f"Error taking screenshot: {e}")
    
    def save_html(self, html_content: str, filename: str):
        """
        Save HTML content if debug mode is enabled.
        
        Args:
            html_content (str): HTML content to save
            filename (str): Name of the HTML file
        """
        if self.debug:
            try:
                filepath = f"{self.save_path}/{filename}"
                with open(filepath, 'w', encoding='utf-8') as f:
                    f.write(html_content)
                logger.info(f"HTML saved to {filepath}")
            except Exception as e:
                logger.error(f"Error saving HTML: {e}")
    
    def select_filter_option(self, dropdown_id: str, option_text: str, timeout: int = 20) -> bool:
        """
        Select an option from a dropdown by visible text.
        
        Args:
            dropdown_id (str): HTML ID of the dropdown element
            option_text (str): Text of the option to select
            timeout (int): Maximum wait time in seconds
            
        Returns:
            bool: True if selection was successful, False otherwise
        """
        try:
            # Wait for the dropdown to be available and get it
            dropdown_element = WebDriverWait(self.driver, timeout).until(
                EC.presence_of_element_located((By.ID, dropdown_id))
            )
            
            # Create a Select object
            dropdown_select = Select(dropdown_element)
            
            # Log available options for debugging
            options = [option.text for option in dropdown_select.options]
            logger.info(f"Options in {dropdown_id}: {options}")
            
            # Select by visible text
            dropdown_select.select_by_visible_text(option_text)
            logger.info(f"Selected '{option_text}' from {dropdown_id}")
            
            # Wait a moment for the selection to take effect
            time.sleep(1)
            
            # Verify selection
            selected_option = dropdown_select.first_selected_option.text
            logger.info(f"Currently selected option in {dropdown_id}: '{selected_option}'")
            
            return selected_option == option_text
            
        except Exception as e:
            logger.error(f"Error selecting option '{option_text}' from dropdown {dropdown_id}: {e}")
            return False
    
    def select_filter_by_value(self, dropdown_id: str, value: str, timeout: int = 20) -> bool:
        """
        Select an option from a dropdown by value.
        
        Args:
            dropdown_id (str): HTML ID of the dropdown element
            value (str): Value attribute of the option to select
            timeout (int): Maximum wait time in seconds
            
        Returns:
            bool: True if selection was successful, False otherwise
        """
        try:
            # Wait for the dropdown to be available and get it
            dropdown_element = WebDriverWait(self.driver, timeout).until(
                EC.presence_of_element_located((By.ID, dropdown_id))
            )
            
            # Create a Select object
            dropdown_select = Select(dropdown_element)
            
            # Log available options for debugging
            options = [(option.get_attribute('value'), option.text) for option in dropdown_select.options]
            logger.info(f"Options in {dropdown_id}: {options}")
            
            # Select by value
            dropdown_select.select_by_value(value)
            logger.info(f"Selected option with value '{value}' from {dropdown_id}")
            
            # Wait a moment for the selection to take effect
            time.sleep(1)
            
            # Verify selection
            selected_value = dropdown_select.first_selected_option.get_attribute('value')
            logger.info(f"Currently selected value in {dropdown_id}: '{selected_value}'")
            
            return selected_value == value
            
        except Exception as e:
            logger.error(f"Error selecting option with value '{value}' from dropdown {dropdown_id}: {e}")
            return False
    
    def apply_filters(self) -> bool:
        """
        Click the Apply button for the filters.
        
        Returns:
            bool: True if clicking succeeded, False otherwise
        """
        try:
            # Click the Apply button
            apply_button = WebDriverWait(self.driver, 20).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, ".js-competition-filters-apply"))
            )
            
            # Take screenshot before clicking apply
            self.take_screenshot("before_apply.png")
            
            # Scroll to button to ensure it's visible
            self.driver.execute_script("arguments[0].scrollIntoView(true);", apply_button)
            time.sleep(1)
            
            # Click with JavaScript (more reliable than Selenium's click)
            self.driver.execute_script("arguments[0].click();", apply_button)
            logger.info("Clicked Apply button")
            
            # Wait for the page to reload
            time.sleep(5)
            
            # Take screenshot after clicking apply
            self.take_screenshot("after_apply.png")
            
            return True
            
        except Exception as e:
            logger.error(f"Error clicking Apply button: {e}")
            return False
    
    def load_page_with_season(self, url: str, season: str, timeout: int = 30) -> str:
        """
        Load a page with Selenium and select the correct season and filters.
        
        Args:
            url (str): URL to load
            season (str): Season to select (e.g., "2023-2024")
            timeout (int): Maximum wait time in seconds
            
        Returns:
            str: HTML content of the page after JavaScript execution
        """
        logger.info(f"Loading URL for season {season}: {url}")
        
        # Get the season ID and other parameters
        season_id = SEASON_PARAMS.get(season)
        comp_group_id = COMPETITION_GROUP_PARAMS.get(season)
        comp_id = COMPETITION_PARAMS.get(season)
        
        if not season_id or not comp_group_id or not comp_id:
            logger.error(f"Missing parameters for season {season}")
            return ""
        
        # For 2023-2024, use a direct URL with all parameters
        if season == "2023-2024":
            full_url = f"{url}?season={season_id}&competition-group={comp_group_id}&competition={comp_id}"
            logger.info(f"Using direct URL for 2023-2024: {full_url}")
            self.driver.get(full_url)
        else:
            # Load the base URL for current season
            self.driver.get(url)
        
        # Wait for page to load initially
        time.sleep(5)
        
        # Take screenshot of initial page
        self.take_screenshot(f"initial_page_{season}.png")
        
        # For the 2023-2024 season, we'll use the URL parameters instead of selecting from dropdowns
        if season == "2023-2024":
            # Just wait for the table to appear
            logger.info("Using URL parameters for 2023-2024 season, waiting for table to load")
            try:
                WebDriverWait(self.driver, timeout).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, "table"))
                )
                logger.info("Table loaded for 2023-2024 season")
            except Exception as e:
                logger.warning(f"Timeout waiting for table: {e}")
                
            # Additional wait to ensure JavaScript has fully executed
            time.sleep(5)
        else:
            # For 2024-2025, use the dropdown selection
            logger.info("Selecting filters for 2024-2025 season")
            
            # Select the season from dropdown
            if self.select_filter_by_value("season", season_id):
                logger.info(f"Selected season {season}")
            else:
                logger.warning(f"Failed to select season {season}")
            
            # Select the competition group
            women_league_text = "LONDON HOCKEY LEAGUE WOMENS"
            if self.select_filter_option("competition-group", women_league_text):
                logger.info(f"Selected competition group: {women_league_text}")
            else:
                logger.warning(f"Failed to select competition group: {women_league_text}")
            
            # Select the competition
            premier_division_text = "London Women's Premier Division"
            if self.select_filter_option("competition", premier_division_text):
                logger.info(f"Selected competition: {premier_division_text}")
            else:
                logger.warning(f"Failed to select competition: {premier_division_text}")
            
            # Apply the filters
            if self.apply_filters():
                logger.info("Applied filters successfully")
            else:
                logger.warning("Failed to apply filters")
                
            # Wait for the table to load after applying filters
            try:
                WebDriverWait(self.driver, timeout).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, "table"))
                )
                logger.info("Table loaded after applying filters")
            except Exception as e:
                logger.warning(f"Timeout waiting for table after applying filters: {e}")
            
            # Additional wait to ensure JavaScript has fully executed
            time.sleep(5)
        
        # Take screenshot of final page
        self.take_screenshot(f"filtered_page_{season}.png")
        
        # Save the HTML for debugging
        html_content = self.driver.page_source
        self.save_html(html_content, f"debug_{season}.html")
        
        return html_content
    
    def extract_table_data(self, html_content: str, season: str) -> pd.DataFrame:
        """
        Extract league table data from the HTML content.
        
        Args:
            html_content (str): Raw HTML content of the page
            season (str): Season identifier (e.g., "2024-2025")
            
        Returns:
            pd.DataFrame: DataFrame containing the league table data
        """
        soup = BeautifulSoup(html_content, 'html.parser')
        
        # Find the competition title
        competition_title = soup.select_one('.c-ribbon__title')
        competition = competition_title.text.strip() if competition_title else "London Women's Premier Division"
        logger.info(f"Extracting data for: {competition} ({season})")
        
        # Find the table - looking for the table inside the c-table-container
        table_container = soup.find('div', class_='c-table-container')
        
        # If not found, try to find any table element
        if not table_container:
            logger.warning("Table container not found, trying to find any table")
            table = soup.find('table')
        else:
            table = table_container.find('table')
        
        # If still not found, return empty DataFrame
        if not table:
            logger.error("No table found in the HTML")
            return pd.DataFrame()
        
        # Extract headers
        headers = []
        header_row = table.find('thead').find('tr')
        for th in header_row.find_all('th'):
            # Try to find the desktop view text (more descriptive)
            lg_span = th.find('span', class_='u-hide u-inline-block@lg')
            if lg_span and lg_span.text.strip():
                headers.append(lg_span.text.strip())
            else:
                # Try to find the mobile view text (abbreviated)
                sm_span = th.find('span', class_='u-hide@lg')
                if sm_span and sm_span.text.strip():
                    if sm_span.text.strip() == 'P' and len(headers) < 3:
                        headers.append("Played")  # First P is for Played
                    elif sm_span.text.strip() == 'P' and len(headers) > 8:
                        headers.append("Points")  # Second P is for Points
                    else:
                        # Convert abbreviated headers to full names
                        abbr_map = {
                            'W': 'Won',
                            'D': 'Drawn',
                            'L': 'Lost',
                            'F': 'For',
                            'A': 'Against',
                            'GD': 'GD'
                        }
                        headers.append(abbr_map.get(sm_span.text.strip(), sm_span.text.strip()))
                else:
                    # If no spans found, use empty string for position
                    headers.append("Position")
        
        # Make sure we have the right headers
        expected_headers = ['Position', 'Team', 'Played', 'Won', 'Drawn', 'Lost', 'For', 'Against', 'GD', 'Points']
        
        # If we didn't get all headers correctly, use the expected ones
        if len(headers) != len(expected_headers) or not all(h in headers for h in expected_headers):
            logger.warning(f"Headers mismatch. Found: {headers}, Expected: {expected_headers}")
            headers = expected_headers
        
        # Extract rows
        rows = []
        tbody = table.find('tbody')
        if not tbody:
            logger.error("Table does not have a tbody element")
            return pd.DataFrame()
        
        for tr in tbody.find_all('tr'):
            tds = tr.find_all('td')
            
            # Skip if not enough cells
            if len(tds) < 8:  # Minimum expected: Position, Team, P, W, D, L, GD, Points
                logger.warning(f"Row has insufficient cells: {len(tds)}, skipping")
                continue
            
            row_data = []
            
            # Position
            row_data.append(tds[0].text.strip())
            
            # Team name
            team_cell = tds[1]
            team_link = team_cell.find('a')
            row_data.append(team_link.text.strip() if team_link else team_cell.text.strip())
            
            # Add the rest of the stats: Played, Won, Drawn, Lost
            for i in range(2, 6):
                row_data.append(tds[i].text.strip())
            
            # For and Against - these might be hidden on mobile
            for_cell = tds[6]
            against_cell = tds[7]
            
            # Make sure to extract the text without extra whitespace
            for_value = for_cell.text.strip()
            against_value = against_cell.text.strip()
            
            row_data.append(for_value)
            row_data.append(against_value)
            
            # GD
            gd_cell = tds[8] if len(tds) > 8 else None
            row_data.append(gd_cell.text.strip() if gd_cell else "")
            
            # Points - often in a <b> tag
            points_cell = tds[9] if len(tds) > 9 else None
            if points_cell:
                b_tag = points_cell.find('b')
                points_value = b_tag.text.strip() if b_tag else points_cell.text.strip()
                row_data.append(points_value)
            else:
                row_data.append("")
            
            # Ensure we have the right number of columns
            while len(row_data) < len(headers):
                row_data.append("")
                
            # Trim if too long
            if len(row_data) > len(headers):
                row_data = row_data[:len(headers)]
            
            rows.append(row_data)
        
        # Create DataFrame
        df = pd.DataFrame(rows, columns=headers)
        
        # Check if we have any data
        if df.empty:
            logger.warning("No data found in the table")
            return df
        
        # Add season column
        df['Season'] = season
        
        # Add competition info
        df['Competition Group'] = 'LONDON HOCKEY LEAGUE WOMENS'
        df['Competition'] = competition
        
        # Reorder columns to put season and competition first
        first_cols = ['Season', 'Competition Group', 'Competition']
        df = df[first_cols + [col for col in df.columns if col not in first_cols]]
        
        # Convert numeric columns
        numeric_cols = ['Played', 'Won', 'Drawn', 'Lost', 'For', 'Against', 'GD', 'Points']
        for col in numeric_cols:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce')
        
        logger.info(f"Successfully extracted {len(df)} rows from the table")
        return df
    
    def save_combined_data(self) -> str:
        """
        Save the combined DataFrame to a CSV file with proper formatting.
        
        Returns:
            str: The path to the saved file, or None if saving failed
        """
        if self.combined_data.empty:
            logger.warning("No data to save")
            return None
        
        try:
            # Format the date for the filename
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            
            # Create the filename with timestamp
            filename = f"london_womens_premier_all_seasons_{timestamp}.csv"
            filepath = os.path.join(self.save_path, filename)
            
            # Save the DataFrame to CSV
            self.combined_data.to_csv(filepath, index=False)
            logger.info(f"Combined data saved to {filepath}")
            return filepath
            
        except Exception as e:
            logger.error(f"Error saving data: {e}")
            return None
    
    def scrape_season(self, season_name: str) -> pd.DataFrame:
        """
        Scrape league table data for a specific season.
        
        Args:
            season_name (str): Name of the season (e.g., "2024-2025")
            
        Returns:
            pd.DataFrame: DataFrame containing league table data for the season
        """
        logger.info(f"Processing season: {season_name}")
        
        # Get season ID
        season_id = SEASON_PARAMS.get(season_name)
        if not season_id:
            logger.error(f"Unknown season: {season_name}")
            return pd.DataFrame()
        
        # Construct the URL
        url = f"{BASE_URL}/{COMPETITION_PATH}"
        
        # Load the page and select the correct season
        html_content = self.load_page_with_season(url, season_name)
        
        # Extract the table data
        df = self.extract_table_data(html_content, season_name)
        
        # Verify the data looks different from other seasons
        # (This is a sanity check to make sure we're getting different data for different seasons)
        if not df.empty and not self.combined_data.empty:
            sample_team = df.iloc[0]['Team'] if len(df) > 0 else None
            sample_points = df.iloc[0]['Points'] if len(df) > 0 else None
            logger.info(f"Sample data for {season_name}: Team={sample_team}, Points={sample_points}")
        
        # Add data to combined DataFrame
        if not df.empty:
            if self.combined_data.empty:
                self.combined_data = df.copy()
            else:
                self.combined_data = pd.concat([self.combined_data, df], ignore_index=True)
            
            # Print a preview of the data
            logger.info(f"Preview of data for {season_name}:")
            logger.info(df.head().to_string())
        
        return df
    
    def run(self, seasons: List[str] = None) -> Dict[str, pd.DataFrame]:
        """
        Run the scraper for all available seasons or a subset.
        
        Args:
            seasons (List[str], optional): List of seasons to scrape, 
                or None for all available seasons
        
        Returns:
            Dict[str, pd.DataFrame]: Dictionary mapping season names to DataFrames
        """
        results = {}
        
        logger.info("Starting the scraping process...")
        
        # Determine which seasons to scrape
        if not seasons:
            seasons_to_scrape = list(SEASON_PARAMS.keys())
        else:
            seasons_to_scrape = [s for s in seasons if s in SEASON_PARAMS]
        
        # Scrape each season
        for season_name in seasons_to_scrape:
            try:
                df = self.scrape_season(season_name)
                
                if not df.empty:
                    results[season_name] = df
                
                # Be nice to the server - add a delay between requests
                time.sleep(3)
                
            except Exception as e:
                logger.error(f"Error processing season {season_name}: {e}")
                import traceback
                logger.error(traceback.format_exc())
        
        # Save combined data
        if not self.combined_data.empty:
            self.save_combined_data()
        
        logger.info("Scraping process completed")
        return results


def main():
    """
    Main entry point for the scraper.
    
    Parses command line arguments and initializes the scraper.
    """
    parser = argparse.ArgumentParser(
        description='Scrape hockey league table data from England Hockey website using Selenium.',
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    parser.add_argument('--output', type=str, default='hockey_league_data', 
                        help='Directory to save output data')
    parser.add_argument('--no-headless', action='store_true', 
                        help='Show browser window (not headless)')
    parser.add_argument('--debug', action='store_true',
                        help='Enable debug mode (save screenshots and HTML files)')
    parser.add_argument('--season', type=str, 
                        choices=['2024-2025', '2023-2024', 'all'], 
                        default='all',
                        help='Specific season to scrape, or "all" for all seasons')
    
    args = parser.parse_args()
    
    # Handle the SSL warning
    import warnings
    warnings.filterwarnings("ignore", category=Warning)
    
    print("=" * 80)
    print("England Hockey League Table Scraping")
    print("=" * 80)
    print(f"Starting at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Output directory: {args.output}")
    print(f"Browser mode: {'Visible' if args.no_headless else 'Headless'}")
    print(f"Debug mode: {'Enabled' if args.debug else 'Disabled'}")
    print(f"Season(s) to scrape: {args.season}")
    print("-" * 80)
    
    # Initialize scraper for web scraping
    headless = not args.no_headless  # Default is headless unless --no-headless is specified
    scraper = HockeyLeagueTableScraper(args.output, headless, args.debug)
    
    try:
        # Run scraper
        start_time = time.time()
        
        if args.season == 'all':
            results = scraper.run()
            total_rows = len(scraper.combined_data)
        else:
            df = scraper.scrape_season(args.season)
            results = {args.season: df}
            total_rows = len(df)
        
        end_time = time.time()
        
        # Print summary
        print("\n" + "=" * 80)
        print(f"Scraping completed in {end_time - start_time:.2f} seconds")
        print(f"Total rows extracted: {total_rows}")
        
        for season, df in results.items():
            print(f"Season {season}: {len(df)} rows")
        
        # Make sure combined data is saved
        filepath = scraper.save_combined_data()
        if filepath:
            print(f"Combined data saved to: {filepath}")
        
        print("=" * 80)
        
    except Exception as e:
        logger.error(f"Error during scraping: {e}")
        import traceback
        logger.error(traceback.format_exc())
        sys.exit(1)
    
    finally:
        # Always close the browser, even if there's an error
        scraper.close()


if __name__ == "__main__":
    main()