# Architecture and Data Serving Design

## System Architecture

Raw Air Quality Data
→ Spark Ingestion Pipeline
→ Partitioned Parquet Storage
→ Spark Data Profiling
→ Batch Data Cleaning
→ Feature Engineering
→ Cleaned Data Layer
→ Star Schema Data Warehouse
→ Analytical Queries
→ End Users

## Tools Used

### Apache Spark

Used for:

* Reading large parquet datasets
* Data profiling
* Batch transformations
* Cleaning operations
* Feature engineering

### Parquet

Used because:

* Columnar storage format
* Efficient compression
* Fast analytical reads
* Suitable for large datasets

### SQLite Data Warehouse

Used for:

* Structured storage
* Star schema implementation
* Analytical query execution

### Git

Used for:

* Version control
* Branch management
* Tracking milestone progress
* Collaborative development

## End User Use Cases

1. Compare pollutant levels across stations.
2. Analyze monthly air quality trends.
3. Study pollutant behavior over time.
4. Generate environmental monitoring reports.
5. Support decision-making using aggregated analytics.

## Data Serving

The cleaned and transformed dataset is stored in a warehouse-friendly structure that supports aggregation and reporting queries. Users interact with analytical views rather than raw data, improving performance and usability.


## Batch Transformation Implementation

Implemented Spark batch transformation workflow including parquet ingestion, data quality validation, missing-value imputation, and partitioned output generation for downstream analytics.

