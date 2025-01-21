# FPL Academy

A comprehensive web-based tool designed for Fantasy Premier League (FPL) managers to visualize and analyze Premier League statistics effectively. Built with Flask, HTML, CSS for the frontend, Python and MongoDB for the backend, and hosted on Vercel.

---

## Features

### User Interface
- **Login and Registration**: User authentication system to access the dashboard.
- **Dashboard**: Centralized location for various tools and visualizations.
  - **Injury Updates**: Generate tweets summarizing daily injuries in the Premier League.
  - **Price Change**: Generate tweets summarizing daily player price changes.
  - **Attack Stats**: Analyze attacking statistics of Premier League teams.
  - **Defence Stats**: Analyze defensive statistics of Premier League teams.
  - **Team Card (Attack + Defence)**: View and compare a team's attack and defense stats.
  - **Team Matches (Attack + Defence)**: Explore team statistics on a game-week basis.
  - **Team Comparison (Attack + Defence)**: Compare attack and defense statistics of two teams.

### Data Handling
- **Data Sources**: Scraped data from Fantasy Premier League and SofaScore, merged into a unified MongoDB database.
- **Automated Tweet Generation**: Simplified tweet creation with copy functionality for daily updates.

### Technologies
- **Frontend**: Flask, HTML, CSS.
- **Backend**: Python, MongoDB.
- **Hosting**: Vercel.

---

## Data Structure

### Teams Fixtures
- Season
- Gameweek (GW)
- Home Team
- Away Team
- Goals Home
- Goals Away
- xG Home
- xG Away
- Shots Home
- Shots Away
- Shots in Box Home (SiB)
- Shots in Box Away (SiB)
- Shots on Target Home (SoT)
- Shots on Target Away (SoT)
- Big Chances Home (BC)
- Big Chances Away (BC)

### Player Stats
- Season
- Gameweek Number
- Player Full Name
- Team
- Opponent Team
- Home/Away Indicator
- Minutes Played
- Goals Scored
- Expected Goals (xG)
- Assists
- Expected Assists (xA)
- Own Goals
- Total Shots
- Big Chances
- Chances Created
- Big Chances Created
- Shots on Target
- Hit Woodwork
- Total Crosses
- Player Web Name
- Player ID
- Position
- Total Points
- Kickoff Time

---

## How to Use

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/fpl-academy.git
   ```

2. Navigate to the project directory:
   ```bash
   cd fpl-academy
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Run the application:
   ```bash
   python app.py
   ```

5. Access the application in your browser at `http://localhost:5000`.

---

## Contributions

Contributions are welcome! Feel free to submit issues or pull requests to improve the project.

---

