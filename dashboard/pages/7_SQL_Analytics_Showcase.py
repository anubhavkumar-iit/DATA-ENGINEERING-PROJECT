import streamlit as st
import sys
import time
import pandas as pd
import plotly.express as px
from pathlib import Path

# Add project root to path for local imports
sys.path.append(str(Path(__file__).resolve().parent.parent))

from utils.db_connector import inject_custom_css, run_query, get_connection
import queries.sql_queries as qy

st.set_page_config(page_title="SQL Showcase - AQI Warehouse", page_icon="💻", layout="wide")
inject_custom_css()

st.title("💻 SQL Analytics Showcase")
st.write("Demonstrate warehouse query capabilities and execute pre-built OLAP SQL queries live.")

# Dictionary of showcase queries
queries_dict = {
    "Query 1: Average PM2.5 by Station": {
        "sql": qy.SHOWCASE_QUERY_1,
        "desc": "Compare PM2.5 metrics across monitoring stations in the relational model. Demonstrates aggregates over joins.",
        "chart_type": "bar",
        "chart_config": {
            "x": "avg_pm25",
            "y": "station_name",
            "orientation": "h",
            "color": "avg_pm25",
            "title": "Ranked Average PM2.5 Concentrations",
            "scale": "Viridis"
        }
    },
    "Query 2: Hourly Average Temperature per Station": {
        "sql": qy.SHOWCASE_QUERY_2,
        "desc": "Aggregates temperature records by hour of day and station to verify meteorological variations.",
        "chart_type": "line",
        "chart_config": {
            "x": "hour",
            "y": "avg_temp_c",
            "color": "station_name",
            "title": "Hourly Average Temperature Diurnal Cycle"
        }
    },
    "Query 3: Pollutant Counts (Data Completeness)": {
        "sql": qy.SHOWCASE_QUERY_3,
        "desc": "Returns total readings and null values per pollutant type, measuring database completeness.",
        "chart_type": "bar_group",
        "chart_config": {
            "x": "pollutant_name",
            "y": "null_percentage",
            "title": "Null Percentages by Pollutant Type"
        }
    }
}

# Select box for queries
selected_key = st.selectbox("Select SQL Query to Execute", options=list(queries_dict.keys()))
selected_info = queries_dict[selected_key]

st.markdown(f"**Description:** {selected_info['desc']}")

# Show raw SQL query code block
st.code(selected_info["sql"], language="sql")

# Execution button
if st.button("⚡ Run Query Live"):
    with st.spinner("Executing query against SQLite warehouse..."):
        start_time = time.time()
        try:
            # Execute query and benchmark
            df_result = run_query(selected_info["sql"])
            exec_time = time.time() - start_time
            
            # KPI callout for query benchmark
            col_time, col_rows = st.columns(2)
            with col_time:
                st.metric(label="Execution Time", value=f"{exec_time:.4f} seconds")
            with col_rows:
                st.metric(label="Rows Returned", value=len(df_result))
                
            st.write("### Query Results")
            st.dataframe(df_result, use_container_width=True)
            
            # Interactive visualization depending on config
            st.write("### Interactive Visualizations")
            cfg = selected_info["chart_config"]
            
            if selected_info["chart_type"] == "bar":
                fig = px.bar(
                    df_result,
                    x=cfg["x"],
                    y=cfg["y"],
                    orientation=cfg.get("orientation", "v"),
                    color=cfg.get("color"),
                    color_continuous_scale=cfg.get("scale"),
                    template="plotly_dark",
                    title=cfg["title"]
                )
                fig.update_layout(yaxis={"categoryorder": "total ascending"} if cfg.get("orientation") == "h" else {})
                st.plotly_chart(fig, use_container_width=True)
                
            elif selected_info["chart_type"] == "line":
                fig = px.line(
                    df_result,
                    x=cfg["x"],
                    y=cfg["y"],
                    color=cfg.get("color"),
                    markers=True,
                    template="plotly_dark",
                    title=cfg["title"]
                )
                st.plotly_chart(fig, use_container_width=True)
                
            elif selected_info["chart_type"] == "bar_group":
                fig = px.bar(
                    df_result,
                    x=cfg["x"],
                    y=cfg["y"],
                    color=cfg["x"],
                    color_discrete_sequence=px.colors.qualitative.Pastel,
                    template="plotly_dark",
                    title=cfg["title"]
                )
                st.plotly_chart(fig, use_container_width=True)
                
        except Exception as e:
            st.error(f"Failed to execute query: {str(e)}")

st.write("---")
st.info("💡 **Milestone Connection:** This page executes pre-defined analytical SQL queries directly on the SQLite database (Milestone 2), demonstrating the query speed and efficiency of the Star Schema design.")
