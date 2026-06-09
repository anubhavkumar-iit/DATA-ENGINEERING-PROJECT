# Architecture and Data Serving Design

## Folder Structure

```
DATA-ENGINEERING-PROJECT/
|-- DEM_Project_Milestone1/
|   |-- data/ingestion_layer/partitioned_data/ (partitioned parquet: year=/month=)
|   |-- logs/ingestion_logs.txt
|   `-- notebooks/Team5_Parquet_Ingestion_Pipeline.ipynb
|-- DEM_Project_Milestone2/
|   |-- data/database/air_quality.db
|   |-- logs/data_model_logs.txt
|   `-- notebooks/Team5_Data_Model_Milestone2.ipynb
`-- DEM_Project_Milestone3/
    |-- docs/architecture.md  literature_review.md  data_model_justification.md
    |-- notebooks/Team5_Milestone3_Batch_Transformation.ipynb
    `-- reports/before_after_quality_report.csv  performance_report.md
```

---

## Milestone 1 -- Ingestion Layer

**Source:** Delhi air quality dataset — 8,844,800 rows, 22 columns, 15 monitoring stations, 13 pollutant types, hourly readings.

**PySpark Configuration:** `spark.sql.shuffle.partitions=8`

**Pipeline Steps:**
1. Load raw parquet file into a Spark DataFrame
2. Cast datetime column to correct timestamp type
3. Extract `year` and `month` partition columns
4. Null profile — flag `vws_m_s` as structurally missing (6,546,511 nulls out of 8,844,800 rows)
5. Deduplication — 0 duplicate rows found
6. Write output partitioned by `year=/month=` to `ingestion_layer/partitioned_data/`

**Output:** Partitioned parquet files, `ingestion_logs.txt` (8,844,800 rows processed, pipeline status: SUCCESS)

---

## Milestone 2 -- Data Model

**Database:** SQLite star schema — `air_quality.db`

**Schema:**

| Table | Rows | Description |
|---|---|---|
| `dim_station` | 15 | station_id PK, station_name, city, state |
| `dim_pollutant` | 13 | pollutant_id PK AUTOINCREMENT, pollutant_name UNIQUE |
| `dim_time` | — | time_id PK, dt_str UNIQUE, year, month, day, hour |
| `fact_measurements` | 8,844,800 | FK refs to all three dims + value + 9 weather cols |

**Key Design Decision:** Normalising station metadata out of the fact table avoids repeating 15 stations' attributes across 8.8M rows, eliminates update anomalies, and enables efficient GROUP BY queries. FK constraints use `ON DELETE CASCADE`.

**Script:** `scripts/data_model.py` — reads partitioned parquet files one at a time (memory-safe) and inserts into SQLite.

---

## Milestone 3 -- Batch Transformation

**Engine:** PySpark batch processing

**Transformations Applied:**

| Transformation | Detail |
|---|---|
| Median imputation | 7 columns: `at_c`, `rh_percent`, `ws_m_s`, `wd_deg`, `rf_mm`, `tot_rf_mm`, `sr_w_mt2`, `bp_mmhg` — per-station median |
| AQI category | `Good` (≤50) / `Moderate` (≤100) / `Poor` (≤200) / `Severe` (>200) |
| Season | `Winter` / `Summer` / `Monsoon` / `Post-Monsoon` |
| Year/month extraction | From timestamp for partitioned output |

**Quality Results (before → after):**

| Column | Missing Before | Missing After |
|---|---|---|
| at_c | 2,532,923 | 0 |
| rh_percent | 1,519,086 | 0 |
| ws_m_s | 1,531,562 | 0 |
| wd_deg | 1,836,378 | 0 |
| rf_mm | 4,006,105 | 0 |
| tot_rf_mm | 801,929 | 0 |
| sr_w_mt2 | 1,610,725 | 0 |
| bp_mmhg | 3,022,601 | 0 |
| vws_m_s | 6,546,511 | 6,546,511 (structural — intentionally left) |

**Output:** Partitioned by `year` and `month`. All 7 imputed columns: 0 nulls after transformation.

---

## Data Flow Diagram

```
Raw Parquet (8,844,800 rows)
        |
        v
PySpark Ingestion (M1)
  - Cast types, extract year/month
  - Null profile, dedup
  - Partitioned write
        |
        v
Partitioned Parquet Storage
(ingestion_layer/partitioned_data/)
        |
        v
SQLite Star Schema (M2)
  - dim_station (15 rows)
  - dim_pollutant (13 rows)
  - dim_time
  - fact_measurements (8.8M rows)
        |
        v
PySpark Batch Transformation (M3)
  - Median imputation (7 cols)
  - AQI category + Season features
  - Partitioned output
        |
        v
Cleaned Parquet (0 nulls in imputed cols)
        |
        v
Analytical Queries → End Users
```

---

## Tools Used

### Apache Spark
Used for ingestion, null profiling, batch transformations, median imputation, and feature engineering across 8.8M rows.

### Parquet
Columnar storage format chosen for efficient compression, fast analytical reads, and native support for partition pruning by `year`/`month`.

### SQLite
Lightweight relational database used for the star schema data warehouse. Sufficient for 8.8M rows in a read-heavy analytics workload with only 15 stations — no distributed infrastructure needed.

### Git
Version control with per-person feature branches (`anubhav/`, `shambhavi/`, `milliam/`) merged to `main` at each milestone completion.

---

## End User Use Cases

1. Compare pollutant levels across the 15 monitoring stations.
2. Analyse monthly and seasonal air quality trends.
3. Study pollutant behaviour over time using AQI categories.
4. Generate environmental monitoring reports from cleaned data.
5. Support policy decision-making using aggregated analytics.

## Updated
Milestone 3 documentation completed 

## See Also
- [Literature Review](./literature_review.md)
- [Data Model Justification](./data_model_justification.md)
- [README](../../README.md)
