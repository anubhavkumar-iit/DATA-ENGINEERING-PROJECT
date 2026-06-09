"""
Page 8 — Regional Air Quality Analytics
=========================================
Reads directly from the partitioned Parquet storage (Milestone 1 output) covering
all 24 months (Jan 2024 – Dec 2025).  Applies the same median-imputation and
feature-engineering (AQI category, season) that Milestone 3 implemented in Spark,
then presents a fully interactive regional breakdown across 6 Delhi regions.

Milestone connections:
  Milestone 1  ─ reads partitioned Parquet (year/month directories)
  Milestone 3  ─ re-applies imputation + feature engineering on-the-fly
  Milestone 2  ─ station metadata kept consistent with dim_station schema
"""

import streamlit as st
import sys
import os
import glob
import time
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent.parent))
from utils.db_connector import inject_custom_css

st.set_page_config(
    page_title="Regional Analytics – AQI Dashboard",
    page_icon="🗺️",
    layout="wide",
)
inject_custom_css()

# ─── Constants ────────────────────────────────────────────────────────────────
BASE_DIR = Path(__file__).resolve().parent.parent

PARQUET_BASE = (
    BASE_DIR
    / "data"
    / "partitioned_data"
)

STATION_REGION = {
    "site_105":  "North Delhi",
    "site_1427": "West Delhi",
    "site_1428": "South-East Delhi",
    "site_107":  "Central Delhi",
    "site_109":  "Central Delhi",
    "site_1429": "South Delhi",
    "site_115":  "South-West Delhi",
    "site_1431": "East Delhi",
    "site_122":  "Central Delhi",
    "site_1563": "Central Delhi",
    "site_124":  "South Delhi",
    "site_5395": "Central Delhi",
    "site_125":  "West Delhi",
    "site_1424": "Central Delhi",
    "site_1425": "Central Delhi",
}

REGION_COLOUR = {
    "North Delhi":      "#4facfe",
    "Central Delhi":    "#f857a6",
    "South Delhi":      "#38ef7d",
    "East Delhi":       "#ff9966",
    "West Delhi":       "#a78bfa",
    "South-East Delhi": "#fbbf24",
    "South-West Delhi": "#34d399",
}

MEDIANS = {   # From Milestone 3 (computed on full 8.8M dataset)
    "at_c":       27.1,
    "rh_percent": 65.0,
    "ws_m_s":      0.6,
    "wd_deg":    189.0,
    "tot_rf_mm":   0.0,
    "sr_w_mt2":   17.0,
    "bp_mmhg":   983.0,
}

MONTH_NAMES = {
    1:"January",2:"February",3:"March",4:"April",5:"May",6:"June",
    7:"July",8:"August",9:"September",10:"October",11:"November",12:"December",
}

SEASONS = {
    1:"Winter",2:"Winter",3:"Summer",4:"Summer",5:"Summer",
    6:"Monsoon",7:"Monsoon",8:"Monsoon",9:"Monsoon",
    10:"Post-Monsoon",11:"Post-Monsoon",12:"Winter",
}

# ─── Data helpers ─────────────────────────────────────────────────────────────
@st.cache_data(ttl=600, show_spinner="Loading parquet partition …")
def load_month(year: int, month: int) -> pd.DataFrame:
    """Load one month's parquet partition and apply Milestone-3 cleaning."""
    path = PARQUET_BASE / f"year={year}" / f"month={month}"
    files = [f for f in glob.glob(str(path / "*.parquet")) if not f.endswith(".crc")]
    if not files:
        return pd.DataFrame()

    df = pd.concat([pd.read_parquet(f) for f in files], ignore_index=True)

    # ── Milestone 3: median imputation ────────────────────────────────────────
    for col, med in MEDIANS.items():
        if col in df.columns:
            df[col] = df[col].fillna(med)
    if "rf_mm" in df.columns:
        df["rf_mm"] = df["rf_mm"].fillna(0)

    # ── Milestone 3: feature engineering ─────────────────────────────────────
    df["aqi_category"] = pd.cut(
        df["value"],
        bins=[-np.inf, 50, 100, 200, np.inf],
        labels=["Good", "Moderate", "Poor", "Severe"],
    )
    df["season"] = df["month"].map(SEASONS) if "month" in df.columns else SEASONS[month]
    df["year"]  = year
    df["month"] = month

    # ── Map station → region ─────────────────────────────────────────────────
    df["region"] = df["station_id"].map(STATION_REGION).fillna("Other")

    return df


