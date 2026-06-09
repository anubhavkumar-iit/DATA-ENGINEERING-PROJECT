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

st.set_page_config(page_title="Time-Series Trends - AQI Warehouse", page_icon="📈", layout="wide")
inject_custom_css()

st.title("📈 Temporal Trends & Time-Series Analytics")
st.write("Understand temporal variations using dim_time and Spark batch calculations.")

# Sidebar Filters
st.sidebar.header("🔍 Time Filters")

# Fetch pollutants list
try:
    pollutants_df = run_query(qy.GET_ALL_POLLUTANTS)
    pollutant_list = list(pollutants_df["pollutant_name"].unique())
except Exception as e:
    pollutant_list = ["pm25", "pm10", "no2", "so2", "co", "ozone"]

selected_pollutant = st.sidebar.selectbox(
    "Select Pollutant for Trends",
    options=pollutant_list,
    index=pollutant_list.index("pm25") if "pm25" in pollutant_list else 0
)

# Load database daily/hourly trends (January 2024)
try:
    df_daily = run_query(qy.TIME_DAILY_TREND, (selected_pollutant,))
    df_hourly = run_query(qy.TIME_HOURLY_TREND, (selected_pollutant,))
except Exception as e:
    st.error(f"Error executing time-series query: {str(e)}")
    df_daily = pd.DataFrame()
    df_hourly = pd.DataFrame()

# Layout
tabs = st.tabs(["🕒 Local Warehouse Trends (Jan 2024)", "⚡ Spark Batch Pipeline Trends (2024-2025)"])

with tabs[0]:
    st.subheader(f"January 2024 Temporal Behavior for {selected_pollutant.upper()}")
    
    if not df_daily.empty and not df_hourly.empty:
        col_daily, col_hourly = st.columns(2)
        
        with col_daily:
            st.write("##### Daily Trend & Moving Average")
            
            # Interactive moving average slider
            window = st.slider("Select Moving Average Window (Days)", min_value=1, max_value=7, value=3)
            
            # Compute moving average in Pandas
            df_daily["Moving Average"] = df_daily["avg_value"].rolling(window=window, min_periods=1).mean()
            
            fig_daily = go.Figure()
            fig_daily.add_trace(go.Scatter(
                x=df_daily["day"], 
                y=df_daily["avg_value"],
                mode='lines+markers',
                name='Daily Avg',
                line=dict(color='#4facfe', width=2)
            ))
            fig_daily.add_trace(go.Scatter(
                x=df_daily["day"], 
                y=df_daily["Moving Average"],
                mode='lines',
                name=f'{window}-Day MA',
                line=dict(color='#ff9966', width=3, dash='dash')
            ))
            fig_daily.update_layout(
                xaxis_title="Day of Month (January 2024)",
                yaxis_title="Concentration (ug/m³)",
                template="plotly_dark",
                legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
                height=300,
                margin=dict(l=20, r=20, t=40, b=20)
            )
            st.plotly_chart(fig_daily, use_container_width=True)
            
        with col_hourly:
            st.write("##### Hourly Diurnal Cycle")
            
            fig_hourly = px.line(
                df_hourly,
                x="hour",
                y="avg_value",
                markers=True,
                color_discrete_sequence=["#00f2fe"],
                labels={"avg_value": "Avg Concentration (ug/m³)", "hour": "Hour of Day"},
                template="plotly_dark"
            )
            fig_hourly.update_layout(
                xaxis=dict(tickmode='linear', tick0=0, dtick=2),
                height=300,
                margin=dict(l=20, r=20, t=40, b=20)
            )
            st.plotly_chart(fig_hourly, use_container_width=True)
            
        st.write("---")
        
        # AQI Category Distribution (Jan 2024)
        col_aqi, col_season = st.columns(2)
        
        with col_aqi:
            st.write("##### PM2.5 AQI Category Breakdown")
            try:
                df_aqi = run_query(qy.TIME_AQI_DISTRIBUTION)
                
                # Sort categories for consistency
                cat_order = {"Good": 0, "Moderate": 1, "Poor": 2, "Severe": 3}
                df_aqi["order"] = df_aqi["aqi_category"].map(cat_order)
                df_aqi = df_aqi.sort_values("order").drop(columns=["order"])
                
                fig_aqi = px.pie(
                    df_aqi,
                    values="count",
                    names="aqi_category",
                    hole=0.4,
                    color="aqi_category",
                    color_discrete_map={
                        "Good": "#38ef7d",
                        "Moderate": "#f1c40f",
                        "Poor": "#ff9966",
                        "Severe": "#ff5e62"
                    },
                    template="plotly_dark"
                )
                fig_aqi.update_layout(
                    height=250,
                    margin=dict(l=20, r=20, t=20, b=20)
                )
                st.plotly_chart(fig_aqi, use_container_width=True)
            except Exception as e:
                st.error(f"Error displaying AQI distribution: {str(e)}")
                
        with col_season:
            st.write("##### Feature Engineered Season Analysis")
            st.markdown(
                """
                In Milestone 3, seasons were calculated based on observation month:
                * **Winter**: December, January, February (Month 12, 1, 2)
                * **Summer**: March, April, May (Month 3, 4, 5)
                * **Monsoon**: June, July, August, September (Month 6, 7, 8, 9)
                * **Post-Monsoon**: October, November (Month 10, 11)
                
                Because the local SQLite warehouse database covers **January 2024**, 100% of the active database entries fall under the **Winter** category.
                """
            )
            st.info("❄️ All active records in the local database are categorized as **Winter**.")
            
    else:
        st.warning("No time-series data found in the warehouse.")

