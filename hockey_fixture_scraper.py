#!/usr/bin/env python3
"""
England Hockey League Data Scraper

A Selenium-based web scraper for extracting hockey match data from the England Hockey League website.
This script handles JavaScript-rendered content and extracts fixtures/results for the
London Women's Premier Division hockey league.

Features:
- Extracts both historical match data (with scores) and upcoming fixtures (with times)
- Processes multiple seasons (2024-2025, 2023-2024)
- Incrementally saves data as CSV for real-time monitoring
- Handles JavaScript-loaded dynamic content
- Specially optimized for macOS

Author: Valerie M
GitHub: https://github.com/yourusername
Date: March 2025
"""

import os
import time
import argparse
import csv
from datetime import datetime
from typing import Dict, List, Optional, Set

import pandas as pd
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# Define constants for the website URLs and parameters
BASE_URL = "https://london.englandhockey.co.uk/competitions"
COMPETITION_PATH = "2024-2025-4477305-london-hockey-league-womens-4477409-london-womens-premier-division/fixtures"
SEASON_PARAMS = {
    "2024-2025": "14edd6a1-2d0e-447a-8550-68b42882e46d",
    "2023-2024": "3d87a2df-f97d-47a1-8371-b8e5267c5360"
}

# Competition group IDs vary by season
COMPETITION_GROUP_PARAMS = {
    "2024-2025": "30df1a93-543a-4352-a493-72e5ae8c102d",  # Current season
    "2023-2024": "8c166342-84d4-4f76-ae04-85bb285359da"   # Previous season
}

# Competition IDs vary by season
COMPETITION_PARAMS = {
    "2024-2025": "a91902a0-70f5-4edb-8f50-0eba140e972f",  # Current season
    "2023-2024": "bbd3b34a-7621-4e1d-8bf4-e10a1712241e"   # Previous season
}

# For backward compatibility with existing code
COMPETITION_GROUP_PARAM = COMPETITION_GROUP_PARAMS["2024-2025"]
COMPETITION_PARAM = COMPETITION_PARAMS["2024-2025"]


