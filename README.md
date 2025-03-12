# Hockey League Dashboard Project
  
  
  ### Before and After Comparison
  
  
  ### [England Hockey Website (Original)](https://london.englandhockey.co.uk/competitions/2024-2025-4477305-london-hockey-league-womens-4477409-london-womens-premier-division/fixtures?match-day=2025-03-08&season=14edd6a1-2d0e-447a-8550-68b42882e46d&competition-group=30df1a93-543a-4352-a493-72e5ae8c102d&competition=a91902a0-70f5-4edb-8f50-0eba140e972f)

  <img src="https://github.com/user-attachments/assets/ca89845f-450b-4b28-8cad-be646eacd845" width="400" alt="Screenshot">
    <img src="https://github.com/user-attachments/assets/12821653-ae99-4c8a-a5ec-0e390d83e8c7" width="400" alt="Screenshot">

  ### [Tableau Dashboard](https://public.tableau.com/app/profile/valerie.madojemu/viz/HamsteadWestminsterResultsandFixtures/FixturesResults)
  
  <img src="https://github.com/user-attachments/assets/43f4cfa9-853e-4ca6-ace5-06994e30d2ab" width="400" alt="Screenshot">
    <img src="https://github.com/user-attachments/assets/4ec8dc7f-ba29-4f12-b6d4-17139408fc06" width="400" alt="Screenshot">

  ## Summary
  
  This project delivers an interactive dashboard that reimagines the England Hockey fixture list for the London Women's Premier League Division, with design elements inspired by Hampstead & Westminster Hockey Club. The solution transforms traditional match-centric data into a comprehensive team-focused analytics platform through a three-stage process: web scraping, data transformation, and visualisation.
  
  The dashboard was specifically designed to answer critical pre-match questions for players, coaches and supporters:
  
  - What is our current league position?
  - How is our recent form, along with that of upcoming opponents?
  - Did we win against this opponent earlier in the season?
  - What is our historical record against each team?
  
  By addressing these questions through an intuitive interface, the project provides valuable match intelligence and performance tracking.
  
  ## Project Background
  
  ### Problem Statement
  
  Sports fixtures data typically follows a match-centric structure with one row per game, listing home and away teams with their respective scores. While this format efficiently represents match information, it creates significant challenges for team-focused analysis, especially when trying to:
  
  1. View a team's complete fixture list (home and away games)
  2. Analyse performance patterns across multiple seasons
  3. Compare head-to-head records against specific opponents
  4. Create visualisations that filter by team regardless of home/away status
  
  The England Hockey website presents additional challenges, as data is loaded dynamically via JavaScript, making it inaccessible to traditional web scraping methods. Furthermore, the standard presentation lacks comprehensive historical analysis and team-specific filtering options.
  
  ### Data Structure Challenge
  
  The fundamental challenge lies in the original data structure:
  
  **Original Fixtures Format:**
  
  ```
  | Week Date  | Home Team   | Away Team   | Home Score | Away Score |
  |------------|-------------|-------------|------------|------------|
  | 21/09/2024 | Barnes W2   | Wimbledon W3| 2          | 1          |
  | 05/10/2024 | Wimbledon W3| Barnes W2   | 0          | 3          |
  
  ```
  
  When trying to link this data with team standings:
  
  **Team Standings:**
  
  ```
  | Team        | Played | Won | Drawn | Lost | Points |
  |-------------|--------|-----|-------|------|--------|
  | Barnes W2   | 10     | 7   | 1     | 2    | 22     |
  | Wimbledon W3| 10     | 5   | 2     | 3    | 17     |
  
  ```
  
  The problem becomes evident: creating relationships between these tables in Tableau would either show only home matches or only away matches for a team, not their complete fixture list. This results in an incomplete performance picture.
  
  ## Technical Solution
  
  To overcome these challenges, I developed a three-component system:
  
  ### 1. Data Acquisition - Web Scraping
  
  The first challenge was extracting data from the England Hockey website, where content is loaded dynamically via JavaScript. I created two Python scripts:
  
  - **[hockey_fixture_scraper.py](https://github.com/Mad4Viz/Hockey_Fixtures_and_Results_2024-2025/blob/main/hockey_fixture_scraper.py)**: Extracts fixtures and results data
  - **[hockey_league_scraper.py](https://github.com/Mad4Viz/Hockey_Fixtures_and_Results_2024-2025/blob/main/hockey_league_scraper.py)**: Extracts league standings data
  
  These scripts use Selenium to automate browser interactions, allowing them to:
  
  - Navigate the England Hockey website
  - Wait for JavaScript-rendered content to load
  - Extract fixtures, results, and standings data
  - Process multiple seasons (2023-2024, 2024-2025)
  - Handle dynamic date selection and page navigation
  - Save the extracted data as structured CSV files
  
  ### 2. Data Transformation - Pivoting
  
  After acquiring the raw data, I created **[Hockey_Fixture_Pivot.py](https://github.com/Mad4Viz/Hockey_Fixtures_and_Results_2024-2025/blob/main/Hockey_Fixture_Pivot.py)** to transform the match-centric data into a team-centric format. This script:
  
  - Takes the original fixtures data (1 row per match)
  - Creates two rows per match (one from each team's perspective)
  - Adds contextual information (Team_Role, Result)
  - Removes redundant columns
  - Calculates Win/Loss/Draw results automatically
  
  The transformation creates a flexible structure where each row represents a team's participation in a match, rather than the match itself.
  
  **Transformed Data Format:**
  
  ```
  | Week Date  | Team Role | Team        | Opponent    | Team Score | Opponent Score | Result |
  |------------|-----------|-------------|-------------|------------|----------------|--------|
  | 21/09/2024 | Home      | Barnes W2   | Wimbledon W3| 2          | 1              | Win    |
  | 21/09/2024 | Away      | Wimbledon W3| Barnes W2   | 1          | 2              | Loss   |
  
  ```
  
  This pivoted structure enables team-focused analysis regardless of whether a team played at home or away.
  
  ### [3. Data Visualisation - Tableau Dashboard](https://public.tableau.com/app/profile/valerie.madojemu/viz/HamsteadWestminsterResultsandFixtures/FixturesResults)
  
  The final component is a Tableau dashboard that leverages the transformed data structure to provide comprehensive team analysis. The dashboard includes:
  
  - Current league standings with key statistics
  - Recent form indicators with match results
  - Upcoming fixtures with venue information
  - Historical head-to-head comparisons
  - Performance trends across seasons
  
  The visualisation allows users to filter by team and provides immediate insights into past performance and upcoming fixtures.
  
  ## Implementation Process
  
  ### Web Scraping Implementation
  
  The web scraping component presented several technical challenges:
  
  1. **Dynamic Content**: The England Hockey website loads fixture data via JavaScript after the initial page load, requiring Selenium to interact with the DOM.
  2. **Date Navigation**: To capture all fixtures, the scripts needed to iterate through multiple date selections on the calendar interface.
  3. **Season Parameters**: Different seasons use different URL parameters and competition IDs, requiring season-specific handling.
  4. **Browser Compatibility**: Special considerations were needed for macOS compatibility.
  
  The implementation includes robust error handling, logging, and validation to ensure data integrity. Each page is systematically processed with appropriate wait times to avoid overwhelming the server.
  
  ```python
  # Example from hockey_fixture_scraper.py showing date navigation
  def scrape_season(self, season_name: str, season_id: str) -> List[Dict]:
      """
      Scrape match data for a specific season.
      """
      print(f"Processing season: {season_name}")
  
      # Get the correct competition parameters for this season
      comp_group_id = COMPETITION_GROUP_PARAMS.get(season_name, COMPETITION_GROUP_PARAM)
      comp_id = COMPETITION_PARAMS.get(season_name, COMPETITION_PARAM)
  
      # Construct the URL with parameters
      url = f"{BASE_URL}/{COMPETITION_PATH}"
      url_with_params = f"{url}?season={season_id}&competition-group={comp_group_id}&competition={comp_id}"
  
      # Load the initial page
      html_content = self.load_page(url_with_params)
  
      # Find the current date and extract match data
      week_date = self.find_selected_date(BeautifulSoup(html_content, 'html.parser'))
      matches = self.extract_match_data(html_content, season_name, week_date)
  
      # Process additional dates
      available_dates = self.get_available_dates(html_content)
      processed_dates = [week_date]
  
      for date_info in available_dates:
          if date_info['value'] not in processed_dates:
              processed_dates.append(date_info['value'])
              date_url = f"{url}?season={season_id}&competition-group={comp_group_id}&competition={comp_id}&match-day={date_info['id']}"
              date_html = self.load_page(date_url)
              date_matches = self.extract_match_data(date_html, season_name, date_info['value'])
              matches.extend(date_matches)
  
      return matches
  
  ```
  
  ### Data Pivoting Methodology
  
  The pivoting process transforms each match into two team-perspective records. This approach:
  
  1. **Doubles the row count**: Creating separate entries for home and away teams
  2. **Normalises team references**: All teams appear in a single "Team" column
  3. **Contextualises scores**: Relabels scores as "Team_Score" and "Opponent_Score"
  4. **Adds Result classification**: Automatically determines Win/Loss/Draw outcomes
  
  ```python
  # Example from Hockey_Fixture_Pivot.py showing the pivoting logic
  def pivot_and_clean_data(fixtures_df):
      """
      Pivot the fixtures data to create one row per team per match
      """
      df = fixtures_df.copy()
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
  
          # Add both rows to restructured data
          restructured_data.append(home_row)
          restructured_data.append(away_row)
  
      # Create new DataFrame and add Result column
      pivoted_df = pd.DataFrame(restructured_data)
      pivoted_df['Result'] = pivoted_df.apply(determine_result, axis=1)
  
      return pivoted_df
  
  ```
  
  ### [Dashboard Design Process](https://public.tableau.com/app/profile/valerie.madojemu/viz/HamsteadWestminsterResultsandFixtures/FixturesResults)
  
  The Tableau dashboard was designed with both functionality and aesthetics in mind. The design process included:
  
  1. **User Research**: Identifying key questions users need answered before matches
  2. **Visual Hierarchy**: Organising information from most to least urgent
  3. **Team-Centric Approach**: Making all visualisations filterable by team
  4. **Club Branding**: Incorporating Hampstead & Westminster Hockey Club design elements
  
  The final design presents a comprehensive match intelligence platform that allows quick access to key performance indicators and historical results.
  
  ## Results & Deliverables
  
  ### Data Architecture
  
  The project produced three key data assets:
  
  1. **League_Fixtures_and_Results.csv**: Raw match data (264 rows × 12 columns)
  2. **Clean_Pivot_Fixtures.csv**: Transformed team-centric data (528 rows × 12 columns)
  3. **Tableau_Standings.csv**: League standings data (24 rows × 13 columns)
  
  The transformed data structure enables powerful relationship capabilities in Tableau, allowing for comprehensive team-focused analysis that wasn't possible with the original data format.
  
  ### Dashboard Functionality
  
  The [Tableau dashboards](https://public.tableau.com/app/profile/valerie.madojemu/viz/HamsteadWestminsterResultsandFixtures/FixturesResults) delivers an intuitive interface with several connected views:
  
  1. **Team Summary Section**:
      - Current league position
      - Points, goals for/against, and goal difference
      - Comparison to previous season
  2. **League Table Section**:
      - Complete standings with all teams
      - Win/draw/loss record and points
      - Interactive filtering capabilities
  3. **Recent Form Section**:
      - Last 5 matches with results indicated
      - Performance trends and patterns
  4. **Upcoming Fixtures Section**:
      - Next scheduled matches
      - Venue and timing information
      - Previous result against upcoming opponent
  5. **Head-to-Head Section**:
      - Historical record against each opponent
      - Win percentage calculation
  
  ### Key Insights
  
  The dashboard enables users to quickly derive key insights such as:
  
  - Hampstead & Westminster Ladies 3s currently sit in 7th position with 28 points
  - The team has scored 29 goals, ranking 10th in league, which is interesting to highlight as Old Cranleighans who are sitting further down the table have scored 31, ranking higher at 7th.
  - The team has conceded 36 goals ranking 6th in the league. With 2nd in the league Southgate only conceding 14 goals more than 50% less.
  
  These insights provide valuable pre-match intelligence for players, coaches, and keen supporters.
  
  ## Technical Details
  
  ### Tools and Technologies
  
  The project leveraged several technologies:
  
  - **Python 3.8+**: Core programming language
  - **Selenium**: Browser automation for JavaScript-rendered content
  - **BeautifulSoup4**: HTML parsing and navigation
  - **Pandas**: Data manipulation and transformation
  - **Tableau**: Data visualisation and dashboard creation
  - **GitHub**: Version control and code management
  
  ### Challenges and Solutions
  
  Several technical challenges were addressed during the project:
  
  1. **JavaScript-Rendered Content**:
      - **Challenge**: The England Hockey website loads fixtures dynamically after page load
      - **Solution**: Implemented Selenium with appropriate wait conditions to ensure content was fully loaded before extraction
  2. **Data Structure Transformation**:
      - **Challenge**: Converting match-centric data to team-centric format
      - **Solution**: Developed a custom pivoting algorithm that creates two perspectives of each match
  3. **Season Parameter Differences**:
      - **Challenge**: Different seasons use different URL parameters and competition IDs
      - **Solution**: Created season-specific parameter mappings and handling logic
  4. **Dashboard Filtering**:
      - **Challenge**: Enabling intuitive team filtering across all visualisations
      - **Solution**: Implemented relationship-based data connections in Tableau
  
  ## Conclusion & Future Work
  
  ### Summary of Achievements
  
  This project successfully transformed traditionally structured sports fixture data into a team-focused analytics platform through a combination of web scraping, data transformation, and interactive visualisation. The resulting dashboard provides valuable pre-match intelligence and performance tracking for the London Women's Premier Hockey League Division.
  
  The solution demonstrates how restructuring data can fundamentally change analysis capabilities, particularly in sports analytics where traditional match-centric data structures limit team-focused insights.
  
  ### Potential Enhancements
  
  Several enhancements could further extend the value of this project:
  
  1. **Automated Updates**: Implementing scheduled runs of the scraping scripts to keep data current
  2. **Additional Leagues**: Expanding coverage to other divisions and competitions
  3. **Player Statistics**: Incorporating individual player data when available
  4. **Predictive Elements**: Adding win probability predictions for upcoming matches
  5. **Mobile App**: Developing a dedicated mobile application for on-the-go access
  
  ### Lessons Learned
  
  Key takeaways from this project include:
  
  1. **Data Structure Matters**: How data is structured fundamentally impacts what questions can be effectively answered
  2. **Web Scraping Complexity**: Modern websites with JavaScript-rendered content require sophisticated scraping approaches
  3. **User-Focused Design**: Starting with key user questions leads to more valuable analytics solutions
  4. **Cross-Tool Integration**: The power of combining multiple technologies (Python, Selenium, Tableau) to create comprehensive solutions
  
  This project demonstrates how technical expertise in data acquisition, transformation, and visualisation can be combined to create practical solutions that enhance sports analytics and decision-making.
  
  ---
  
  *Note: This project was developed for educational and analytical purposes. All data has been ethically sourced from publicly available information.*
