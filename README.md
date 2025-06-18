# ⚾ MLB Statistics Dashboard

An interactive web dashboard for exploring Major League Baseball statistics and events from 2015 to 2025. Built using Dash and Plotly, this app allows users to visualize top hitters, team totals, and detailed event data filtered by year and team.

## Live Demo

🔗 [View the Live Dashboard on Render](https://mlb-history-capstone-project.onrender.com)

---

## 📸 Screenshot

![Dashboard Screenshot](c:\Users\kelly\OneDrive\Pictures\Screenshots\dashboard_screenshot.png)

---
## Features

- **Top 2 Home Run Hitters by Year** 
    Dynamic bar chart showing the top players for any selected year.

- **Team Home Run Totals (2015–2025)**  
  Grouped bar chart comparing total home runs per team over time.

- **Event Detail Table**  
  Filtered by year and team(s), this scrollable table shows detailed game events.

- **Team & Year Filters**  
  Interactive dropdowns allow users to explore stats by year and team(s).

- Clean table views for long event descriptions

---

## Technologies Used

- Python
- Dash (Plotly)
- Pandas
- SQLite
- Plotly Express
- HTML/CSS (via Dash components)

---

## Setup Instructions

### 1. Clone the repository

git clone https://github.com/Kgonlez/MLB-History-Capstone-Project.git
cd mlb-capstone-project

### 2. Set up virtual environment

python -m venv venv
source venv/Scripts/activate (#On Windows)

### 3. Install Dependencies 

pip install -r requirements.txt

### 4. Run the Dashboard Locally

python scripts/dashboard.py
Then open your browser to http://127.0.0.1:8050