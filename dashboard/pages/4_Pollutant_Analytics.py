import streamlit as st
import sys
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from pathlib import Path

# Add project root to path for local imports
sys.path.append(str(Path(__file__).resolve().parent.parent))

from utils.db_connector import inject_custom_css, run_query
import queries.sql_queries as qy

st.set_page_config(page_title="Pollutant Analytics - AQI Warehouse", page_icon="🧪", layout="wide")
inject_custom_css()

st.title("🧪 Pollutant Profiling & Analytics")
st.write("Understand pollutant concentrations, rankings, and data distributions across the warehouse.")

# Load Pollutant Summaries
try:
    df_summary = run_query(qy.POLLUTANT_SUMMARY)
except Exception as e:
    st.error(f"Error executing pollutant summary query: {str(e)}")
    df_summary = pd.DataFrame()

if not df_summary.empty:
    col_rank, col_desc = st.columns([1.2, 1])
    
    with col_rank:
        st.subheader("🏆 Pollutant Rankings (Average Concentrations)")
        
        # Color bar chart of averages
        fig_rank = px.bar(
            df_summary,
            x="avg_value",
            y="pollutant_name",
            orientation="h",
            color="avg_value",
            color_continuous_scale="Thermal",
            labels={"avg_value": "Avg Concentration (ug/m³)", "pollutant_name": "Pollutant Type"},
            template="plotly_dark"
        )
        fig_rank.update_layout(
            yaxis={"categoryorder": "total ascending"},
            height=380,
            margin=dict(l=20, r=20, t=20, b=20)
        )
        st.plotly_chart(fig_rank, use_container_width=True)
        
    with col_desc:
        st.subheader("📋 Descriptive Statistics")
        st.dataframe(
            df_summary,
            use_container_width=True,
            column_config={
                "pollutant_name": "Pollutant",
                "avg_value": "Average",
                "min_value": "Min",
                "max_value": "Max",
                "reading_count": "Readings Count"
            },
            hide_index=True
        )

    st.write("---")
    
    # Interactive distribution profiles
    st.subheader("📊 Pollutant Data Distribution Profiles")
    
    pollutants_list = list(df_summary["pollutant_name"].unique())
    selected_pollutant = st.selectbox(
        "Select Pollutant for Distribution Analysis",
        options=pollutants_list,
        index=pollutants_list.index("pm25") if "pm25" in pollutants_list else 0
    )
    
    # Fetch distribution values (limiting to 10,000 for responsive rendering)
    dist_query = """
    SELECT f.value, s.station_name
    FROM fact_measurements f
    JOIN dim_station s ON s.station_id = f.station_id
    JOIN dim_pollutant p ON p.pollutant_id = f.pollutant_id
    WHERE p.pollutant_name = ? AND f.value IS NOT NULL
    LIMIT 10000;
    """
    
    try:
        df_dist = run_query(dist_query, (selected_pollutant,))
    except Exception as e:
        st.error(f"Error fetching distribution data: {str(e)}")
        df_dist = pd.DataFrame()
        
    if not df_dist.empty:
        col_hist, col_box = st.columns(2)
        
        with col_hist:
            st.write(f"##### Histogram of {selected_pollutant.upper()} Concentration")
            fig_hist = px.histogram(
                df_dist,
                x="value",
                nbins=50,
                color_discrete_sequence=["#00f2fe"],
                labels={"value": "Concentration (ug/m³)"},
                template="plotly_dark"
            )
            fig_hist.update_layout(
                height=300,
                margin=dict(l=20, r=20, t=20, b=20)
            )
            st.plotly_chart(fig_hist, use_container_width=True)
            
        with col_box:
            st.write(f"##### Boxplot of {selected_pollutant.upper()} by Station")
            fig_box = px.box(
                df_dist,
                x="station_name",
                y="value",
                color="station_name",
                color_discrete_sequence=px.colors.qualitative.Vivid,
                labels={"value": "Concentration (ug/m³)", "station_name": "Station"},
                template="plotly_dark"
            )
            fig_box.update_layout(
                showlegend=False,
                xaxis={"tickangle": 45},
                height=300,
                margin=dict(l=20, r=20, t=20, b=20)
            )
            st.plotly_chart(fig_box, use_container_width=True)
    else:
        st.warning("No distribution data available for this pollutant.")
        
else:
    st.warning("No pollutant data found in the warehouse database.")

st.write("---")
st.info("💡 **Milestone Connection:** This page queries the fact table to showcase pollutant categories and metrics. Combining it with dim_station highlights how the Star Schema facilitates quick slice-and-dice aggregations.")
