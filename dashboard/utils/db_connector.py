import sqlite3
import os
import pandas as pd
from pathlib import Path

# Possible database locations to check
DB_SEARCH_PATHS = [
    Path(__file__).resolve().parent.parent.parent / "DEM_Project_MilestoneTWO" / "data" / "database" / "air_quality.db",
    Path("/Users/anubhav/Documents/DATA-ENGINEERING-PROJECT/DEM_Project_MilestoneTWO/data/database/air_quality.db"),
    Path("/Users/anubhav/Downloads/air_quality.db"),
    Path("./DEM_Project_MilestoneTWO/data/database/air_quality.db"),
]

def find_db_path() -> Path:
    """
    Search for the SQLite database path across common locations.
    Raises FileNotFoundError if database cannot be located.
    """
    for path in DB_SEARCH_PATHS:
        if path.exists():
            return path
    raise FileNotFoundError(
        "Could not automatically locate the SQLite database 'air_quality.db'. "
        "Please ensure Milestone 2 has been executed and the database exists."
    )

def get_connection() -> sqlite3.Connection:
    """
    Create and return a sqlite3 connection.
    Enables WAL journal mode for concurrent read performance.
    """
    db_path = find_db_path()
    conn = sqlite3.connect(db_path)
    # Performance pragmas
    conn.execute("PRAGMA journal_mode=WAL;")
    conn.execute("PRAGMA synchronous=OFF;")
    return conn

def validate_warehouse_tables() -> dict:
    """
    Validate that all required Star Schema tables exist in the database.
    Returns a dictionary of status indicators and row counts.
    """
    required_tables = ["dim_station", "dim_pollutant", "dim_time", "fact_measurements"]
    validation_results = {}
    
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        # Get list of existing tables
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        existing_tables = [row[0] for row in cursor.fetchall()]
        
        for table in required_tables:
            if table in existing_tables:
                cursor.execute(f"SELECT COUNT(*) FROM {table}")
                row_count = cursor.fetchone()[0]
                validation_results[table] = {
                    "exists": True,
                    "row_count": row_count,
                    "columns": [col[1] for col in cursor.execute(f"PRAGMA table_info({table});").fetchall()]
                }
            else:
                validation_results[table] = {
                    "exists": False,
                    "row_count": 0,
                    "columns": []
                }
        conn.close()
    except Exception as e:
        # Fallback if connection fails
        for table in required_tables:
            validation_results[table] = {"exists": False, "row_count": 0, "columns": [], "error": str(e)}
            
    return validation_results

def run_query(query: str, params: tuple = ()) -> pd.DataFrame:
    """
    Execute a SQL query against the database and return a Pandas DataFrame.
    """
    conn = get_connection()
    try:
        df = pd.read_sql_query(query, conn, params=params)
    finally:
        conn.close()
    return df

def inject_custom_css():
    """
    Inject custom styles into the Streamlit application page.
    """
    import streamlit as st
    css_path = Path(__file__).resolve().parent.parent / "assets" / "style.css"
    if css_path.exists():
        with open(css_path) as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