with tabs[1]:
    st.subheader("⚡ Long-term Monthly Averages (Spark Pipeline Output)")
    st.markdown(
        """
        The following dataset represents the monthly average values of the **entire 8.8 million records** processed and computed in PySpark during the Milestone 3 batch transformation process.
        This provides context on temporal trends across years 2024 and 2025.
        """
    )
    
    # Pre-calculated Spark monthly trends from notebook cell 31
    spark_trends = [
        {"Year": 2024, "Month": 1, "Avg_Value": 75.46, "Label": "Jan 24"},
        {"Year": 2024, "Month": 2, "Avg_Value": 49.70, "Label": "Feb 24"},
        {"Year": 2024, "Month": 3, "Avg_Value": 40.85, "Label": "Mar 24"},
        {"Year": 2024, "Month": 4, "Avg_Value": 42.62, "Label": "Apr 24"},
        {"Year": 2024, "Month": 5, "Avg_Value": 49.64, "Label": "May 24"},
        {"Year": 2024, "Month": 6, "Avg_Value": 38.11, "Label": "Jun 24"},
        {"Year": 2024, "Month": 7, "Avg_Value": 23.85, "Label": "Jul 24"},
        {"Year": 2024, "Month": 8, "Avg_Value": 19.01, "Label": "Aug 24"},
        {"Year": 2024, "Month": 9, "Avg_Value": 24.58, "Label": "Sep 24"},
        {"Year": 2024, "Month": 10, "Avg_Value": 52.41, "Label": "Oct 24"},
        {"Year": 2024, "Month": 11, "Avg_Value": 87.40, "Label": "Nov 24"},
        {"Year": 2024, "Month": 12, "Avg_Value": 68.37, "Label": "Dec 24"},
        {"Year": 2025, "Month": 1, "Avg_Value": 65.39, "Label": "Jan 25"},
        {"Year": 2025, "Month": 2, "Avg_Value": 50.90, "Label": "Feb 25"},
        {"Year": 2025, "Month": 3, "Avg_Value": 42.39, "Label": "Mar 25"},
        {"Year": 2025, "Month": 4, "Avg_Value": 51.19, "Label": "Apr 25"},
        {"Year": 2025, "Month": 5, "Avg_Value": 40.10, "Label": "May 25"},
        {"Year": 2025, "Month": 6, "Avg_Value": 33.44, "Label": "Jun 25"},
        {"Year": 2025, "Month": 7, "Avg_Value": 22.05, "Label": "Jul 25"},
        {"Year": 2025, "Month": 8, "Avg_Value": 23.36, "Label": "Aug 25"},
        {"Year": 2025, "Month": 9, "Avg_Value": 26.52, "Label": "Sep 25"},
        {"Year": 2025, "Month": 10, "Avg_Value": 54.57, "Label": "Oct 25"},
        {"Year": 2025, "Month": 11, "Avg_Value": 88.28, "Label": "Nov 25"},
        {"Year": 2025, "Month": 12, "Avg_Value": 87.48, "Label": "Dec 25"},
    ]
    df_spark_trends = pd.DataFrame(spark_trends)
    
    # Plotly Trend line
    fig_spark = px.line(
        df_spark_trends,
        x="Label",
        y="Avg_Value",
        markers=True,
        color_discrete_sequence=["#38ef7d"],
        labels={"Avg_Value": "Average Pollutant Concentration (ug/m³)", "Label": "Time Month"},
        template="plotly_dark"
    )
    fig_spark.update_layout(
        height=350,
        margin=dict(l=20, r=20, t=20, b=20)
    )
    st.plotly_chart(fig_spark, use_container_width=True)
    
    # Analysis summary
    st.markdown(
        """
        **Insights from Spark Monthly Trends:**
        1. **High Seasonality**: Cleaned concentrations peak dramatically during the winter months (November, December, January) matching values near **88 ug/m³**.
        2. **Monsoon Washout**: Concentrations hit yearly minimums during July and August (~19-22 ug/m³), reflecting the monsoon washout effect.
        """
    )

st.write("---")
st.info("💡 **Milestone Connection:** This page combines time-series parameters from dim_time (Milestone 2) with moving averages and season feature-engineering (Milestone 3). Full trends demonstrate Spark capabilities on the full 8.8M dataset.")
