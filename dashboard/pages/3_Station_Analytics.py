import streamlit as st
import sys
import pandas as pd
import plotly.express as px
from pathlib import Path

# Add project root to path for local imports
sys.path.append(str(Path(__file__).resolve().parent.parent))

from utils.db_connector import inject_custom_css, run_query
import queries.sql_queries as qy

st.set_page_config(page_title="Station Analytics - AQI Warehouse", page_icon="📡", layout="wide")
inject_custom_css()

st.title("📡 Station Air Quality Analytics")
st.write("Compare measurements across monitoring stations using optimized warehouse joins.")

# Fetch filter lists from DB
try:
    pollutants_df = run_query(qy.GET_ALL_POLLUTANTS)
    pollutant_list = list(pollutants_df["pollutant_name"].unique())
except Exception as e:
    pollutant_list = ["pm25", "pm10", "no2", "so2", "co", "ozone"]

# Filtering Sidebar
st.sidebar.header("🔍 Filters")
selected_pollutant = st.sidebar.selectbox(
    "Select Pollutant",
    options=pollutant_list,
    index=pollutant_list.index("pm25") if "pm25" in pollutant_list else 0
)

# Load data based on selected pollutant
try:
    df_station_pollutant = run_query(qy.STATION_AVERAGE_POLLUTANT, (selected_pollutant,))
except Exception as e:
    st.error(f"Error executing station query: {str(e)}")
    df_station_pollutant = pd.DataFrame()

if not df_station_pollutant.empty:
    # KPI Callouts
    top_polluted = df_station_pollutant.iloc[0]
    least_polluted = df_station_pollutant.iloc[-1]
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric(
            label="Most Polluted Station", 
            value=top_polluted["station_name"].split(",")[0],
            delta=f"{top_polluted['avg_value']} avg"
        )
    with col2:
        st.metric(
            label="Least Polluted Station", 
            value=least_polluted["station_name"].split(",")[0],
            delta=f"{least_polluted['avg_value']} avg",
            delta_color="inverse"
        )
    with col3:
        overall_avg = round(df_station_pollutant["avg_value"].mean(), 2)
        st.metric(
            label=f"Overall {selected_pollutant.upper()} Avg", 
            value=f"{overall_avg} ug/m³"
        )

    st.write("---")
    
    # Visualizations
    col_plot, col_tbl = st.columns([1.5, 1])
    
    with col_plot:
        st.subheader(f"Ranked Station Averages ({selected_pollutant.upper()})")
        # Color palettes curated and harmonic (avoid basic red/green)
        fig = px.bar(
            df_station_pollutant,
            x="avg_value",
            y="station_name",
            orientation="h",
            color="avg_value",
            color_continuous_scale="Viridis",
            labels={"avg_value": "Average Concentration", "station_name": "Monitoring Station"},
            template="plotly_dark"
        )
        fig.update_layout(
            yaxis={"categoryorder": "total ascending"},
            height=400,
            margin=dict(l=20, r=20, t=20, b=20)
        )
        st.plotly_chart(fig, use_container_width=True)
        
    with col_tbl:
        st.subheader("Data Summary Table")
        st.dataframe(
            df_station_pollutant[["station_name", "avg_value", "min_value", "max_value", "reading_count"]],
            use_container_width=True,
            column_config={
                "station_name": "Station",
                "avg_value": "Avg",
                "min_value": "Min",
                "max_value": "Max",
                "reading_count": "Readings Count"
            },
            hide_index=True
        )

    st.write("---")
    
    # Station Multi-Comparison
    st.subheader("📡 Multiple Stations Comparison")
    
    # Multi-select stations
    stations_list = list(df_station_pollutant["station_name"].unique())
    selected_stations = st.multiselect(
        "Select Stations to Compare",
        options=stations_list,
        default=stations_list[:3]
    )
    
    if selected_stations:
        # Load comparison values for all pollutants
        try:
            df_compare = run_query(qy.STATION_COMPARISON_ALL_POLLUTANTS)
            df_compare_filtered = df_compare[df_compare["station_name"].isin(selected_stations)]
            
            # Filter to major pollutants for clarity
            df_compare_filtered = df_compare_filtered[
                df_compare_filtered["pollutant_name"].isin(["pm25", "pm10", "no2", "so2", "ozone", "nh3"])
            ]
            
            fig_compare = px.bar(
                df_compare_filtered,
                x="pollutant_name",
                y="avg_value",
                color="station_name",
                barmode="group",
                color_discrete_sequence=px.colors.qualitative.Pastel,
                labels={"avg_value": "Average Concentration", "pollutant_name": "Pollutant Type"},
                template="plotly_dark"
            )
            fig_compare.update_layout(
                height=350,
                margin=dict(l=20, r=20, t=20, b=20)
            )
            st.plotly_chart(fig_compare, use_container_width=True)
            
        except Exception as e:
            st.error(f"Error generating comparison charts: {str(e)}")
    else:
        st.warning("Please select at least one station for comparison.")

else:
    st.warning("No station data found in the warehouse database.")

st.write("---")
st.info("💡 **Milestone Connection:** Relational joins between fact_measurements, dim_station, and dim_pollutant tables implement Milestone 2 query design. Station filters allow real-time analytical slicing.")