class HockeyLeagueScraper:
    """
    A class for scraping and processing hockey league data from England Hockey website.
    
    This scraper uses Selenium to load the page and wait for JavaScript to execute,
    then extracts the fixture data from the rendered page. Data is saved incrementally
    to allow real-time monitoring of the scraping process.
    
    Attributes:
        save_path (str): Directory path where data will be saved
        headless (bool): Whether to run the browser in headless mode
        driver: The Selenium WebDriver instance
        csv_path (str): Path to the CSV file where data is being saved
        processed_matches (Set[str]): Set of unique match identifiers to avoid duplicates
    """
    
    def __init__(self, save_path: str = "hockey_data", headless: bool = True):
        """
        Initialize the scraper with a location to save the extracted data.
        
        Args:
            save_path (str): Directory path where data will be saved
            headless (bool): Whether to run the browser in headless mode
        """
        self.save_path = save_path
        self.headless = headless
        
        # Create save directory if it doesn't exist
        if not os.path.exists(save_path):
            os.makedirs(save_path)
        
        # Set up CSV file path with timestamp
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        self.csv_path = os.path.join(self.save_path, f'hockey_league_data_{timestamp}.csv')
        
        # Set to track processed matches (to avoid duplicates)
        self.processed_matches = set()
        
        # Write CSV header
        self._write_csv_header()
        
        # Initialize the web driver
        self.driver = self.setup_browser(headless)
        
        print(f"Initialized scraper. Data will be saved to: {self.csv_path}")
    
    def _write_csv_header(self):
        """
        Write the header row to the CSV file.
        """
        # Define the column headers
        headers = [
            'Season', 'Competition Group', 'Competition', 'Week Date', 
            'Home Team', 'Away Team', 'Home Team Score', 'Away Team Score',
            'Home Team Badge', 'Away Team Badge', 'Fixture Location', 'Time of Match'
        ]
        
        # Write the header row
        with open(self.csv_path, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(headers)
    
    def _append_to_csv(self, matches: List[Dict]):
        """
        Append match data to the CSV file.
        
        Args:
            matches (List[Dict]): List of match data dictionaries to append
        """
        if not matches:
            return
        
        # Define the column order
        columns = [
            'Season', 'Competition Group', 'Competition', 'Week Date', 
            'Home Team', 'Away Team', 'Home Team Score', 'Away Team Score',
            'Home Team Badge', 'Away Team Badge', 'Fixture Location', 'Time of Match'
        ]
        
        # Append rows to the CSV
        with open(self.csv_path, 'a', newline='', encoding='utf-8') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=columns)
            for match in matches:
                writer.writerow(match)
        
        print(f"Appended {len(matches)} matches to CSV")
    
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
            options.add_argument('--headless')
        
        # Common options for stability
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--disable-gpu')
        options.add_argument('--window-size=1920,1080')
        options.add_argument('--user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/98.0.4758.102 Safari/537.36')
        
        # Use the default Chrome installation for Mac with regular options
        return webdriver.Chrome(options=options)
    
    def close(self):
        """
        Close the WebDriver when finished.
        """
        if self.driver:
            self.driver.quit()
    
    def load_page(self, url: str, wait_selector: str = None, timeout: int = 30) -> str:
        """
        Load a page with Selenium and wait for content to be available.
        
        Args:
            url (str): URL to load
            wait_selector (str): CSS selector to wait for, or None to just wait a fixed time
            timeout (int): Maximum wait time in seconds
            
        Returns:
            str: HTML content of the page after JavaScript execution
        """
        print(f"Loading URL: {url}")
        self.driver.get(url)
        
        # Wait for page to load
        if wait_selector:
            try:
                # Wait for the element to appear
                wait = WebDriverWait(self.driver, timeout)
                wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, wait_selector)))
                
                # Wait for loader to disappear
                try:
                    loader_selector = ".c-loader"
                    wait.until(EC.invisibility_of_element_located((By.CSS_SELECTOR, loader_selector)))
                except:
                    print("Loader may not have been visible or has already disappeared")
            except Exception as e:
                print(f"Timeout waiting for element {wait_selector}: {str(e)}")
                print("Continuing with current page content...")
        else:
            # If no selector provided, just wait a fixed time
            time.sleep(10)
        
        # Additional wait to ensure JavaScript has fully executed
        time.sleep(5)
        
        return self.driver.page_source
    
    def find_selected_date(self, soup: BeautifulSoup) -> Optional[str]:
        """
        Find the selected date in the timeline/date picker.
        
        Args:
            soup (BeautifulSoup): Parsed HTML
            
        Returns:
            Optional[str]: The selected date in YYYY-MM-DD format, or None if not found
        """
        # Look for items with both is-initial-selected AND is-selected classes
        initial_selected = soup.select('.c-date-picker-timeline__item.is-initial-selected.is-selected')
        if initial_selected:
            for item in initial_selected:
                time_elem = item.select_one('time')
                if time_elem and time_elem.get('datetime'):
                    date_str = time_elem.get('datetime').split('T')[0]
                    print(f"Found initial selected date: {date_str}")
                    return date_str
        
        # Look for items with is-initial-selected class
        initial_selected = soup.select('.c-date-picker-timeline__item.is-initial-selected')
        if initial_selected:
            for item in initial_selected:
                time_elem = item.select_one('time')
                if time_elem and time_elem.get('datetime'):
                    date_str = time_elem.get('datetime').split('T')[0]
                    print(f"Found initial selected date: {date_str}")
                    return date_str
        
        # Look for buttons with is-selected class
        selected_buttons = soup.select('.c-date-picker-timeline__item-inner.is-selected')
        if selected_buttons:
            for button in selected_buttons:
                time_elem = button.select_one('time')
                if time_elem and time_elem.get('datetime'):
                    date_str = time_elem.get('datetime').split('T')[0]
                    print(f"Found selected button date: {date_str}")
                    return date_str
        
        # Look for items with is-selected class
        selected_items = soup.select('.c-date-picker-timeline__item.is-selected')
        if selected_items:
            for item in selected_items:
                time_elem = item.select_one('time')
                if time_elem and time_elem.get('datetime'):
                    date_str = time_elem.get('datetime').split('T')[0]
                    print(f"Found selected item date: {date_str}")
                    return date_str
        
        # If still not found, look for any time elements
        time_elements = soup.select('time[datetime]')
        if time_elements:
            for time_elem in time_elements:
                datetime_attr = time_elem.get('datetime')
                if datetime_attr and 'T' in datetime_attr:
                    date_str = datetime_attr.split('T')[0]
                    print(f"Found date from time element: {date_str}")
                    return date_str
        
        # If still not found, return a default date
        today = datetime.now().strftime('%Y-%m-%d')
        print(f"No date found, using today's date: {today}")
        return today
    
    def get_available_dates(self, html_content: str) -> List[Dict[str, str]]:
        """
        Extract all available match dates from the timeline in the webpage.
        
        Args:
            html_content (str): Raw HTML content of the page
            
        Returns:
            List[Dict[str, str]]: List of dictionaries with date IDs and date values
        """
        soup = BeautifulSoup(html_content, 'html.parser')
        date_items = soup.select('.c-date-picker-timeline__item')
        
        dates = []
        for item in date_items:
            button = item.select_one('.js-fixture-date')
            if button:
                date_id = button.get('id')
                time_element = button.select_one('time')
                if time_element and date_id:
                    date_text = time_element.text.strip()
                    date_value = time_element.get('datetime')
                    if date_value:
                        # Convert to YYYY-MM-DD format
                        if 'T' in date_value:
                            date_value = date_value.split('T')[0]
                        
                        dates.append({
                            'id': date_id,
                            'text': date_text,
                            'value': date_value,
                            'is_selected': 'is-selected' in item.get('class', []) or 'is-initial-selected' in item.get('class', [])
                        })
        
        # If no dates found, use fallback approach
        if not dates:
            time_elements = soup.select('time[datetime]')
            for time_elem in time_elements:
                datetime_attr = time_elem.get('datetime')
                if datetime_attr and 'T' in datetime_attr:
                    date_value = datetime_attr.split('T')[0]
                    parent = time_elem.parent
                    if parent and parent.name == 'button':
                        date_id = parent.get('id')
                        if date_id:
                            date_text = time_elem.text.strip()
                            dates.append({
                                'id': date_id,
                                'text': date_text,
                                'value': date_value,
                                'is_selected': False
                            })
        
        return dates
    
    def create_match_id(self, match_data: Dict) -> str:
        """
        Create a unique identifier for a match to avoid duplicates.
        
        Args:
            match_data (Dict): Match data dictionary
            
        Returns:
            str: Unique match identifier
        """
        # Create a unique ID using season, date, home and away teams
        season = match_data.get('Season', '')
        date = match_data.get('Week Date', '')
        home = match_data.get('Home Team', '')
        away = match_data.get('Away Team', '')
        
        return f"{season}_{date}_{home}_vs_{away}"
    
    def extract_match_data(self, html_content: str, season: str, week_date: str) -> List[Dict]:
        """
        Extract match data from the HTML content for a specific week.
        
        Args:
            html_content (str): Raw HTML content of the page
            season (str): Season identifier (e.g., "2024-2025")
            week_date (str): Date of the match week
            
        Returns:
            List[Dict]: List of dictionaries containing match data
        """
        soup = BeautifulSoup(html_content, 'html.parser')
        competition_title = soup.select_one('.c-ribbon__title')
        competition = competition_title.text.strip() if competition_title else "London Women's Premier Division"
        
        # Get all match containers
        match_containers = soup.select('.c-match-detail-card__container')
        
        # Debug information
        print(f"Found {len(match_containers)} match containers on the page")
        
        # If no matches found with the main selector, look for a different pattern
        if not match_containers:
            match_containers = soup.select('.c-fixture')
            print(f"Alternative selector found {len(match_containers)} matches")
        
        matches = []
        for container in match_containers:
            match_data = {
                'Season': season,
                'Competition Group': 'LONDON HOCKEY LEAGUE WOMENS',
                'Competition': competition,
                'Week Date': week_date
            }
            
            # Extract home team info
            home_badge = container.select_one('.c-fixture__badge-before')
            if home_badge:
                home_team = home_badge.select_one('.c-badge__label')
                match_data['Home Team'] = home_team.text.strip() if home_team else ''
                
                home_img = home_badge.select_one('.c-badge__image')
                match_data['Home Team Badge'] = home_img.get('src') if home_img else ''
            
            # Extract away team info
            away_badge = container.select_one('.c-fixture__badge-after')
            if away_badge:
                away_team = away_badge.select_one('.c-badge__label')
                match_data['Away Team'] = away_team.text.strip() if away_team else ''
                
                away_img = away_badge.select_one('.c-badge__image')
                match_data['Away Team Badge'] = away_img.get('src') if away_img else ''
            
            # Initialize score fields
            match_data['Home Team Score'] = ''
            match_data['Away Team Score'] = ''
            match_data['Time of Match'] = ''
            
            # Extract match time or score
            fixture_body = container.select_one('.c-fixture__body')
            if fixture_body:
                # First, check for the score board (found in past matches)
                score_board = fixture_body.select_one('.c-fixture__score-board')
                if score_board:
                    score_items = score_board.select('.c-score__item')
                    if len(score_items) >= 2:
                        match_data['Home Team Score'] = score_items[0].text.strip()
                        match_data['Away Team Score'] = score_items[1].text.strip()
                        match_data['Time of Match'] = 'Completed'
                
                # If no score board, try the direct score element
                elif fixture_body.select_one('.c-fixture__score'):
                    score_element = fixture_body.select_one('.c-fixture__score')
                    score_text = score_element.text.strip()
                    scores = score_text.split('-')
                    if len(scores) == 2:
                        match_data['Home Team Score'] = scores[0].strip()
                        match_data['Away Team Score'] = scores[1].strip()
                        match_data['Time of Match'] = 'Completed'
                
                # If no scores found, this is likely a future match with a time
                if not match_data['Home Team Score'] or not match_data['Away Team Score']:
                    # Look for the fixture time (future matches)
                    time_element = fixture_body.select_one('.c-fixture__time')
                    if time_element:
                        match_data['Time of Match'] = time_element.text.strip()
                        # Clear any partial scores
                        match_data['Home Team Score'] = ''
                        match_data['Away Team Score'] = ''
            else:
                # Try alternative selectors for fixture info
                fixture_info = container.select_one('.c-fixture__info')
                if fixture_info:
                    time_element = fixture_info.select_one('.c-fixture__time')
                    if time_element:
                        match_data['Time of Match'] = time_element.text.strip()
                    
                    score_element = fixture_info.select_one('.c-fixture__score')
                    if score_element:
                        score_text = score_element.text.strip()
                        scores = score_text.split('-')
                        if len(scores) == 2:
                            match_data['Home Team Score'] = scores[0].strip()
                            match_data['Away Team Score'] = scores[1].strip()
                            match_data['Time of Match'] = 'Completed'
            
            # Extract location
            location = container.select_one('.c-fixture__location')
            if location:
                location_text = location.select_one('span')
                match_data['Fixture Location'] = location_text.text.strip() if location_text else ''
            
            # Only add match if we have both home and away teams and it's not a duplicate
            if match_data['Home Team'] and match_data['Away Team']:
                match_id = self.create_match_id(match_data)
                if match_id not in self.processed_matches:
                    self.processed_matches.add(match_id)
                    matches.append(match_data)
            elif match_data['Home Team'] or match_data['Away Team']:
                print(f"Skipping incomplete match: {match_data['Home Team']} vs {match_data['Away Team']}")
        
        print(f"Extracted {len(matches)} new matches for {week_date}")
        
        # Incrementally save to CSV
        if matches:
            self._append_to_csv(matches)
        
        return matches
    
    def scrape_season(self, season_name: str, season_id: str) -> List[Dict]:
        """
        Scrape match data for a specific season.
        
        Args:
            season_name (str): Name of the season (e.g., "2024-2025")
            season_id (str): ID of the season
            
        Returns:
            List[Dict]: List of dictionaries containing match data for the season
        """
        print(f"Processing season: {season_name}")
        
        # Get the correct competition group and competition IDs for this season
        comp_group_id = COMPETITION_GROUP_PARAMS.get(season_name, COMPETITION_GROUP_PARAM)
        comp_id = COMPETITION_PARAMS.get(season_name, COMPETITION_PARAM)
        
        # Construct the URL for the season with explicit parameters
        url = f"{BASE_URL}/{COMPETITION_PATH}"
        url_with_params = f"{url}?season={season_id}&competition-group={comp_group_id}&competition={comp_id}"
        
        print(f"Using URL with parameters: {url_with_params}")
        
        # Load the initial page - don't specify a wait selector, just use fixed wait time
        html_content = self.load_page(url_with_params)
        
        # Parse the HTML
        soup = BeautifulSoup(html_content, 'html.parser')
        
        # Find the date
        week_date = self.find_selected_date(soup)
        
        # Extract the match data
        matches = self.extract_match_data(html_content, season_name, week_date)
        all_season_matches = matches.copy()
        
        # Get all available dates
        available_dates = self.get_available_dates(html_content)
        print(f"Found {len(available_dates)} dates for season {season_name}")
        
        # Keep track of processed dates to avoid duplicates
        processed_dates = [week_date]
        
        for date_info in available_dates:
            date_id = date_info['id']
            date_value = date_info['value']
            
            # Skip dates we've already processed
            if date_value in processed_dates:
                continue
            
            processed_dates.append(date_value)
            print(f"Processing date: {date_value}")
            
            # Construct URL for this date with the correct season parameters
            date_url = f"{url}?season={season_id}&competition-group={comp_group_id}&competition={comp_id}&match-day={date_id}"
            
            # Load the page for this date
            date_html = self.load_page(date_url)
            
            # Extract match data
            date_matches = self.extract_match_data(date_html, season_name, date_value)
            all_season_matches.extend(date_matches)
        
        print(f"Completed season {season_name}: Extracted {len(all_season_matches)} matches across {len(processed_dates)} dates")
        return all_season_matches
    
    def scrape_all_seasons(self) -> pd.DataFrame:
        """
        Scrape data for all available seasons and compile into a DataFrame.
        
        Returns:
            pd.DataFrame: Combined data for all seasons
        """
        all_matches = []
        
        for season_name, season_id in SEASON_PARAMS.items():
            season_matches = self.scrape_season(season_name, season_id)
            all_matches.extend(season_matches)
        
        # Convert to DataFrame
        df = pd.DataFrame(all_matches)
        
        # If we have no data, return an empty DataFrame
        if df.empty:
            print("No match data was extracted.")
            return df
        
        # Ensure all required columns are present
        required_columns = [
            'Season', 'Competition Group', 'Competition', 'Week Date', 
            'Home Team', 'Away Team', 'Home Team Score', 'Away Team Score',
            'Home Team Badge', 'Away Team Badge', 'Fixture Location', 'Time of Match'
        ]
        
        for col in required_columns:
            if col not in df.columns:
                df[col] = ''
        
        # Reorder columns to match requested format
        df = df[required_columns]
        
        print(f"Scraping complete: Extracted a total of {len(df)} unique matches")
        print(f"Final data saved to {self.csv_path}")
        
        return df


