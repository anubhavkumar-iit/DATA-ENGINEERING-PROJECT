# Air Quality Analytics Dashboard

This dashboard is the visualization and analytics layer sitting on top of the completed Data Engineering pipeline for Delhi Air Quality monitoring. It integrates the achievements of Milestones 1, 2, and 3.

## Project Structure

```text
dashboard/
├── app.py                      # Main landing page (Pipeline Storyboard)
├── requirements.txt            # Python dependencies
├── README.md                   # Setup instructions
├── pages/                      # Multi-page application modules
│   ├── 1_Executive_Overview.py # Milestone 1-3 KPIs & overview
│   ├── 2_Warehouse_Explorer.py # Star schema metadata & details
│   ├── 3_Station_Analytics.py  # Station ranking & metrics
│   ├── 4_Pollutant_Analytics.py# Pollutant level rankings & distributions
│   ├── 5_Time_Series_Analytics.py # Hourly & daily trends
│   ├── 6_Data_Quality.py       # Before/After data quality reports
│   └── 7_SQL_Showcase.py       # Live SQL queries & benchmarks
├── utils/
│   └── db_connector.py         # DB connection & validation utility
└── queries/
    └── sql_queries.py          # Centralized OLAP SQL queries
```

## Setup and Run Instructions

### Prerequisites
* Python 3.8 or above
* Pip package manager

### 1. Install Dependencies
Run the following command in your terminal to install required libraries:
```bash
pip install -r requirements.txt
```

### 2. Run the Dashboard
Execute the following command to start the Streamlit local development server:
```bash
streamlit run app.py
```
This will launch the application and automatically open a tab in your default browser (usually at `http://localhost:8501`).