def available_periods() -> list[tuple[int,int]]:
    """Return sorted (year, month) tuples that exist in the partition store."""
    periods = []
    for y in (2024, 2025):
        for m in range(1, 13):
            p = PARQUET_BASE / f"year={y}" / f"month={m}"
            if p.exists():
                periods.append((y, m))
    return sorted(periods)


# ─── Header ──────────────────────────────────────────────────────────────────
st.markdown(
    """
    <div class="hero-container" style="padding:28px 36px;">
        <div class="hero-title" style="font-size:2.2rem;">🗺️ Regional Air Quality Analytics</div>
        <div class="hero-subtitle">
            Reads directly from partitioned Parquet storage (Milestone 1) with Milestone-3
            cleaning applied on-the-fly. Pick any month to explore Delhi's 6 monitoring regions.
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

# ─── Sidebar controls ─────────────────────────────────────────────────────────
st.sidebar.header("⚙️ Controls")

periods = available_periods()
if not periods:
    st.error("Could not find partitioned Parquet data. Check the ingestion layer path.")
    st.stop()

# Year / Month pickers
years  = sorted({p[0] for p in periods})
sel_year  = st.sidebar.selectbox("Year", years, index=0)
months_avail = sorted({p[1] for p in periods if p[0] == sel_year})
sel_month = st.sidebar.selectbox(
    "Month",
    months_avail,
    format_func=lambda m: MONTH_NAMES[m],
    index=0,
)

# Pollutant picker
all_pollutants = [
    "pm25","pm10","no2","no","so2","co","ozone",
    "nh3","benzene","toluene","xylene","mp_xylene","eth_benzene",
]
sel_pollutant = st.sidebar.selectbox("Pollutant", all_pollutants, index=0)

# Metric selector
metric_options = {
    "Avg Concentration (ug/m³)": "value",
    "Avg Temperature (°C)":      "at_c",
    "Avg Humidity (%)":          "rh_percent",
    "Avg Wind Speed (m/s)":      "ws_m_s",
    "Avg Solar Radiation (W/m²)":"sr_w_mt2",
    "Avg Barometric Press.(mmHg)":"bp_mmhg",
}
sel_metric_label = st.sidebar.selectbox("Regional Metric", list(metric_options.keys()))
sel_metric = metric_options[sel_metric_label]

# ─── Load data ────────────────────────────────────────────────────────────────
t0  = time.time()
df  = load_month(sel_year, sel_month)
load_time = time.time() - t0

if df.empty:
    st.error(f"No data found for {MONTH_NAMES[sel_month]} {sel_year}.")
    st.stop()

df_pol = df[df["pollutant"] == sel_pollutant].copy()

# ─── Top KPI strip ────────────────────────────────────────────────────────────
total_rows   = len(df)
n_stations   = df["station_id"].nunique()
n_regions    = df["region"].nunique()
overall_avg  = round(df_pol["value"].mean(), 2) if not df_pol.empty else 0
worst_region = (
    df_pol.groupby("region")["value"].mean().idxmax() if not df_pol.empty else "N/A"
)

k1, k2, k3, k4, k5, k6 = st.columns(6)
for col, val, label in [
    (k1, f"{total_rows:,}", "Records Loaded"),
    (k2, f"{n_stations}", "Monitoring Stations"),
    (k3, f"{n_regions}", "Regions"),
    (k4, SEASONS[sel_month], "Season"),
    (k5, f"{overall_avg}", f"Avg {sel_pollutant.upper()}"),
    (k6, worst_region, "Most Polluted Region"),
]:
    col.markdown(
        f'<div class="kpi-card"><div class="kpi-value" style="font-size:1.6rem;">{val}</div>'
        f'<div class="kpi-label">{label}</div></div>',
        unsafe_allow_html=True,
    )

st.caption(f"⚡ Data loaded in {load_time:.2f}s from {MONTH_NAMES[sel_month]} {sel_year} partition.")

st.write("---")

# ─── ROW 1: Ranked bar + Daily trend ─────────────────────────────────────────
col_bar, col_line = st.columns([1, 1.6])

with col_bar:
    st.subheader(f"📊 {sel_metric_label} by Region")
    if sel_metric == "value":
        agg_df = df_pol.groupby("region")[sel_metric].mean().reset_index()
    else:
        agg_df = df.groupby("region")[sel_metric].mean().reset_index()

    agg_df = agg_df.sort_values(sel_metric, ascending=True)
    agg_df["color"] = agg_df["region"].map(REGION_COLOUR)

    fig_bar = go.Figure(go.Bar(
        x=agg_df[sel_metric],
        y=agg_df["region"],
        orientation="h",
        marker_color=agg_df["color"],
        text=agg_df[sel_metric].round(2),
        textposition="outside",
    ))
    fig_bar.update_layout(
        template="plotly_dark",
        height=320,
        margin=dict(l=10, r=30, t=10, b=10),
        xaxis_title=sel_metric_label,
    )
    st.plotly_chart(fig_bar, use_container_width=True)

with col_line:
    st.subheader(f"📅 Daily {sel_pollutant.upper()} Trend by Region")
    daily = (
        df_pol.groupby(["region", "day"])["value"]
        .mean()
        .reset_index()
        .rename(columns={"value": "avg"})
    )
    fig_trend = px.line(
        daily, x="day", y="avg", color="region",
        color_discrete_map=REGION_COLOUR,
        labels={"avg": "Avg Concentration (ug/m³)", "day": "Day of Month"},
        template="plotly_dark",
        markers=False,
    )
    fig_trend.update_layout(
        height=320,
        margin=dict(l=10, r=10, t=10, b=10),
        legend=dict(orientation="h", y=-0.25),
    )
    st.plotly_chart(fig_trend, use_container_width=True)

st.write("---")

# ─── ROW 2: AQI donut + Hourly heatmap ───────────────────────────────────────
col_donut, col_heat = st.columns([1, 1.6])

with col_donut:
    st.subheader("🍩 AQI Category Mix by Region")
    sel_region_donut = st.selectbox("Select Region", sorted(STATION_REGION.values(), key=str), key="donut_region")
    aqi_counts = (
        df_pol[df_pol["region"] == sel_region_donut]["aqi_category"]
        .value_counts()
        .reset_index()
        .rename(columns={"index": "aqi_category", "count": "count", "aqi_category": "category"})
    )
    # Handle both pandas versions
    if "category" not in aqi_counts.columns:
        aqi_counts.columns = ["category", "count"]
    fig_donut = px.pie(
        aqi_counts, values="count", names="category", hole=0.45,
        color="category",
        color_discrete_map={
            "Good": "#38ef7d", "Moderate": "#fbbf24",
            "Poor": "#ff9966", "Severe": "#ff5e62",
        },
        template="plotly_dark",
    )
    fig_donut.update_layout(
        height=300,
        margin=dict(l=10, r=10, t=10, b=10),
        showlegend=True,
        legend=dict(orientation="h", y=-0.1),
    )
    st.plotly_chart(fig_donut, use_container_width=True)

with col_heat:
    st.subheader(f"🕐 Hour-of-Day vs Region Heatmap ({sel_pollutant.upper()})")
    heat_df = (
        df_pol.groupby(["region", "hour"])["value"]
        .mean()
        .reset_index()
        .pivot(index="region", columns="hour", values="value")
    )
    fig_heat = px.imshow(
        heat_df,
        color_continuous_scale="Plasma",
        aspect="auto",
        labels={"color": "Avg Concentration", "x": "Hour of Day", "y": "Region"},
        template="plotly_dark",
    )
    fig_heat.update_layout(
        height=310,
        margin=dict(l=10, r=10, t=10, b=10),
        coloraxis_colorbar=dict(thickness=12, len=0.8),
    )
    st.plotly_chart(fig_heat, use_container_width=True)

st.write("---")

# ─── ROW 3: Pollutant radar + Station drilldown ───────────────────────────────
col_radar, col_drill = st.columns([1, 1.4])

with col_radar:
    st.subheader("🕸️ Regional Pollution Radar")
    radar_pollutants = ["pm25", "pm10", "no2", "so2", "ozone", "nh3"]
    radar_data = []
    for pol in radar_pollutants:
        sub = df[df["pollutant"] == pol].groupby("region")["value"].mean()
        radar_data.append(sub.rename(pol))
    radar_df = pd.concat(radar_data, axis=1).fillna(0)

    # Normalise 0-1 per pollutant for shape clarity
    radar_norm = radar_df.div(radar_df.max(axis=0).replace(0, 1))

    fig_radar = go.Figure()
    for region in radar_norm.index:
        vals = list(radar_norm.loc[region]) + [radar_norm.loc[region, radar_pollutants[0]]]
        cats = radar_pollutants + [radar_pollutants[0]]
        fig_radar.add_trace(go.Scatterpolar(
            r=vals, theta=cats,
            fill="toself", opacity=0.55,
            name=region,
            line_color=REGION_COLOUR.get(region, "#ffffff"),
        ))
    fig_radar.update_layout(
        polar=dict(radialaxis=dict(visible=True, range=[0, 1])),
        template="plotly_dark",
        height=360,
        margin=dict(l=30, r=30, t=10, b=10),
        legend=dict(orientation="h", y=-0.1),
        showlegend=True,
    )
    st.plotly_chart(fig_radar, use_container_width=True)

with col_drill:
    st.subheader("📡 Station-level Drilldown")
    sel_region_drill = st.selectbox("Select Region", sorted(set(STATION_REGION.values())), key="drill_region")
    station_df = (
        df_pol[df_pol["region"] == sel_region_drill]
        .groupby("station_name")
        .agg(
            avg_val=("value", "mean"),
            avg_temp=("at_c", "mean"),
            avg_hum=("rh_percent", "mean"),
            avg_wind=("ws_m_s", "mean"),
            readings=("value", "count"),
        )
        .reset_index()
        .sort_values("avg_val", ascending=False)
        .round(2)
    )
    station_df.columns = ["Station", f"Avg {sel_pollutant.upper()}", "Avg Temp (°C)", "Humidity (%)", "Wind (m/s)", "Readings"]
    st.dataframe(station_df, use_container_width=True, hide_index=True)

    # Mini bar
    fig_mini = px.bar(
        station_df, x=f"Avg {sel_pollutant.upper()}", y="Station",
        orientation="h",
        color=f"Avg {sel_pollutant.upper()}",
        color_continuous_scale="Reds",
        template="plotly_dark",
    )
    fig_mini.update_layout(height=200, margin=dict(l=10, r=10, t=10, b=10), showlegend=False)
    st.plotly_chart(fig_mini, use_container_width=True)

st.write("---")

# ─── ROW 4: Met conditions scatter + AQI severity table ──────────────────────
col_scatter, col_sev = st.columns([1.4, 1])

with col_scatter:
    st.subheader(f"🌡️ Temperature vs {sel_pollutant.upper()} (by Region)")
    scatter_df = (
        df_pol[df_pol["at_c"].notna() & df_pol["value"].notna()]
        .groupby(["station_name", "region"])
        .agg(avg_temp=("at_c", "mean"), avg_val=("value", "mean"), avg_hum=("rh_percent", "mean"))
        .reset_index()
    )
    fig_sc = px.scatter(
        scatter_df,
        x="avg_temp", y="avg_val",
        color="region",
        size="avg_hum",
        color_discrete_map=REGION_COLOUR,
        hover_name="station_name",
        labels={"avg_temp": "Avg Temperature (°C)", "avg_val": f"Avg {sel_pollutant.upper()} (ug/m³)", "avg_hum": "Humidity (%)"},
        template="plotly_dark",
    )
    fig_sc.update_layout(
        height=320,
        margin=dict(l=10, r=10, t=10, b=10),
        legend=dict(orientation="h", y=-0.25),
    )
    st.plotly_chart(fig_sc, use_container_width=True)

with col_sev:
    st.subheader("⚠️ AQI Severity Breakdown by Region")
    sev_df = (
        df_pol.groupby(["region", "aqi_category"])
        .size()
        .reset_index(name="count")
    )
    sev_pct = sev_df.copy()
    totals = sev_pct.groupby("region")["count"].transform("sum")
    sev_pct["pct"] = (sev_pct["count"] / totals * 100).round(1)

    fig_sev = px.bar(
        sev_pct, x="pct", y="region", color="aqi_category",
        orientation="h", barmode="stack",
        color_discrete_map={
            "Good": "#38ef7d", "Moderate": "#fbbf24",
            "Poor": "#ff9966", "Severe": "#ff5e62",
        },
        labels={"pct": "% of Readings", "region": "Region"},
        template="plotly_dark",
    )
    fig_sev.update_layout(
        height=320,
        margin=dict(l=10, r=10, t=10, b=10),
        legend_title="AQI",
        legend=dict(orientation="h", y=-0.25),
    )
    st.plotly_chart(fig_sev, use_container_width=True)

st.write("---")
st.info(
    "💡 **Pipeline Application:** Data read directly from **Milestone 1** partitioned Parquet "
    f"(`year={sel_year}/month={sel_month}/`). **Milestone 3** imputation & feature engineering "
    "applied on-the-fly. Region groupings sit on top of the **Milestone 2** station dimension model."
)