def main():
    """
    Main entry point for the scraper.
    
    Parses command line arguments and initializes the scraper.
    """
    parser = argparse.ArgumentParser(
        description='Scrape hockey league data from England Hockey website using Selenium.',
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    parser.add_argument('--output', type=str, default='hockey_data', 
                        help='Directory to save output data')
    parser.add_argument('--no-headless', action='store_true', 
                        help='Show browser window (not headless)')
    
    args = parser.parse_args()
    
    # Handle the SSL warning
    import warnings
    warnings.filterwarnings("ignore", category=Warning)
    
    print("=" * 80)
    print("England Hockey League Data Scraper")
    print("=" * 80)
    print(f"Starting at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Output directory: {args.output}")
    print(f"Browser mode: {'Visible' if args.no_headless else 'Headless'}")
    print("-" * 80)
    
    # Initialize scraper
    headless = not args.no_headless  # Default is headless unless --no-headless is specified
    scraper = HockeyLeagueScraper(args.output, headless)
    
    try:
        # Run scraper
        start_time = time.time()
        df = scraper.scrape_all_seasons()
        end_time = time.time()
        
        # Print summary
        print("\n" + "=" * 80)
        print(f"Scraping completed in {end_time - start_time:.2f} seconds")
        print(f"Total matches extracted: {len(df)}")
        print(f"Data saved to: {scraper.csv_path}")
        print("=" * 80)
        
    finally:
        # Always close the browser, even if there's an error
        scraper.close()


if __name__ == "__main__":
    main()