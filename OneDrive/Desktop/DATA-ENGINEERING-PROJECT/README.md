# Delhi Air Quality Data Engineering Project
### Team 5 — IIT Madras Zanzibar | Data Engineering (DEM)

---

## Project Overview

This project builds an end-to-end data engineering pipeline for the Delhi Air Quality dataset. It covers data ingestion, warehouse modelling, and batch transformation across three milestones, processing 8,844,800 hourly air quality readings from 15 monitoring stations across 13 pollutant types.

---

## Team

| Member | Branch | Responsibility |
|---|---|---|
| Anubhav | `anubhav/m3-batch-pipeline` | PySpark batch transformation pipeline |
| Shambhavi | `shambhavi/m3-reports` | Quality reports and performance evaluation |
| Milliam | `milliam/m3-docs-scaffold` | Architecture docs, literature review, README |

---

## Milestone Summary

| Milestone | Description | Key Output |
|---|---|---|
| **M1 — Ingestion** | PySpark ingestion of raw parquet data | Partitioned parquet files (`year=/month=`) |
| **M2 — Data Model** | SQLite star schema warehouse | `air_quality.db` with 4 tables, 8.8M fact rows |
| **M3 — Batch Transform** | PySpark cleaning, imputation, feature engineering | Cleaned parquet + quality report |

---

## Folder Structure

```
DATA-ENGINEERING-PROJECT/
|-- DEM_Project_Milestone1/
|   |-- data/ingestion_layer/partitioned_data/
|   |-- logs/ingestion_logs.txt
|   `-- notebooks/Team5_Parquet_Ingestion_Pipeline.ipynb
|-- DEM_Project_Milestone2/
|   |-- data/database/air_quality.db
|   |-- logs/data_model_logs.txt
|   `-- notebooks/Team5_Data_Model_Milestone2.ipynb
`-- DEM_Project_Milestone3/
    |-- docs/architecture.md
    |-- docs/literature_review.md
    |-- docs/data_model_justification.md
    |-- notebooks/Team5_Milestone3_Batch_Transformation.ipynb
    `-- reports/before_after_quality_report.csv
```

---

## How to Run

### Milestone 1 — Ingestion
1. Open `DEM_Project_Milestone1/notebooks/Team5_Parquet_Ingestion_Pipeline.ipynb` in Google Colab
2. Upload `ingestion_layer.zip` to `/content/`
3. Run all cells
4. Output: partitioned parquet files in `ingestion_layer/partitioned_data/`

### Milestone 2 — Data Model
1. Open `DEM_Project_Milestone2/notebooks/Team5_Data_Model_Milestone2.ipynb` in Google Colab
2. Upload the partitioned parquet output from M1
3. Run all cells
4. Output: `air_quality.db` (SQLite star schema)

### Milestone 3 — Batch Transformation
1. Open `DEM_Project_Milestone3/notebooks/Team5_Milestone3_Batch_Transformation.ipynb` in Google Colab
2. Upload `ingestion_layer.zip` to `/content/`
3. Run all cells
4. Output: cleaned parquet partitioned by `year`/`month`, `before_after_quality_report.csv`

---

## Dataset

- **Source:** Delhi Air Quality dataset
- **Rows:** 8,844,800
- **Stations:** 15
- **Pollutants:** 13
- **Frequency:** Hourly readings

---

## Key Results

| Metric | Value |
|---|---|
| Total rows processed | 8,844,800 |
| Duplicate rows | 0 |
| Columns imputed (median) | 7 |
| Null values remaining after cleaning | 0 (except `vws_m_s` — structural) |
| AQI categories added | Good / Moderate / Poor / Severe |
| Season feature added | Winter / Summer / Monsoon / Post-Monsoon |

---

## Documentation

- [Architecture & Data Flow](DEM_Project_Milestone3/docs/architecture.md)
- [Literature Review](DEM_Project_Milestone3/docs/literature_review.md)
- [Data Model Justification](DEM_Project_Milestone3/docs/data_model_justification.md)
