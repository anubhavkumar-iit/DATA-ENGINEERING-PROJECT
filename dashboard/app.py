import streamlit as st
import sys
import os
from pathlib import Path

# Add project root to path for local imports
sys.path.append(str(Path(__file__).resolve().parent))

from utils.db_connector import inject_custom_css, validate_warehouse_tables, find_db_path

st.set_page_config(
    page_title="Delhi Air Quality Data Warehouse Dashboard",
    page_icon="🌬️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Inject CSS styling
inject_custom_css()

# Hero Section
st.markdown(
    """
    <div class="hero-container">
        <div class="hero-title">🌬️ Delhi Air Quality Analytics & Data Warehouse</div>
        <div class="hero-subtitle">
            An end-to-end Data Engineering pipeline, Star Schema relational warehouse, and analytics engine built to monitor and analyze hourly air quality index measurements across 15 monitoring stations.
        </div>
    </div>
    """,
    unsafe_allow_html=True
)

st.write("---")

# Pipeline Flowchart section
st.subheader("🛠️ Data Engineering Pipeline & Architecture")
st.markdown(
    """
    This dashboard represents the visualization and consumption layer of a multi-stage Data Engineering pipeline.
    Hover over navigation pages on the sidebar to explore different elements of the system.
    
    <div class="pipeline-flow">
        <div class="pipeline-step">
            📁 Raw Data<br><span style="font-size:0.75rem; font-weight:normal; color:#a0aec0;">Parquet (8.8M rows)</span>
        </div>
        <div class="pipeline-arrow">➔</div>
        <div class="pipeline-step">
            ⚡ Spark Ingestion<br><span style="font-size:0.75rem; font-weight:normal; color:#a0aec0;">Partition & Deduplicate</span>
        </div>
        <div class="pipeline-arrow">➔</div>
        <div class="pipeline-step">
            💾 Partitioned Parquet<br><span style="font-size:0.75rem; font-weight:normal; color:#a0aec0;">192 Files (Year/Month)</span>
        </div>
        <div class="pipeline-arrow">➔</div>
        <div class="pipeline-step">
            🧹 Batch Cleaning<br><span style="font-size:0.75rem; font-weight:normal; color:#a0aec0;">Median Imputation</span>
        </div>
        <div class="pipeline-arrow">➔</div>
        <div class="pipeline-step">
            ⚙️ Feature Eng.<br><span style="font-size:0.75rem; font-weight:normal; color:#a0aec0;">AQI Categories & Seasons</span>
        </div>
        <div class="pipeline-arrow">➔</div>
        <div class="pipeline-step">
            🏢 SQLite Warehouse<br><span style="font-size:0.75rem; font-weight:normal; color:#a0aec0;">Star Schema OLAP</span>
        </div>
        <div class="pipeline-arrow">➔</div>
        <div class="pipeline-step" style="border-color:#4facfe; background:rgba(79,172,254,0.1);">
            📊 Analytics Engine<br><span style="font-size:0.75rem; font-weight:normal; color:#4facfe;">Streamlit Dashboard</span>
        </div>
    </div>
    """,
    unsafe_allow_html=True
)

st.write("## 🏛️ Pipeline Achievements by Milestone")

col1, col2 = st.columns(2)

with col1:
    st.markdown(
        """
        <div class="milestone-card">
            <div class="milestone-header">
                <span class="milestone-title">Milestone 1 — Data Ingestion & Storage</span>
                <span class="milestone-tag">Ingested</span>
            </div>
            <p class="milestone-desc">
                Established a robust, memory-safe data ingestion pipeline using <b>Apache Spark</b>. Raw dataset consists of <b>8,844,800 records</b> across 22 columns. No duplicates were detected during profiling. Structured into partitioned columnar Parquet storage (192 partitions in total, partitioned by year and month).
            </p>
            <span style="font-size:0.85rem; color:#4facfe;">🔗 Navigate to <b>Executive Overview</b> to see the ingestion KPIs.</span>
        </div>
        
        <div class="milestone-card">
            <div class="milestone-header">
                <span class="milestone-title">Milestone 2 — Star Schema Construction</span>
                <span class="milestone-tag" style="background:linear-gradient(135deg, #f857a6 0%, #ff5858 100%);">Structured</span>
            </div>
            <p class="milestone-desc">
                Constructed an optimized <b>Star Schema Relational Data Warehouse</b> in SQLite to support analytical queries. Built 3 dimension tables (<b>dim_station</b>, <b>dim_pollutant</b>, and <b>dim_time</b>) and 1 central fact table (<b>fact_measurements</b>). Indexes were constructed on foreign keys to optimize joins and aggregates.
            </p>
            <span style="font-size:0.85rem; color:#4facfe;">🔗 Navigate to <b>Warehouse Explorer</b> to inspect the relational schema.</span>
        </div>
        """,
        unsafe_allow_html=True
    )

with col2:
    st.markdown(
        """
        <div class="milestone-card">
            <div class="milestone-header">
                <span class="milestone-title">Milestone 3 — Quality & Transformations</span>
                <span class="milestone-tag" style="background:linear-gradient(135deg, #00c6ff 0%, #0072ff 100%);">Transformed</span>
            </div>
            <p class="milestone-desc">
                Implemented a batch transformation workflow to resolve quality issues:
                <ul>
                    <li>Handled missing meteorological data (imputed with medians).</li>
                    <li>Cleaned <b>at_c</b>, <b>rh_percent</b>, <b>ws_m_s</b>, <b>wd_deg</b>, and <b>tot_rf_mm</b> to 0% missing values.</li>
                    <li>Feature engineered columns: <b>season</b> and <b>aqi_category</b>.</li>
                </ul>
            </p>
            <span style="font-size:0.85rem; color:#4facfe;">🔗 Navigate to <b>Data Quality Dashboard</b> to view before/after statistics.</span>
        </div>
        
        <div class="milestone-card">
            <div class="milestone-header">
                <span class="milestone-title">Milestone 4 — Analytics Dashboard Layer</span>
                <span class="milestone-tag" style="background:linear-gradient(135deg, #ff9966 0%, #ff5e62 100%);">Visualized</span>
            </div>
            <p class="milestone-desc">
                This interactive <b>Streamlit & Plotly</b> dashboard serves as the user interface for business intelligence. It queries the star schema warehouse directly using SQL joins, demonstrating analytical query capabilities, spatial summaries, pollutant distributions, and temporal trends.
            </p>
            <span style="font-size:0.85rem; color:#4facfe;">🔗 Navigate to <b>Station, Pollutant, Trends, SQL Showcase, or Regional Analytics</b> pages.</span>
        </div>
        """,
        unsafe_allow_html=True
    )

st.write("---")

# Database Connection Status
st.subheader("🔌 Data Warehouse Connection Status")
try:
    db_path = find_db_path()
    db_size_mb = os.path.getsize(db_path) / (1024 * 1024)
    validation = validate_warehouse_tables()
    
    col_a, col_b = st.columns([3, 1])
    with col_a:
        st.success(f"Connected successfully to SQLite database: `{db_path}`")
        st.info(f"Database file size: **{db_size_mb:.2f} MB**")
    
    with col_b:
        all_exist = all(info["exists"] for info in validation.values())
        if all_exist:
            st.metric(label="Star Schema Status", value="VALID", help="All dimension and fact tables exist and are accessible.")
        else:
            st.metric(label="Star Schema Status", value="INVALID", delta="-Missing Tables", delta_color="inverse")
except Exception as e:
    st.error(f"Failed to connect to the SQLite database. Error details: {str(e)}")
