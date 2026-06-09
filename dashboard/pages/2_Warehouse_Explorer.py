import streamlit as st
import sys
import pandas as pd
from pathlib import Path

# Add project root to path for local imports
sys.path.append(str(Path(__file__).resolve().parent.parent))

from utils.db_connector import inject_custom_css, validate_warehouse_tables

st.set_page_config(page_title="Warehouse Explorer - AQI Warehouse", page_icon="🏢", layout="wide")
inject_custom_css()

st.title("🏢 Relational Data Warehouse Explorer")
st.write("Milestone 2 implementation: Star Schema architecture mapping.")

# Run table validations to inspect schemas and row counts
validation_results = validate_warehouse_tables()

# Layout
col_left, col_right = st.columns([1, 1.2])

with col_left:
    st.subheader("📐 Star Schema Model Relationships")
    st.markdown(
        """
        The warehouse is modeled as a **Star Schema** centered around `fact_measurements` to support high-performance analytical queries.
        
        * **Fact Table**: Contains numeric values (pollutant concentrations) and meteorological measurements (`at_c`, `rh_percent`, etc.).
        * **Dimension Tables**: Filterable descriptive descriptors (`dim_station`, `dim_pollutant`, `dim_time`).
        """
    )
    
    # Render Mermaid diagram
    st.markdown(
        """
        ```mermaid
        erDiagram
            dim_station ||--o{ fact_measurements : "station_id"
            dim_pollutant ||--o{ fact_measurements : "pollutant_id"
            dim_time ||--o{ fact_measurements : "time_id"
            
            dim_station {
                text station_id PK
                text station_name
                text city
                text state
            }
            dim_pollutant {
                int pollutant_id PK
                text pollutant_name
            }
            dim_time {
                int time_id PK
                text dt_str
                int year
                int month
                int day
                int hour
            }
            fact_measurements {
                int measurement_id PK
                text station_id FK
                int pollutant_id FK
                int time_id FK
                real value
                real at_c
                real rh_percent
                real ws_m_s
                real wd_deg
                real rf_mm
                real tot_rf_mm
                real sr_w_mt2
                real bp_mmhg
                real vws_m_s
            }
        ```
        """,
        unsafe_allow_html=True
    )

with col_right:
    st.subheader("📋 Table Profiles & Columns")
    
    # Selection box for tables
    selected_table = st.selectbox(
        "Select Table to Inspect",
        options=["fact_measurements", "dim_station", "dim_pollutant", "dim_time"]
    )
    
    table_info = validation_results.get(selected_table, {"exists": False, "row_count": 0, "columns": []})
    
    if table_info["exists"]:
        # Show row count and column count
        col_c1, col_c2 = st.columns(2)
        with col_c1:
            st.metric(label="Total Rows", value=f"{table_info['row_count']:,}")
        with col_c2:
            st.metric(label="Total Columns", value=len(table_info['columns']))
            
        # Display schema table
        st.write("#### Schema Schema details")
        schema_df = pd.DataFrame({
            "Column Number": range(1, len(table_info["columns"]) + 1),
            "Column Name": table_info["columns"]
        })
        st.dataframe(schema_df, use_container_width=True, hide_index=True)
        
        # Display a sample of the table data
        st.write("#### Sample Data (Top 5 rows)")
        from utils.db_connector import run_query
        try:
            sample_df = run_query(f"SELECT * FROM {selected_table} LIMIT 5;")
            st.dataframe(sample_df, use_container_width=True)
        except Exception as e:
            st.error(f"Error fetching data sample: {str(e)}")
            
    else:
        st.error(f"Table '{selected_table}' was not found in the SQLite warehouse.")

st.write("---")
st.info("💡 **Milestone Connection:** Relational warehouse construction (Milestone 2) ensures data is normalized, which minimizes redundancy. The fact table references dimension foreign keys, supporting OLAP aggregation patterns.")
